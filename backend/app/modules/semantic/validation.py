"""Deterministic structural validation against the current authorized catalog."""

import hashlib
import json
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from functools import cache
from typing import Any, Literal

from app.modules.catalog.models import CatalogState, ColumnMeta, TableMeta
from app.modules.catalog.service import visible_tables
from app.modules.datasources.models import DataSource
from app.modules.semantic.models import (
    SemanticDefinition,
    ValidationIssue,
    ValidationReport,
)


def native_kind(data_type: str) -> str:
    value = data_type.lower()
    if "timestamp" in value or "datetime" in value:
        return "datetime"
    if value == "date":
        return "date"
    if "bool" in value:
        return "boolean"
    if re.match(
        r"(smallint|bigint|tinyint|mediumint|int|integer|number|numeric|decimal|dec\b|float|double|real)",
        value,
    ):
        return "number"
    if any(t in value for t in ("char", "text", "clob", "string", "uuid")):
        return "string"
    return "unsupported"


def parse_value(value: str, column: ColumnMeta) -> Any:
    kind = native_kind(column.data_type)
    if kind == "number":
        number = Decimal(value)
        if not number.is_finite():
            raise ValueError("数字必须为有限值")
        if (
            re.match(
                r"(smallint|bigint|tinyint|mediumint|int)", column.data_type.lower()
            )
            and number != number.to_integral_value()
        ):
            raise ValueError("整数列不能使用小数")
        return number
    if kind == "date":
        return date.fromisoformat(value)
    if kind == "datetime":
        return datetime.fromisoformat(value)
    if kind == "boolean":
        if value not in ("true", "false"):
            raise ValueError("布尔值必须为 true 或 false")
        return value == "true"
    if kind == "string":
        return value
    raise ValueError("暂不支持该类型作为过滤值")


