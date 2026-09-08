"""SELECT over authorized logical tables; physical bindings and row scopes stay local."""

import uuid

import sqlglot
from sqlglot import exp
from sqlglot.dialects import Dialect
from sqlglot.optimizer.qualify import qualify
from sqlglot.optimizer.scope import traverse_scope
from sqlglot.schema import MappingSchema

from app.modules.query.compiler import CompiledQuery, reject, typed_value
from app.modules.query.models import ResultColumn, SqlPlan


def tables_for(definition, tables, grant):
    metadata = {(t.schema_name, t.name): t for t in tables}
    access = {a.model_id: set(a.columns) for a in grant.exploration} if grant else None
    result = {}
    for model in definition.models:
        if access is not None and model.id not in access:
            continue
        table = metadata[(model.relation.schema_name, model.relation.name)]
        sensitive = {
            d.column
            for d in definition.dimensions
            if d.model_id == model.id and d.sensitive
        }
        columns = [
            c
            for c in table.columns
            if c.name not in sensitive
            and (access is None or c.name in access[model.id])
        ]
        if columns:
            result[model.id] = (model, table, columns)
    return result


def catalog(definition, tables, grant):
    return [
        {
            "name": name,
            "description": model.label,
            "grain": model.grain,
            "columns": [
                {"name": c.name, "type": c.data_type, "description": c.comment}
                for c in columns
            ],
        }
        for name, (model, _, columns) in tables_for(definition, tables, grant).items()
    ]


# Positive AST allowlist: functions with side effects, table functions, commands,
# locks, INTO, hints, variables, external schemas and recursive queries are absent.
ALLOWED = set(
    "Select From Table TableAlias Column Identifier Alias Join Where And Or EQ NEQ GT GTE LT LTE In Is Not Null Boolean Group Having Order Ordered Limit Offset Literal Sum Count Avg Min Max Distinct Div Nullif Coalesce Cast DataType DataTypeParam Star Paren Add Sub Mul Mod Neg Between Like ILike Case If When Concat Lower Upper Trim Length Substring Round Abs Ceil Floor Date DateTrunc TimestampTrunc Extract Interval DateAdd DateSub DateDiff CurrentDate CurrentTimestamp TimeToStr TsOrDsToDate StrToDate Window WindowSpec RowNumber Rank DenseRank Lag Lead FirstValue LastValue CTE With Subquery Union Intersect Except Tuple Exists Filter".split()
)
TYPES = {
    "INT",
    "BIGINT",
    "SMALLINT",
    "TINYINT",
    "DECIMAL",
    "DOUBLE",
    "FLOAT",
    "REAL",
    "VARCHAR",
    "CHAR",
    "TEXT",
    "DATE",
    "TIMESTAMP",
    "TIMESTAMPTZ",
    "BOOLEAN",
    "UNKNOWN",
}
ALLOWED.add("Var")


