import { isAxiosError } from "axios"
import {
  Children,
  cloneElement,
  isValidElement,
  type ReactElement,
  type ReactNode,
  useId,
} from "react"
import type { SemanticDefinition, TopicSummary } from "@/client"

export type Definition = Required<SemanticDefinition>
export type Group =
  | "models"
  | "dimensions"
  | "metrics"
  | "filters"
  | "relations"
  | "entities"
export const groups: { key: Group; label: string; hint: string }[] = [
  {
    key: "metrics",
    label: "指标",
    hint: "想计算什么？例如「销售额 = 订单金额求和」。按需定义统计口径，供团队重复使用；明细探索可以不配置指标。",
  },
  {
    key: "dimensions",
    label: "维度",
    hint: "想按什么角度分析？例如把 order_date 设为「订单日期」、region 设为「地区」，之后就能按日期或地区查看数据。",
  },
  {
    key: "models",
    label: "数据表",
    hint: "这个主题需要哪些表？从数据表目录中选择，并说明每行代表什么，例如「一笔订单」。每张表在主题内对应一个数据模型。",
  },
  {
    key: "filters",
    label: "统计条件",
    hint: "哪些记录应该参与统计？例如「只统计已支付订单」。条件需要在指标中勾选才会生效。区间包含下界、不包含上界。",
  },
  {
    key: "relations",
    label: "表间关联",
    hint: "多张表如何对应？例如订单的客户编号对应客户表的主键。关联字段按顺序配对，目标需覆盖完整主键，避免重复统计。",
  },
  {
    key: "entities",
    label: "名称与别名",
    hint: "业务叫法对应哪个编码？例如「华东区」和「华东」都对应 EAST。名称、别名与编码保留在本地配置中。",
  },
]
export const aggregations: Record<string, string> = {
  sum: "求和",
  count: "行数",
  count_distinct: "去重计数",
  avg: "平均值",
  min: "最小值",
  max: "最大值",
  ratio: "比率",
}
export const additiveLabels: Record<string, string> = {
  additive: "可累加",
  semi_additive: "部分维度可累加",
  non_additive: "不可累加",
}
export const control =
  "w-full min-w-0 rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30 disabled:opacity-50"
export function Field({
  label,
  children,
  hint,
}: {
  label: string
  children: ReactNode
  hint?: string
}) {
  const id = useId()
  const child =
    Children.count(children) === 1 && isValidElement(children)
      ? (children as ReactElement<{ id?: string; "aria-describedby"?: string }>)
      : null
  const fieldId = child?.props.id || id
  return (
    <div className="flex min-w-0 flex-col gap-2 text-sm font-medium">
      <label htmlFor={fieldId}>{label}</label>
      {child
        ? cloneElement(child, {
            id: fieldId,
            "aria-describedby":
              [child.props["aria-describedby"], hint ? `${fieldId}-hint` : ""]
                .filter(Boolean)
                .join(" ") || undefined,
          })
        : children}
      {hint && (
        <span
          id={`${fieldId}-hint`}
          className="text-xs font-normal leading-5 text-muted-foreground"
        >
          {hint}
        </span>
      )}
    </div>
  )
}
export function Status({ value }: { value: TopicSummary["availability"] }) {
  const styles = {
    ready: "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400",
    draft: "bg-muted text-muted-foreground",
    needs_review: "bg-amber-500/10 text-amber-700 dark:text-amber-400",
    disabled: "bg-muted text-muted-foreground",
  }
  return (
    <span
      className={`inline-flex whitespace-nowrap rounded-full px-2.5 py-1 text-xs ${styles[value]}`}
    >
      {
        {
          ready: "已发布",
          draft: "草稿",
          needs_review: "需重新校验",
          disabled: "已停用",
        }[value]
      }
    </span>
  )
}
export function errorMessage(error: unknown): string {
  const detail = isAxiosError(error) ? error.response?.data?.detail : undefined
  if (typeof detail === "string") return detail
  if (detail?.issues)
    return `${detail.message}：${detail.issues
      .filter((i: { severity: string }) => i.severity === "error")
      .slice(0, 3)
      .map((i: { message: string }) => i.message)
      .join("；")}`
  if (Array.isArray(detail))
    return detail
      .slice(0, 3)
      .map((i) => `${i.loc?.slice(1).join(".")}：${i.msg}`)
      .join("；")
  return "操作失败，请检查网络后重试"
}
export function normalize(value: SemanticDefinition): Definition {
  return {
    schema_version: 1,
    owner: "",
    timezone: "Asia/Shanghai",
    external_allowed: false,
    models: [],
    dimensions: [],
    metrics: [],
    filters: [],
    relations: [],
    entities: [],
    ...value,
  }
}
export function download(name: string, content: string) {
  const url = URL.createObjectURL(
    new Blob([content], { type: "text/plain;charset=utf-8" }),
  )
  const link = document.createElement("a")
  link.href = url
  link.download = name
  link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