def validate(
    definition: SemanticDefinition,
    source: DataSource | None,
    state: CatalogState | None,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    def issue(
        path: str,
        code: str,
        message: str,
        severity: Literal["error", "warning"] = "error",
    ) -> None:
        issues.append(
            ValidationIssue(severity=severity, code=code, path=path, message=message)
        )

    if not source or not source.enabled:
        issue("source", "SOURCE_DISABLED", "数据源不存在或已停用")
    if (
        not state
        or not state.version
        or (source and state.source_revision != source.revision)
        or state.revision != state.synced_scope_revision
    ):
        issue("catalog", "CATALOG_NOT_READY", "请先确认数据源范围并成功同步最新元数据")
    if not definition.owner.strip():
        issue("owner", "OWNER_REQUIRED", "请填写业务口径责任人")
    if not definition.models:
        issue("models", "MODELS_REQUIRED", "至少配置一个数据模型")

    for group in (
        "models",
        "dimensions",
        "metrics",
        "filters",
        "relations",
        "entities",
    ):
        ids = [row.id for row in getattr(definition, group)]
        if len(set(ids)) != len(ids):
            issue(group, "DUPLICATE_ID", "同一分类中的稳定标识不能重复")
    logical = list(definition.dimensions) + list(definition.metrics)
    names: dict[str, str] = {}
    for item in logical:
        for name in {item.id, item.label, *item.aliases}:
            normalized = name.strip().casefold()
            if not normalized or (normalized in names and names[normalized] != item.id):
                issue(item.id, "AMBIGUOUS_ALIAS", f"名称或别名“{name}”存在歧义")
            names[normalized] = item.id
    if len({x.id for x in logical}) != len(logical):
        issue("definition", "DUPLICATE_LOGICAL_ID", "指标和维度不能使用相同标识")

    catalog = (
        {(t.schema_name, t.name, t.kind): t for t in visible_tables(state)}
        if state
        else {}
    )
    models = {m.id: m for m in definition.models}
    tables: dict[str, TableMeta] = {}
    binding: dict[str, Any] = {}
    for model in definition.models:
        ref = model.relation
        table = catalog.get((ref.schema_name, ref.name, ref.kind))
        if not table:
            issue(model.id, "TABLE_UNAVAILABLE", "模型引用的表或视图不在当前授权目录中")
            continue
        tables[model.id] = table
        pk = [c.name for c in table.columns if c.primary_key]
        if len(set(model.primary_key)) != len(model.primary_key) or set(
            model.primary_key
        ) != set(pk):
            issue(
                model.id,
                "PRIMARY_KEY_MISMATCH",
                "模型主键与当前目录不一致，请重新选择模型对象",
            )
        if not pk:
            issue(
                model.id,
                "NO_PRIMARY_KEY",
                "目录没有可验证主键，此模型不能作为多对一关联的目标",
                "warning",
            )
        if table.warnings:
            issue(
                model.id,
                "CATALOG_WARNING",
                "源库键字典信息不完整；人工关联仍须通过目标主键校验",
                "warning",
            )
        binding[model.id] = {
            "relation": ref.model_dump(),
            "primary_key": pk,
            "columns": {},
        }
        for c in table.columns:
            if c.primary_key:
                binding[model.id]["columns"][c.name] = c.model_dump(
                    exclude={"comment", "ordinal"}
                )

    def column(model_id: str, name: str | None, path: str) -> ColumnMeta | None:
        if model_id not in models:
            issue(path, "MODEL_MISSING", "引用的数据模型不存在")
            return None
        table = tables.get(model_id)
        found = (
            next((c for c in table.columns if c.name == name), None) if table else None
        )
        if not found:
            issue(path, "COLUMN_MISSING", f"引用字段“{name or '未选择'}”不可用")
        else:
            binding[model_id]["columns"][found.name] = found.model_dump(
                exclude={"comment", "ordinal"}
            )
        return found

    dimensions = {d.id: d for d in definition.dimensions}
    dimension_columns: dict[str, ColumnMeta] = {}
    for dim in definition.dimensions:
        col = column(dim.model_id, dim.column, dim.id)
        if not col:
            continue
        dimension_columns[dim.id] = col
        kind = native_kind(col.data_type)
        if kind == "unsupported" or (
            dim.value_type != "entity" and dim.value_type != kind
        ):
            issue(
                dim.id, "DIMENSION_TYPE", f"维度类型与字段类型 {col.data_type} 不一致"
            )
        if dim.value_type == "entity" and kind not in ("number", "string"):
            issue(dim.id, "ENTITY_TYPE", "实体编码必须映射到文本或数值列")
        if dim.value_type == "datetime" and dim.timezone_semantics == "date_only":
            issue(
                dim.id, "TIMEZONE_SEMANTICS", "时间戳维度需声明 UTC 或主题本地时间语义"
            )
        if dim.sensitive and dim.external_allowed:
            issue(dim.id, "SENSITIVE_EGRESS", "敏感维度不能标记为允许外发")

    graph: dict[str, list[str]] = {m: [] for m in models}
    for rel in definition.relations:
        if rel.from_model not in models or rel.to_model not in models:
            issue(rel.id, "JOIN_MODEL", "关联两端必须是已配置的数据模型")
            continue
        graph[rel.from_model].append(rel.to_model)
        if rel.cardinality not in ("many_to_one", "one_to_one"):
            issue(rel.id, "FANOUT_JOIN", "首期禁止一对多与多对多关联，避免指标重复累计")
        if (
            len(rel.from_columns) != len(rel.to_columns)
            or len(set(rel.from_columns)) != len(rel.from_columns)
            or len(set(rel.to_columns)) != len(rel.to_columns)
        ):
            issue(rel.id, "JOIN_KEYS", "关联字段必须完整一一配对，不能重复")
        for left, right in zip(rel.from_columns, rel.to_columns, strict=False):
            lc, rc = (
                column(rel.from_model, left, rel.id),
                column(rel.to_model, right, rel.id),
            )
            if (
                lc
                and rc
                and (
                    native_kind(lc.data_type) != native_kind(rc.data_type)
                    or native_kind(lc.data_type) == "unsupported"
                )
            ):
                issue(rel.id, "JOIN_TYPE", "关联两端字段类型不兼容")
        target = tables.get(rel.to_model)
        target_pk = (
            {c.name for c in target.columns if c.primary_key} if target else set()
        )
        if not target_pk or set(rel.to_columns) != target_pk:
            issue(
                rel.id,
                "JOIN_NOT_UNIQUE",
                "关联目标必须覆盖目录已确认的完整主键，包括复合主键",
            )
        if rel.cardinality == "one_to_one":
            left_table = tables.get(rel.from_model)
            left_pk = (
                {c.name for c in left_table.columns if c.primary_key}
                if left_table
                else set()
            )
            if not left_pk or set(rel.from_columns) != left_pk:
                issue(
                    rel.id, "JOIN_NOT_ONE_TO_ONE", "一对一关联的起点也必须覆盖完整主键"
                )

    @cache
    def paths(start: str, target: str) -> int:
        if has_cycle:
            return 0
        if start == target:
            return 1
        return min(2, sum(paths(n, target) for n in graph.get(start, [])))

    def cycle(node: str, stack: set[str], done: set[str]) -> bool:
        if node in stack:
            return True
        if node in done:
            return False
        stack.add(node)
        found = any(cycle(n, stack, done) for n in graph[node])
        stack.remove(node)
        done.add(node)
        return found

    done: set[str] = set()
    has_cycle = any(cycle(n, set(), done) for n in graph)
    if has_cycle:
        issue("relations", "JOIN_CYCLE", "关联不能形成环，请保留明确的单向路径")

    filters = {f.id: f for f in definition.filters}
    for filt in definition.filters:
        dim = dimensions.get(filt.dimension_id)
        col = dimension_columns.get(filt.dimension_id)
        if not dim or not col:
            issue(filt.id, "FILTER_DIMENSION", "过滤引用的维度不可用")
            continue
        null_op = filt.operator in ("is_null", "is_not_null")
        count_ok = (
            len(filt.values)
            == (0 if null_op else 2 if filt.operator == "between" else 1)
            if filt.operator != "in"
            else bool(filt.values)
        )
        if not count_ok:
            issue(filt.id, "FILTER_VALUES", "过滤值数量与操作符不匹配")
        if dim.value_type in ("string", "entity", "boolean") and filt.operator not in (
            "eq",
            "in",
            "is_null",
            "is_not_null",
        ):
            issue(
                filt.id,
                "FILTER_OPERATOR",
                "文本、实体或布尔维度只支持等于、属于或空值判断",
            )
        try:
            values = [parse_value(v, col) for v in filt.values]
            if (
                filt.operator == "between"
                and len(values) == 2
                and values[0] >= values[1]
            ):
                issue(filt.id, "FILTER_INTERVAL", "区间采用左闭右开，下界必须小于上界")
        except ValueError, InvalidOperation, TypeError:
            issue(
                filt.id,
                "FILTER_VALUE_TYPE",
                "过滤值与字段类型不匹配，日期请用 ISO 格式",
            )

    metrics = {m.id: m for m in definition.metrics}
    for metric in definition.metrics:
        if metric.model_id not in models:
            issue(metric.id, "METRIC_MODEL", "指标模型不存在")
        if metric.aggregation not in ("count", "ratio"):
            col = column(metric.model_id, metric.column, metric.id)
            if (
                col
                and metric.aggregation != "count_distinct"
                and native_kind(col.data_type) != "number"
            ):
                issue(metric.id, "AGGREGATE_TYPE", "该聚合需要数值字段")
            if col and native_kind(col.data_type) == "unsupported":
                issue(metric.id, "AGGREGATE_UNSUPPORTED", "暂不支持该字段类型的指标")
        elif metric.column:
            issue(metric.id, "UNUSED_COLUMN", "行数或比率指标不应配置字段")
        if (
            metric.aggregation in ("ratio", "avg", "count_distinct", "min", "max")
            and metric.additivity != "non_additive"
        ):
            issue(
                metric.id, "ADDITIVITY", "比率、平均、去重、最大最小值不能直接跨组累加"
            )
        if metric.additivity == "semi_additive" and not metric.non_additive_dimensions:
            issue(metric.id, "SEMI_ADDITIVE", "半可加指标必须声明禁止跨越的维度")
        if metric.additivity != "semi_additive" and metric.non_additive_dimensions:
            issue(
                metric.id, "ADDITIVITY_RESTRICTIONS", "仅半可加指标可以设置不可累加维度"
            )
        if not set(metric.non_additive_dimensions).issubset(metric.allowed_dimensions):
            issue(
                metric.id, "ADDITIVITY_DIMENSION", "不可累加维度必须属于指标的允许维度"
            )
        required_dimensions = set(metric.allowed_dimensions)
        if len(required_dimensions) != len(metric.allowed_dimensions) or len(
            set(metric.filter_ids)
        ) != len(metric.filter_ids):
            issue(metric.id, "DUPLICATE_REFERENCE", "指标引用的维度和过滤不能重复")
        if metric.time_dimension:
            td = dimensions.get(metric.time_dimension)
            if not td or td.value_type not in ("date", "datetime"):
                issue(metric.id, "TIME_DIMENSION", "时间归属必须引用日期或时间戳维度")
            required_dimensions.add(metric.time_dimension)
        else:
            issue(
                metric.id,
                "NO_TIME_DIMENSION",
                "未配置时间归属，后续不能直接回答该指标的时间范围问题",
                "warning",
            )
        for fid in metric.filter_ids:
            if fid not in filters:
                issue(metric.id, "FILTER_MISSING", f"固定过滤 {fid} 不存在")
            else:
                required_dimensions.add(filters[fid].dimension_id)
        for did in required_dimensions:
            dim = dimensions.get(did)
            if not dim:
                issue(metric.id, "DIMENSION_MISSING", f"维度 {did} 不存在")
            elif paths(metric.model_id, dim.model_id) != 1:
                issue(
                    metric.id,
                    "JOIN_PATH",
                    f"到维度 {did} 必须存在唯一的允许方向关联路径",
                )
        if metric.aggregation == "ratio":
            numerator, denominator = (
                metrics.get(metric.numerator),
                metrics.get(metric.denominator),
            )
            if (
                not numerator
                or not denominator
                or numerator.aggregation == "ratio"
                or denominator.aggregation == "ratio"
            ):
                issue(
                    metric.id,
                    "RATIO_REFERENCE",
                    "比率需引用两个非比率指标，按聚合结果相除",
                )
            elif (
                numerator.model_id != metric.model_id
                or denominator.model_id != metric.model_id
                or set(numerator.filter_ids) != set(denominator.filter_ids)
                or numerator.time_dimension != denominator.time_dimension
                or set(metric.filter_ids) != set(numerator.filter_ids)
                or metric.time_dimension != numerator.time_dimension
            ):
                issue(
                    metric.id,
                    "RATIO_GRAIN",
                    "分子、分母和比率必须使用相同模型、固定过滤及时间口径",
                )
            elif not set(metric.allowed_dimensions).issubset(
                set(numerator.allowed_dimensions) & set(denominator.allowed_dimensions)
            ):
                issue(
                    metric.id,
                    "RATIO_DIMENSIONS",
                    "比率的允许维度必须被分子和分母同时支持",
                )
        elif metric.numerator or metric.denominator:
            issue(metric.id, "UNUSED_RATIO", "非比率指标不能配置分子分母")

    dictionary: dict[tuple[str, str], str] = {}
    for entity in definition.entities:
        dim, col = (
            dimensions.get(entity.dimension_id),
            dimension_columns.get(entity.dimension_id),
        )
        if not dim or not col or dim.value_type != "entity":
            issue(entity.id, "ENTITY_DIMENSION", "实体词条必须引用可用的实体维度")
            continue
        try:
            canonical = parse_value(entity.value, col)
        except ValueError, InvalidOperation:
            issue(entity.id, "ENTITY_VALUE", "实体真实编码与字段类型不一致")
            continue
        for alias in {entity.label, *entity.aliases}:
            key = (entity.dimension_id, alias.strip().casefold())
            if key in dictionary and dictionary[key] != canonical:
                issue(
                    entity.id,
                    "ENTITY_AMBIGUOUS",
                    "同一实体维度中的名称或别名映射到不同编码",
                )
            dictionary[key] = canonical
    digest = hashlib.sha256(
        json.dumps(
            {
                "source_revision": source.revision if source else 0,
                "scope_revision": state.revision if state else 0,
                "models": binding,
            },
            sort_keys=True,
            ensure_ascii=False,
        ).encode()
    ).hexdigest()
    return ValidationReport(
        valid=not any(i.severity == "error" for i in issues),
        issues=issues,
        catalog_version=state.version if state else 0,
        binding_digest=digest,
    )