def compile_sql(definition, tables, kind, plan: SqlPlan, grant=None):
    if kind not in ("postgresql", "mysql", "oracle"):
        reject("自由问数当前支持 PostgreSQL、MySQL、Oracle")
    available = tables_for(definition, tables, grant)
    if not available:
        reject("尚未获得表字段探索权限，请管理员在查询授权中配置")
    try:
        statements = sqlglot.parse(plan.sql, read="postgres")
        if len(statements) != 1 or not isinstance(
            statements[0], (exp.Select, exp.SetOperation)
        ):
            reject("仅允许一条只读 SELECT 查询")
        query = statements[0]
        nodes = list(query.walk())
        if len(nodes) > 1800 or any(type(n).__name__ not in ALLOWED for n in nodes):
            reject("SQL 包含未支持的表达式或非只读操作")
        if any(n.args.get("recursive") for n in query.find_all(exp.With)):
            reject("暂不支持递归查询")
        if any(n.this.value not in TYPES for n in query.find_all(exp.DataType)):
            reject("不支持该转换类型")
        if any(
            n.name.upper()
            not in {
                "YEAR",
                "QUARTER",
                "MONTH",
                "WEEK",
                "DAY",
                "HOUR",
                "MINUTE",
                "SECOND",
                "DOW",
                "DOY",
                "EPOCH",
            }
            for n in query.find_all(exp.Var)
        ):
            reject("不支持该日期单位")
        for node in nodes:
            node.comments = None
        for scope in traverse_scope(query):
            for _, source in scope.sources.items():
                if isinstance(source, exp.Table) and (
                    source.name not in available or source.db or source.catalog
                ):
                    reject("SQL 引用了授权范围外的表")
        query = qualify(
            query,
            dialect="postgres",
            schema=MappingSchema(
                {
                    name: {c.name: "UNKNOWN" for c in cols}
                    for name, (_, _, cols) in available.items()
                },
                dialect="postgres",
                normalize=False,
            ),
            infer_schema=False,
        )
        assert isinstance(query, (exp.Select, exp.SetOperation))
        projections = query.selects
        names = [p.alias_or_name for p in projections]
        if (
            not names
            or len(names) > 100
            or len(names) != len(set(names))
            or any(not n for n in names)
        ):
            reject("查询需有 1 至 100 个名称唯一的结果列")
        # Every occurrence, including CTEs, subqueries and both sides of a join,
        # is replaced with its own scoped projection before SQL is rendered.
        physical = []
        for scope in traverse_scope(query):
            physical.extend(
                s for s in scope.sources.values() if isinstance(s, exp.Table)
            )
        if not physical:
            reject("查询必须读取授权数据表")
        source_models = sorted({available[t.name][0].id for t in physical})
        for table_node in physical:
            model, table, columns = available[table_node.name]
            base = exp.select(
                *[exp.column(c.name, quoted=True) for c in columns]
            ).from_(
                exp.Table(
                    this=exp.to_identifier(table.name, quoted=True),
                    db=exp.to_identifier(table.schema_name, quoted=True),
                )
            )
            if grant and not grant.unrestricted:
                rows = [r for r in grant.rows if r.model_id == model.id]
                if not rows:
                    reject("每张探索表都必须具有行范围授权")
                for row in rows:
                    column = next(c for c in table.columns if c.name == row.column)
                    values = [exp.convert(typed_value(v, column)) for v in row.values]
                    base = base.where(exp.column(row.column, quoted=True).isin(*values))
            scoped = base.subquery(copy=False)
            scoped.set(
                "alias",
                exp.TableAlias(
                    this=exp.to_identifier(table_node.alias_or_name, quoted=True)
                ),
            )
            table_node.replace(scoped)
        # Preserve smaller requested limits; never let SQL override the API cap.
        limit = query.args.get("limit")
        if limit:
            value = limit.expression
            if (
                not isinstance(value, exp.Literal)
                or not value.is_int
                or int(value.this) < 1
            ):
                reject("行数限制必须是正整数")
            cap = min(int(value.this), plan.limit)
        else:
            cap = plan.limit
        query = query.limit(cap if cap < plan.limit else cap + 1)
        parameters = {}
        for literal in list(query.find_all(exp.Literal)):
            # Interval grammar requires a literal, rendered/escaped by SQLGlot.
            if literal.is_string and not isinstance(literal.parent, exp.Interval):
                name = f"p{len(parameters)}"
                parameters[name] = literal.this
                literal.replace(exp.Placeholder(this=name))
        dialect = {"postgresql": "postgres", "mysql": "mysql", "oracle": "oracle"}[kind]
        marker = "__ls_" + uuid.uuid4().hex + "_"
        base_generator = Dialect.get_or_raise(dialect).generator_class

        class BoundGenerator(base_generator):
            def placeholder_sql(self, expression):
                return marker + expression.name + "__"

        sql = BoundGenerator(
            dialect=dialect, unsupported_level=sqlglot.ErrorLevel.RAISE
        ).generate(query)
        if kind != "oracle":
            sql = sql.replace("%", "%%")
        for name in parameters:
            sql = sql.replace(
                marker + name + "__", f":{name}" if kind == "oracle" else f"%({name})s"
            )
        return CompiledQuery(
            sql,
            parameters,
            [ResultColumn(id=n, label=n, value_type="auto") for n in names],
            [
                "自由探索：按显示的 SQL 条件查询，未自动套用指标固定口径",
                "每张表已应用字段与行范围授权；图表和分析仅基于本次返回结果",
            ],
            source_models,
        )
    except (
        sqlglot.errors.SqlglotError,
        ValueError,
        KeyError,
        StopIteration,
        RecursionError,
    ):
        reject("SQL 的字段、关联或表达式无法通过校验，请调整查询")
