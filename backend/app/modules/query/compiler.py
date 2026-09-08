"""Construct an allowlisted AST from a validated release, never parse caller SQL."""

import hashlib
import json
import uuid
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, NoReturn
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlglot import exp
from sqlglot.dialects import Dialect

from app.modules.catalog.models import ColumnMeta, TableMeta
from app.modules.query.models import QueryGrant, QueryPlan, ResultColumn
from app.modules.semantic.models import SemanticDefinition
from app.modules.semantic.validation import native_kind, parse_value


def fingerprint(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        ).encode()
    ).hexdigest()


def reject(message: str) -> NoReturn:
    raise HTTPException(422, message)


def typed_value(
    value: str,
    column: ColumnMeta,
    *,
    semantics: str = "date_only",
    timezone: str = "UTC",
) -> Any:
    try:
        result = parse_value(value, column)
        if isinstance(result, Decimal) and (
            len(result.as_tuple().digits) > 38 or abs(result.adjusted()) > 38
        ):
            reject("数字超出支持的精度范围")
        if isinstance(result, datetime):
            if result.tzinfo is None:
                reject("时间戳过滤必须包含时区偏移，例如 2026-09-01T00:00:00+08:00")
            target = UTC if semantics == "utc" else ZoneInfo(timezone)
            result = result.astimezone(target)
            if (
                "with time zone" not in column.data_type.lower()
                and "timestamptz" not in column.data_type.lower()
            ):
                result = result.replace(tzinfo=None)
        return result
    except ValueError, InvalidOperation, OverflowError:
        reject("过滤值与字段类型不匹配，请检查数字、ISO 日期或带时区的时间戳")


@dataclass
class CompiledQuery:
    sql: str
    parameters: Any
    columns: list[ResultColumn]
    notes: list[str]
    source_models: list[str] = dataclass_field(default_factory=list)


