import { useState } from "react"
import { Button } from "@/components/ui/button"

type Difference = {
  code: string
  row?: number
  column?: number
  side?: string
  expected_count?: number
  actual_count?: number
}

export type CaseResult = {
  case_id: string
  correct: boolean
  error_category: string
  difference?: Difference | null
}

const categories: Record<string, string> = {
  definition: "业务口径",
  retrieval: "语义检索",
  plan: "查询计划",
  dialect: "数据库方言",
  permission: "查询权限",
  performance: "执行性能",
  model: "模型服务",
  privacy: "隐私保护",
  none: "未分类",
}
const reasons: Record<string, string> = {
  truncated: "结果已截断，无法确认完整结果",
  columns: "结果列名称或顺序不一致",
  row_count: "结果行数不一致",
  row_width: "行内单元格数量与列数不一致",
  numeric_value: "数值列包含无效或非有限数值",
  ordered_rows: "结果值或行顺序不一致",
  unordered_rows: "结果值或重复行数量不一致",
  critical: "已标记关键错误，即使结果相同也不通过",
  reported_error: "运行记录已报告错误",
  action: "回答、澄清或不支持的处理方式与预期不一致",
}

function explanation(result: CaseResult) {
  const difference = result.difference
  if (!difference) return "历史记录未保存具体差异，请查阅导出证据"
  const location = difference.row
    ? ` · ${difference.side === "expected" ? "参考结果" : "实际结果"}第 ${difference.row} 行${difference.column ? `，第 ${difference.column} 列` : ""}`
    : ""
  const counts =
    difference.code === "row_count"
      ? ` · 预期 ${difference.expected_count} 行，实际 ${difference.actual_count} 行`
      : ""
  return `${reasons[difference.code] || "请查阅导出证据核对差异"}${location}${counts}`
}

export function RunDiagnostics({ cases }: { cases: CaseResult[] }) {
  const [onlyFailures, setOnlyFailures] = useState(true)
  const [page, setPage] = useState(0)
  const failures = cases.filter((result) => !result.correct)
  const filtered = onlyFailures ? failures : cases
  const currentPage = Math.min(
    page,
    Math.max(0, Math.ceil(filtered.length / 20) - 1),
  )
  const start = currentPage * 20
  return (
    <details className="mt-4 text-sm">
      <summary className="cursor-pointer">
        逐题错误分析 · 未通过 {failures.length} 题
      </summary>
      <label className="mt-4 flex items-center gap-2">
        <input
          type="checkbox"
          checked={onlyFailures}
          onChange={(event) => {
            setOnlyFailures(event.target.checked)
            setPage(0)
          }}
        />
        仅看未通过
      </label>
      <div className="mt-3 divide-y rounded-lg border px-3">
        {filtered.length === 0 && (
          <p className="py-4 text-muted-foreground">全部题目通过。</p>
        )}
        {filtered.slice(start, start + 20).map((result) => (
          <div key={result.case_id} className="space-y-1 py-3 break-words">
            <p className="font-medium">
              {result.case_id} ·{" "}
              {result.correct
                ? "通过"
                : categories[result.error_category] || result.error_category}
            </p>
            {!result.correct && (
              <p className="text-muted-foreground">{explanation(result)}</p>
            )}
          </div>
        ))}
      </div>
      {filtered.length > 0 && (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span role="status" className="mr-auto text-muted-foreground">
            第 {start + 1}–{Math.min(start + 20, filtered.length)} 题，共{" "}
            {filtered.length} 题
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={currentPage === 0}
            onClick={() => setPage(currentPage - 1)}
          >
            上一页题目
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={start + 20 >= filtered.length}
            onClick={() => setPage(currentPage + 1)}
          >
            下一页题目
          </Button>
        </div>
      )}
    </details>
  )
}
