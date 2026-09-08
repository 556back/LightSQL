import { useState } from "react"
import type { TableMeta } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { ValidatedForm } from "@/components/ui/validated-form"
import {
  additiveLabels,
  aggregations,
  control,
  type Definition,
  Field,
  type Group,
  groups,
} from "./shared"

export type Entry = Definition[Group][number]
type Row = Record<string, unknown>
type Choice = { id: string; label: string }
const defaults: Record<Group, Row> = {
  models: {
    id: "",
    label: "",
    relation: { schema_name: "", name: "", kind: "table" },
    grain: "",
    primary_key: [],
  },
  dimensions: {
    id: "",
    label: "",
    model_id: "",
    column: "",
    description: "",
    aliases: [],
    value_type: "string",
    timezone_semantics: "date_only",
    sensitive: false,
    external_allowed: false,
    value_external_allowed: false,
  },
  metrics: {
    id: "",
    label: "",
    model_id: "",
    description: "",
    aliases: [],
    aggregation: "sum",
    column: null,
    unit: "元",
    time_dimension: null,
    allowed_dimensions: [],
    filter_ids: [],
    additivity: "additive",
    non_additive_dimensions: [],
    numerator: null,
    denominator: null,
    zero_denominator: "null",
    external_allowed: false,
  },
  filters: { id: "", label: "", dimension_id: "", operator: "eq", values: [] },
  relations: {
    id: "",
    label: "",
    from_model: "",
    to_model: "",
    from_columns: [],
    to_columns: [],
    cardinality: "many_to_one",
    join_type: "left",
    description: "",
  },
  entities: { id: "", label: "", dimension_id: "", aliases: [], value: "" },
}

