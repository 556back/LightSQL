import { useQuery } from "@tanstack/react-query"
import { AssistantService } from "@/client"
import { errorMessage } from "@/components/Semantic/shared"

export function AnswerEvidence({
  conversationId,
  turnId,
}: {
  conversationId: string
  turnId: string
}) {
  const evidence = useQuery({
    queryKey: ["answer-evidence", conversationId, turnId],
    queryFn: async () =>
      (
        await AssistantService.answerEvidence({
          path: { conversation_id: conversationId, turn_id: turnId },
        })
      ).data,
    retry: false,
    gcTime: 0,
    refetchInterval: 5000,
  })
  const data = evidence.data
  return (
    <details className="rounded-lg border p-4 text-sm">
      <summary className="cursor-pointer font-medium">核对口径与来源</summary>
      {evidence.isError ? (
        <p role="alert" className="mt-3 text-destructive">
          {errorMessage(evidence.error)}
        </p>
      ) : data ? (
        <div className="mt-4 space-y-3 leading-6">
          <p>
            {data.topic} · 语义 v{data.semantic_version} · 元数据 v
            {data.catalog_version}
          </p>
          <p className="text-muted-foreground">
            责任人：{data.owner || "未填写"} · 时区：{data.timezone} ·{" "}
            {data.database_type}
          </p>
          <p>口径发布：{new Date(data.published_at).toLocaleString()}</p>
          <p className="break-words">
            来源：{data.sources.join("；") || "未识别到来源表"}
          </p>
          {data.metrics.map((metric) => (
            <p key={metric}>{metric}</p>
          ))}
          <p>
            固定过滤：
            {data.fixed_filters.join("；") ||
              (data.metrics.length
                ? "无"
                : "自由探索使用 SQL 内的条件，未自动套用指标口径")}
          </p>
          <p>{data.policy}</p>
          {data.query_id && (
            <p className="break-all text-xs text-muted-foreground">
              查询编号：{data.query_id}
              <br />
              完成时间：
              {data.queried_at
                ? new Date(data.queried_at).toLocaleString()
                : "尚未完成"}
            </p>
          )}
          {data.notes.map((note) => (
            <p key={note} className="text-xs text-muted-foreground">
              {note}
            </p>
          ))}
        </div>
      ) : (
        <p className="mt-3">正在读取来源…</p>
      )}
    </details>
  )
}