def compile_plan(
    definition: SemanticDefinition,
    tables: list[TableMeta],
    kind: str,
    plan: QueryPlan,
    grant: QueryGrant | None = None,
) -> CompiledQuery:
    models = {m.id: m for m in definition.models}
    dimensions = {d.id: d for d in definition.dimensions}
    metrics = {m.id: m for m in definition.metrics}
    filters = {f.id: f for f in definition.filters}
    metadata = {(t.schema_name, t.name): t for t in tables}
    columns = {
        mid: {
            c.name: c
            for c in metadata[(m.relation.schema_name, m.relation.name)].columns
        }
        for mid, m in models.items()
    }
    dim_ids = [d.dimension_id for d in plan.dimensions]
    if len(set(plan.metrics)) != len(plan.metrics) or len(set(dim_ids)) != len(dim_ids):
        reject("指标和分组维度不能重复")
    if any(m not in metrics for m in plan.metrics) or any(
        d not in dimensions for d in [*dim_ids, *(f.dimension_id for f in plan.filters)]
    ):
        reject("计划引用了不存在的指标或维度")
    chosen = [metrics[m] for m in plan.metrics]
    root = chosen[0].model_id
    if any(
        (m.model_id, set(m.filter_ids), m.time_dimension)
        != (root, set(chosen[0].filter_ids), chosen[0].time_dimension)
        for m in chosen
    ):
        reject("一次查询的指标必须来自同一模型，并使用相同固定过滤和时间口径")
    used_dims = set(dim_ids) | {f.dimension_id for f in plan.filters}
    for metric in chosen:
        if not used_dims <= set(metric.allowed_dimensions):
            reject("所选维度不在每个指标的允许分析范围内")
        if metric.additivity == "semi_additive" and any(
            d not in dim_ids
            or next(g for g in plan.dimensions if g.dimension_id == d).grain != "value"
            for d in metric.non_additive_dimensions
        ):
            reject("半可加指标必须按其不可累加维度的原始值分组")
    if plan.time_range:
        if not chosen[0].time_dimension:
            reject("该指标尚未定义时间维度")
        used_dims.add(chosen[0].time_dimension)
    if grant:
        if not set(plan.metrics) <= set(grant.metric_ids) or not used_dims <= set(
            grant.dimension_ids
        ):
            raise HTTPException(403, "查询超出已授权的指标或维度")
        if not grant.unrestricted and not any(r.model_id == root for r in grant.rows):
            raise HTTPException(403, "该指标的基础模型尚未配置行级授权")
    required_dims = used_dims | {filters[f].dimension_id for f in chosen[0].filter_ids}
    required_models = {root}
    ordered_relations = []

    def visit(target: str, current: str, path: list) -> list[list]:
        if current == target:
            return [path]
        if len(path) >= len(models):
            return []
        return [
            p
            for rel in definition.relations
            if rel.from_model == current
            for p in visit(target, rel.to_model, [*path, rel])
        ]

    for did in sorted(required_dims):
        paths = visit(dimensions[did].model_id, root, [])
        if len(paths) != 1:
            reject("指标到维度没有唯一的有向关联路径")
        for rel in paths[0]:
            if rel.id not in {r.id for r in ordered_relations}:
                ordered_relations.append(rel)
            required_models.add(rel.to_model)
    aliases = {mid: f"m{i}" for i, mid in enumerate(sorted(required_models))}
    parameters: dict[str, Any] = {}

    def bind(value: Any) -> exp.Placeholder:
        name = f"p{len(parameters)}"
        parameters[name] = value
        return exp.Placeholder(this=name)

    def col(mid: str, name: str) -> exp.Column:
        if name not in columns[mid]:
            reject("字段已不在当前授权目录中")
        return exp.column(name, table=aliases[mid], quoted=True)

    def dimcol(did: str) -> exp.Column:
        d = dimensions[did]
        return col(d.model_id, d.column)

    def predicate(
        expression: exp.Expression,
        operator: str,
        values: list[str],
        meta: ColumnMeta,
        semantics: str = "date_only",
    ) -> exp.Expression:
        if operator in ("is_null", "is_not_null"):
            if values:
                reject("空值判断不能携带过滤值")
            check = exp.Is(this=expression, expression=exp.Null())
            return exp.Not(this=check) if operator == "is_not_null" else check
        expected = 2 if operator == "between" else 1
        if (operator == "in" and not values) or (
            operator != "in" and len(values) != expected
        ):
            reject("过滤值数量与操作符不匹配")
        if native_kind(meta.data_type) in ("string", "boolean") and operator not in (
            "eq",
            "in",
        ):
            reject("文本和布尔字段只支持等值、集合与空值过滤")
        parsed = [
            typed_value(v, meta, semantics=semantics, timezone=definition.timezone)
            for v in values
        ]
        if kind in ("oracle", "dameng") and any(v == "" for v in parsed):
            reject("此数据库无法区分空字符串与 NULL，请使用空值判断")
        args = [bind(v) for v in parsed]
        if operator == "in":
            return exp.In(this=expression, expressions=args)
        if operator == "between":
            if parsed[0] >= parsed[1]:
                reject("区间起点必须早于终点（左闭右开）")
            return exp.and_(
                exp.GTE(this=expression.copy(), expression=args[0]),
                exp.LT(this=expression, expression=args[1]),
            )
        cls = {
            "eq": exp.EQ,
            "gt": exp.GT,
            "gte": exp.GTE,
            "lt": exp.LT,
            "lte": exp.LTE,
        }[operator]
        return cls(this=expression, expression=args[0])

    def relation(mid: str) -> exp.Subquery:
        model = models[mid]
        physical = exp.table_(
            model.relation.name, db=model.relation.schema_name, quoted=True
        )
        # Project explicit catalog columns. Row authorization is applied BEFORE joins.
        base = exp.select(*(exp.column(c, quoted=True) for c in columns[mid])).from_(
            physical
        )
        if grant:
            for row in grant.rows:
                if row.model_id == mid:
                    if row.column not in columns[mid]:
                        reject("行级授权字段已经失效")
                    base = base.where(
                        predicate(
                            exp.column(row.column, quoted=True),
                            "in",
                            row.values,
                            columns[mid][row.column],
                        )
                    )
        return base.subquery(exp.to_identifier(aliases[mid], quoted=True))

    def aggregate(mid: str) -> exp.Expression:
        m = metrics[mid]
        if m.aggregation == "ratio":
            assert m.numerator is not None and m.denominator is not None
            numerator = exp.Cast(
                this=aggregate(m.numerator), to=exp.DataType.build("DECIMAL(38, 10)")
            )
            return exp.Div(
                this=numerator,
                expression=exp.Nullif(
                    this=aggregate(m.denominator), expression=exp.Literal.number(0)
                ),
                typed=True,
            )
        value = col(m.model_id, m.column) if m.column else exp.Star()
        if m.aggregation == "count_distinct":
            return exp.Count(this=exp.Distinct(expressions=[value]))
        return {
            "sum": exp.Sum,
            "count": exp.Count,
            "avg": exp.Avg,
            "min": exp.Min,
            "max": exp.Max,
        }[m.aggregation](this=value)

    projections, grouping, result_columns = [], [], []
    for group in plan.dimensions:
        d = dimensions[group.dimension_id]
        expression = dimcol(d.id)
        if group.grain != "value":
            if d.value_type != "date":
                reject("日/月/年分组目前仅支持业务日期字段；时间戳请使用时间区间过滤")
            fmt = {"day": "%Y-%m-%d", "month": "%Y-%m", "year": "%Y"}[group.grain]
            expression = exp.TimeToStr(this=expression, format=exp.Literal.string(fmt))
        grouping.append(expression.copy())
        projections.append(exp.alias_(expression, d.id, quoted=True))
        result_columns.append(
            ResultColumn(
                id=d.id,
                label=d.label,
                value_type=d.value_type,
                timezone=(
                    "UTC" if d.timezone_semantics == "utc" else definition.timezone
                )
                if d.value_type == "datetime"
                else "",
            )
        )
    for m in chosen:
        projections.append(exp.alias_(aggregate(m.id), m.id, quoted=True))
        result_columns.append(
            ResultColumn(id=m.id, label=m.label, value_type="number", unit=m.unit)
        )
    query = exp.select(*projections).from_(relation(root))
    for rel in ordered_relations:
        on = exp.and_(
            *(
                exp.EQ(this=col(rel.from_model, a), expression=col(rel.to_model, b))
                for a, b in zip(rel.from_columns, rel.to_columns, strict=True)
            )
        )
        query = query.join(relation(rel.to_model), on=on, join_type=rel.join_type)
    for f in [*(filters[fid] for fid in chosen[0].filter_ids), *plan.filters]:
        d = dimensions[f.dimension_id]
        query = query.where(
            predicate(
                dimcol(d.id),
                f.operator,
                f.values,
                columns[d.model_id][d.column],
                d.timezone_semantics,
            )
        )
    if plan.time_range:
        assert chosen[0].time_dimension is not None
        d = dimensions[chosen[0].time_dimension]
        query = query.where(
            predicate(
                dimcol(d.id),
                "between",
                [plan.time_range.start, plan.time_range.end],
                columns[d.model_id][d.column],
                d.timezone_semantics,
            )
        )
    if grouping:
        query = query.group_by(*grouping)
    selected_ids = set(plan.metrics) | set(dim_ids)
    order_fields = [o.field for o in plan.order_by]
    if (
        len(set(order_fields)) != len(order_fields)
        or not set(order_fields) <= selected_ids
    ):
        reject("排序字段必须是结果中的唯一指标或维度")
    orders = [(o.field, o.direction == "desc") for o in plan.order_by]
    orders.extend((d, False) for d in dim_ids if d not in order_fields)
    for field, desc in orders:
        # Explicit NULL-last yields the same ordering across dialects.
        c = exp.column(field, quoted=True)
        query = query.order_by(exp.Ordered(this=c, desc=desc, nulls_first=False))
    query = query.limit(plan.limit + 1)
    allowed = {
        exp.Select,
        exp.From,
        exp.Subquery,
        exp.Table,
        exp.TableAlias,
        exp.Column,
        exp.Identifier,
        exp.Alias,
        exp.Join,
        exp.Where,
        exp.And,
        exp.EQ,
        exp.GT,
        exp.GTE,
        exp.LT,
        exp.LTE,
        exp.In,
        exp.Is,
        exp.Not,
        exp.Null,
        exp.Placeholder,
        exp.Group,
        exp.Order,
        exp.Ordered,
        exp.Limit,
        exp.Literal,
        exp.Sum,
        exp.Count,
        exp.Avg,
        exp.Min,
        exp.Max,
        exp.Distinct,
        exp.Div,
        exp.Nullif,
        exp.Cast,
        exp.DataType,
        exp.DataTypeParam,
        exp.Star,
        exp.TimeToStr,
        exp.Paren,
    }
    if any(type(node) not in allowed for node in query.walk()):
        reject("查询包含当前编译器未支持的表达式")
    dialect = {
        "postgresql": "postgres",
        "kingbase": "postgres",
        "mysql": "mysql",
        "oracle": "oracle",
        "dameng": "oracle",
    }[kind]
    base_generator = Dialect.get_or_raise(dialect).generator_class
    order: list[str] = []
    marker = f"__lightsql_bind_{uuid.uuid4().hex}_"
    while marker in json.dumps(definition.model_dump(mode="json")):
        marker = f"__lightsql_bind_{uuid.uuid4().hex}_"

    class BoundGenerator(base_generator):
        def placeholder_sql(self, expression: exp.Placeholder) -> str:
            name = expression.name
            order.append(name)
            return f"{marker}{name}__"

    sql = BoundGenerator(dialect=dialect).generate(query)
    # Escape percent signs only AFTER date-format transpilation. Escaping in
    # literal_sql corrupts SQLGlot's intermediate %Y -> YYYY transformation.
    if kind in ("mysql", "postgresql", "kingbase"):
        sql = sql.replace("%", "%%")
    for name in set(order):
        placeholder = (
            "?"
            if kind == "dameng"
            else f":{name}"
            if kind == "oracle"
            else f"%({name})s"
        )
        sql = sql.replace(f"{marker}{name}__", placeholder)
    bound = tuple(parameters[n] for n in order) if kind == "dameng" else parameters
    notes = [
        "固定业务过滤与行级权限已在服务端绑定",
        "金额与大整数以十进制文本返回，空值保留为 NULL",
        "未执行成本估算；结果受行数、字节数及执行时间限制",
    ]
    if any(m.additivity != "additive" for m in chosen):
        notes.append("包含不可直接跨组相加的指标；总计应单独查询")
    return CompiledQuery(sql, bound, result_columns, notes, sorted(required_models))
