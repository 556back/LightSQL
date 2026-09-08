import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { AssistantService } from "@/client"
import { errorMessage } from "@/components/Semantic/shared"
import { Button } from "@/components/ui/button"

export function ResultAnalysis({
  conversationId,
  turnId,
  automatic,
}: {
  conversationId: string
  turnId: string
  automatic: boolean
}) {
  const [enabled, setEnabled] = useState(automatic)
  const analysis = useQuery({
    queryKey: ["result-analysis", conversationId, turnId],
    queryFn: async () =>
      (
        await AssistantService.analyze({
          path: { conversation_id: conversationId, turn_id: turnId },
        })
      ).data,
    enabled,
    retry: false,
    staleTime: Infinity,
    gcTime: 0,
    refetchOnWindowFocus: false,
  })
  return (
    <div className="mt-5 space-y-3 border-t pt-4">
      <Button
        variant="outline"
        size="sm"
        disabled={analysis.isFetching}
        onClick={() => {
          if (enabled) analysis.refetch()
          else setEnabled(true)
        }}
      >
        {analysis.isFetching ? "正在分析实际结果…" : "分析结果与建议"}
      </Button>
      {analysis.isError && (
        <p role="alert" className="text-sm text-destructive">
          {errorMessage(analysis.error)}
        </p>
      )}
      {analysis.data && (
        <>
          <p className="text-xs text-muted-foreground">
            {analysis.data.scope}{" "}
            {analysis.data.model && `分析模型：${analysis.data.model}`}
          </p>
          <div className="grid gap-2 sm:grid-cols-3">
            {analysis.data.facts.map((f) => (
              <div key={f.id} className="rounded-md bg-muted/40 p-3 text-xs">
                <p>{f.label}</p>
                <p className="mt-1 break-all font-mono font-medium">
                  {f.value}
                </p>
              </div>
            ))}
          </div>
          {analysis.data.findings?.map((finding, i) => (
            <div key={`${turnId}-${i}`} className="space-y-2 text-sm">
              <p>{finding.interpretation}</p>
              <p className="text-xs text-muted-foreground">
                依据：
                {finding.fact_ids
                  .map((id) => {
                    const f = analysis.data?.facts.find((f) => f.id === id)
                    return f ? `${f.label} = ${f.value}` : ""
                  })
                  .join("；")}
              </p>
              {finding.next_step && <p>建议：{finding.next_step}</p>}
            </div>
          ))}
        </>
      )}
      <p className="text-xs text-muted-foreground">
        分析会将本轮问题及返回结果的数值摘要发送到已配置模型。
      </p>
    </div>
  )
}