export function EntryEditor({
  group,
  entry,
  definition,
  tables,
  onSave,
  onClose,
}: {
  group: Group
  entry?: Entry
  definition: Definition
  tables: TableMeta[]
  onSave: (row: Entry) => void
  onClose: () => void
}) {
  const [row, setRow] = useState<Row>(() => {
    if (entry) return structuredClone(entry)
    return {
      ...structuredClone(defaults[group]),
      id: `${group}_${Array.from(crypto.getRandomValues(new Uint32Array(2)), (value) => value.toString(16).padStart(8, "0")).join("")}`,
      ...(["dimensions", "metrics"].includes(group) &&
      definition.models.length === 1
        ? { model_id: definition.models[0].id }
        : {}),
    }
  })
  const [error, setError] = useState("")
  const set = (key: string, value: unknown) =>
    setRow((r) => ({
      ...r,
      [key]: value,
      ...(key === "model_id" ? { column: null } : {}),
      ...(key === "operator" &&
      ["is_null", "is_not_null"].includes(String(value))
        ? { values: [] }
        : {}),
      ...(key === "additivity" && value !== "semi_additive"
        ? { non_additive_dimensions: [] }
        : {}),
    }))
  const str = (key: string) => String(row[key] ?? "")
  const array = (key: string) => (row[key] ?? []) as string[]
  const columns = (modelId: string): Choice[] => {
    const model = definition.models.find((m) => m.id === modelId)
    const table = tables.find(
      (t) =>
        t.schema_name === model?.relation.schema_name &&
        t.name === model?.relation.name,
    )
    return (
      table?.columns.map((c) => ({
        id: c.name,
        label: `${c.comment ? `${c.comment} · ` : ""}${c.name} · ${c.data_type}${c.primary_key ? " · 主键" : ""}`,
      })) ?? []
    )
  }
  const input = (
    key: string,
    label: string,
    required = false,
    hint?: string,
    multiline = false,
  ) => (
    <Field label={label} hint={hint}>
      {multiline ? (
        <textarea
          aria-label={label}
          className={`resize-none ${control}`}
          rows={3}
          required={required}
          value={str(key)}
          onChange={(e) => set(key, e.target.value)}
        />
      ) : (
        <input
          aria-label={label}
          className={control}
          required={required}
          value={str(key)}
          onChange={(e) => set(key, e.target.value)}
          maxLength={key === "id" ? 48 : key === "value" ? 200 : 120}
        />
      )}
    </Field>
  )
  const select = (
    key: string,
    label: string,
    choices: Choice[] | Record<string, string>,
    optional = false,
  ) => {
    const options = Array.isArray(choices)
      ? choices
      : Object.entries(choices).map(([id, label]) => ({ id, label }))
    return (
      <Field label={label}>
        <select
          aria-label={label}
          className={control}
          required={!optional}
          value={str(key)}
          onChange={(e) => set(key, e.target.value || null)}
        >
          <option value="">{optional ? "不指定" : "请选择"}</option>
          {str(key) && !options.some((c) => c.id === str(key)) && (
            <option value={str(key)}>{str(key)}（引用已失效）</option>
          )}
          {options.map((c) => (
            <option key={c.id} value={c.id}>
              {c.label}
            </option>
          ))}
        </select>
      </Field>
    )
  }
  const check = (key: string, label: string) => (
    <label className="flex items-center gap-2 text-sm">
      <input
        type="checkbox"
        checked={!!row[key]}
        onChange={(e) => set(key, e.target.checked)}
      />
      {label}
    </label>
  )
  const multi = (key: string, label: string, options: Choice[]) => (
    <fieldset className="space-y-2 rounded-lg border p-3">
      <legend className="px-1 text-sm font-medium">{label}</legend>
      <div className="grid gap-2 sm:grid-cols-2">
        {options.map((c) => (
          <label key={c.id} className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={array(key).includes(c.id)}
              onChange={(e) =>
                set(
                  key,
                  e.target.checked
                    ? [...array(key), c.id]
                    : array(key).filter((id) => id !== c.id),
                )
              }
            />
            {c.label}
          </label>
        ))}
        {array(key)
          .filter((id) => !options.some((c) => c.id === id))
          .map((id) => (
            <label key={id} className="flex gap-2 text-sm text-destructive">
              <input
                type="checkbox"
                checked
                onChange={() =>
                  set(
                    key,
                    array(key).filter((v) => v !== id),
                  )
                }
              />
              {id}（已失效）
            </label>
          ))}
      </div>
      {!options.length && !array(key).length && (
        <p className="text-xs text-muted-foreground">请先添加相应配置。</p>
      )}
    </fieldset>
  )
  const lines = (key: string, label: string, hint: string) => (
    <Field label={label} hint={hint}>
      <textarea
        aria-label={label}
        className={`resize-none ${control}`}
        rows={3}
        value={array(key).join("\n")}
        onChange={(e) => set(key, e.target.value.split("\n"))}
      />
    </Field>
  )
  const relation = row.relation as
    | { schema_name: string; name: string }
    | undefined
  const tableIndex = tables.findIndex(
    (t) => t.schema_name === relation?.schema_name && t.name === relation?.name,
  )
  const modelChoices = definition.models.map((m) => ({
    id: m.id,
    label: m.label,
  }))
  const dimensionChoices = definition.dimensions.map((d) => ({
    id: d.id,
    label: d.label,
  }))
  const metricChoices = definition.metrics
    .filter((m) => m.id !== row.id && m.aggregation !== "ratio")
    .map((m) => ({ id: m.id, label: m.label }))
  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            {entry ? "编辑" : "添加"}
            {groups.find((g) => g.key === group)?.label}
          </DialogTitle>
          <DialogDescription>
            {groups.find((g) => g.key === group)?.hint} 添加后记得保存草稿。
          </DialogDescription>
        </DialogHeader>
        <ValidatedForm
          className="space-y-5"
          onSubmit={(e) => {
            e.preventDefault()
            const cleaned = structuredClone(row)
            for (const key of ["aliases", "values"])
              if (Array.isArray(cleaned[key]))
                cleaned[key] = cleaned[key].filter(
                  (v) => typeof v === "string" && v.trim(),
                )
            if (!/^[a-z][a-z0-9_]{0,47}$/.test(str("id"))) {
              setError(
                "稳定标识需以小写字母开头，仅含小写字母、数字和下划线，最多 48 位。",
              )
              return
            }
            if (
              definition[group].some(
                (r) => r.id === row.id && r.id !== entry?.id,
              )
            ) {
              setError("该稳定标识已存在")
              return
            }
            onSave(cleaned as unknown as Entry)
          }}
        >
          {input(
            "label",
            "业务名称",
            true,
            "使用大家熟悉的名称，例如「订单」「销售额」或「地区」。",
          )}
          <details className="rounded-lg border bg-muted/25 px-3 py-2">
            <summary className="cursor-pointer text-xs text-muted-foreground">
              技术标识 · 已{entry ? "固定" : "自动生成，可按需修改"}
            </summary>
            <div className="pt-3">
              <Field
                label="稳定标识"
                hint="用于配置间引用，无需手工命名；创建后保持不变。"
              >
                <input
                  aria-label="稳定标识"
                  className={control}
                  required
                  disabled={!!entry}
                  value={str("id")}
                  maxLength={48}
                  onChange={(e) => set("id", e.target.value)}
                  placeholder="例如 net_sales"
                />
              </Field>
            </div>
          </details>
          {group === "models" && (
            <>
              <Field
                label="选择数据表"
                hint="只显示数据表目录中已选择并同步的表。"
              >
                <select
                  aria-label="目录对象"
                  required
                  className={control}
                  value={tableIndex < 0 ? "" : tableIndex}
                  onChange={(e) => {
                    if (e.target.value === "") {
                      setRow((r) => ({
                        ...r,
                        relation: { schema_name: "", name: "", kind: "table" },
                        primary_key: [],
                      }))
                      return
                    }
                    const t = tables[Number(e.target.value)]
                    if (t)
                      setRow((r) => ({
                        ...r,
                        label: r.label || (t.comment || t.name).slice(0, 120),
                        relation: {
                          schema_name: t.schema_name,
                          name: t.name,
                          kind: t.kind,
                        },
                        primary_key: t.columns
                          .filter((c) => c.primary_key)
                          .map((c) => c.name),
                      }))
                  }}
                >
                  <option value="">请选择已同步的表或视图</option>
                  {tables.map((t, i) => (
                    <option key={`${t.schema_name}.${t.name}`} value={i}>
                      {t.schema_name}.{t.name} ·{" "}
                      {t.kind === "view" ? "视图" : "表"}
                    </option>
                  ))}
                </select>
              </Field>
              {input(
                "grain",
                "每行数据代表什么",
                true,
                "例如：每行代表一个租户下的一笔订单。",
                true,
              )}
              <p className="text-xs text-muted-foreground">
                目录主键：
                {array("primary_key").join(" + ") || "未识别；无法作为关联目标"}
              </p>
            </>
          )}
          {(group === "dimensions" || group === "metrics") && (
            <>
              {select("model_id", "来自哪张数据表", modelChoices)}
              {(group === "dimensions" ||
                !["count", "ratio"].includes(str("aggregation"))) &&
                select("column", "映射字段", columns(str("model_id")))}
              {input(
                "description",
                "业务口径说明",
                group === "metrics",
                undefined,
                true,
              )}
              {lines(
                "aliases",
                "业务别名",
                "每行一个别名，最多 15 个；指标和维度之间不能重名。",
              )}
            </>
          )}
          {group === "dimensions" && (
            <>
              <div className="grid gap-4 sm:grid-cols-2">
                {select("value_type", "业务类型", {
                  string: "文本",
                  number: "数值",
                  date: "日期",
                  datetime: "日期时间",
                  boolean: "布尔",
                  entity: "实体编码",
                })}
                {select("timezone_semantics", "时间含义", {
                  date_only: "自然日期",
                  utc: "UTC 时间",
                  topic_local: "主题本地时间",
                })}
              </div>
              {check("sensitive", "敏感维度")}
              {check(
                "external_allowed",
                "允许业务名称与口径用于外部模型上下文",
              )}
              <p className="text-xs text-muted-foreground">
                维度值始终保留在本地。敏感维度不可允许外发。
              </p>
            </>
          )}
          {group === "metrics" && (
            <>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="聚合方式">
                  <select
                    aria-label="聚合方式"
                    className={control}
                    value={str("aggregation")}
                    onChange={(e) => {
                      const agg = e.target.value
                      setRow((r) => ({
                        ...r,
                        aggregation: agg,
                        additivity: ["sum", "count"].includes(agg)
                          ? "additive"
                          : "non_additive",
                        non_additive_dimensions: [],
                        column: ["count", "ratio"].includes(agg)
                          ? null
                          : r.column,
                        numerator: null,
                        denominator: null,
                      }))
                    }}
                  >
                    {Object.entries(aggregations).map(([id, label]) => (
                      <option key={id} value={id}>
                        {label}
                      </option>
                    ))}
                  </select>
                </Field>
                {input("unit", "业务单位", true)}
              </div>
              {str("aggregation") === "ratio" && (
                <div className="grid gap-4 sm:grid-cols-2">
                  {select("numerator", "分子指标", metricChoices)}
                  {select("denominator", "分母指标", metricChoices)}
                </div>
              )}
              {select(
                "time_dimension",
                "默认时间维度",
                definition.dimensions
                  .filter((d) => ["date", "datetime"].includes(d.value_type))
                  .map((d) => ({ id: d.id, label: d.label })),
                true,
              )}
              {multi("allowed_dimensions", "允许分析的维度", dimensionChoices)}
              {multi(
                "filter_ids",
                "固定口径过滤",
                definition.filters.map((f) => ({ id: f.id, label: f.label })),
              )}
              {select("additivity", "可累加规则", additiveLabels)}
              {str("additivity") === "semi_additive" &&
                multi(
                  "non_additive_dimensions",
                  "不可跨越累加的维度",
                  dimensionChoices.filter((d) =>
                    array("allowed_dimensions").includes(d.id),
                  ),
                )}
              {check(
                "external_allowed",
                "允许业务名称与口径用于外部模型上下文",
              )}
            </>
          )}
          {group === "filters" && (
            <>
              {select("dimension_id", "过滤维度", dimensionChoices)}
              {select("operator", "比较方式", {
                eq: "等于",
                in: "属于集合",
                gt: "大于",
                gte: "大于等于",
                lt: "小于",
                lte: "小于等于",
                between: "区间 [下界, 上界)",
                is_null: "为空",
                is_not_null: "非空",
              })}
              {!["is_null", "is_not_null"].includes(str("operator")) &&
                lines(
                  "values",
                  "过滤值",
                  "每行一个值；日期使用 YYYY-MM-DD，布尔值使用 true / false，区间填两行。",
                )}
            </>
          )}
          {group === "relations" && (
            <>
              <div className="grid gap-4 sm:grid-cols-2">
                {select("from_model", "起点模型（事实侧）", modelChoices)}
                {select("to_model", "目标模型（唯一侧）", modelChoices)}
              </div>
              <fieldset className="space-y-3 rounded-lg border p-3">
                <legend className="px-1 text-sm">关联字段配对</legend>
                {Array.from(
                  {
                    length: Math.max(
                      array("from_columns").length,
                      array("to_columns").length,
                      1,
                    ),
                  },
                  (_, index) => (
                    <div
                      className="flex items-center gap-2"
                      key={`pair-${index}-${Math.max(array("from_columns").length, 1)}`}
                    >
                      {["from_columns", "to_columns"].map((key, side) => (
                        <select
                          key={key}
                          className={control}
                          aria-label={`${side ? "目标" : "起点"}字段 ${index + 1}`}
                          required
                          value={array(key)[index] ?? ""}
                          onChange={(e) => {
                            const values = [...array(key)]
                            values[index] = e.target.value
                            set(key, values)
                          }}
                        >
                          <option value="">
                            {side ? "目标主键" : "起点字段"}
                          </option>
                          {columns(str(side ? "to_model" : "from_model")).map(
                            (c) => (
                              <option key={c.id} value={c.id}>
                                {c.label}
                              </option>
                            ),
                          )}
                        </select>
                      ))}
                      <Button
                        type="button"
                        variant="ghost"
                        aria-label={`删除配对 ${index + 1}`}
                        onClick={() =>
                          setRow((r) => ({
                            ...r,
                            from_columns: array("from_columns").filter(
                              (_, i) => i !== index,
                            ),
                            to_columns: array("to_columns").filter(
                              (_, i) => i !== index,
                            ),
                          }))
                        }
                      >
                        ×
                      </Button>
                    </div>
                  ),
                )}
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() =>
                    setRow((r) => ({
                      ...r,
                      from_columns: [...array("from_columns"), ""],
                      to_columns: [...array("to_columns"), ""],
                    }))
                  }
                >
                  添加字段配对
                </Button>
              </fieldset>
              <div className="grid gap-4 sm:grid-cols-2">
                {select("cardinality", "关联基数", {
                  many_to_one: "多对一",
                  one_to_one: "一对一",
                  one_to_many: "一对多（禁止发布）",
                  many_to_many: "多对多（禁止发布）",
                })}
                {select("join_type", "连接方式", {
                  left: "左连接 · 保留起点记录",
                  inner: "内连接 · 仅匹配记录",
                })}
              </div>
              {input(
                "description",
                "关联业务说明",
                true,
                "说明字段语义与连接方式的业务影响。",
                true,
              )}
            </>
          )}
          {group === "entities" && (
            <>
              {select(
                "dimension_id",
                "实体维度",
                definition.dimensions
                  .filter((d) => d.value_type === "entity")
                  .map((d) => ({ id: d.id, label: d.label })),
              )}
              {input("value", "真实编码", true)}
              {lines(
                "aliases",
                "实体别名",
                "每行一个别名；同一维度的别名只能映射到一个真实编码。",
              )}
            </>
          )}
          {error && (
            <p role="alert" className="text-sm text-destructive">
              {error}
            </p>
          )}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              取消
            </Button>
            <Button type="submit">应用到工作区</Button>
          </DialogFooter>
        </ValidatedForm>
      </DialogContent>
    </Dialog>
  )
}
