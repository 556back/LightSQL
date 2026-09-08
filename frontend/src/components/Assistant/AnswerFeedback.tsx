import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import {
  AssistantService,
  type FeedbackInput,
  type FeedbackPublic,
} from "@/client"
import { control, errorMessage } from "@/components/Semantic/shared"
import { Button } from "@/components/ui/button"
import { ValidatedForm } from "@/components/ui/validated-form"

export function AnswerFeedback({
  conversationId,
  turnId,
  saved,
}: {
  conversationId: string
  turnId: string
  saved?: FeedbackPublic | null
}) {
  const qc = useQueryClient()
  const [editing, setEditing] = useState(false)
  const [rating, setRating] = useState<FeedbackInput["rating"]>(
    saved?.rating || "helpful",
  )
  const [category, setCategory] = useState<FeedbackInput["category"]>(
    saved?.category || "metric",
  )
  const [comment, setComment] = useState(saved?.comment || "")
  const mutation = useMutation({
    mutationFn: () =>
      AssistantService.saveFeedback({
        path: { conversation_id: conversationId, turn_id: turnId },
        body: {
          rating,
          category: rating === "helpful" ? "none" : category,
          comment,
        },
      }),
    onSuccess: () => {
      setEditing(false)
      qc.invalidateQueries({ queryKey: ["conversation", conversationId] })
      qc.invalidateQueries({ queryKey: ["conversations"] })
    },
  })
  return (
    <div className="border-t pt-4 text-sm">
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-muted-foreground">
          {saved
            ? `已记录：${saved.rating === "helpful" ? "有帮助" : "结果有问题"}`
            : "这次回答是否有帮助？"}
        </span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            setRating(saved?.rating || "helpful")
            setCategory(
              saved?.category === "none"
                ? "metric"
                : saved?.category || "metric",
            )
            setComment(saved?.comment || "")
            setEditing(!editing)
          }}
        >
          {saved ? "修改反馈" : "评价回答"}
        </Button>
      </div>
      {editing && (
        <ValidatedForm
          className="mt-3 space-y-3"
          onSubmit={(event) => {
            event.preventDefault()
            mutation.mutate()
          }}
        >
          <label className="block">
            评价
            <select
              aria-label="评价"
              className={control}
              value={rating}
              onChange={(e) => setRating(e.target.value as typeof rating)}
            >
              <option value="helpful">有帮助</option>
              <option value="incorrect">结果有问题</option>
            </select>
          </label>
          {rating === "incorrect" && (
            <label className="block">
              问题分类
              <select
                aria-label="问题分类"
                className={control}
                value={category}
                onChange={(e) => setCategory(e.target.value as typeof category)}
              >
                <option value="metric">指标口径</option>
                <option value="filter">筛选范围</option>
                <option value="data">数据或结果</option>
                <option value="chart">图表展示</option>
                <option value="other">其他</option>
              </select>
            </label>
          )}
          <label className="block">
            补充说明
            <textarea
              aria-label="反馈说明"
              className={`resize-none ${`${control} min-h-20`}`}
              maxLength={1000}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="可填写预期结果、正确口径或复现条件"
            />
          </label>
          <p className="text-xs text-muted-foreground">
            反馈与问题将加密保存到管理员审核队列，保留 90
            天；不会自动修改指标口径。
          </p>
          <Button size="sm" disabled={mutation.isPending}>
            保存反馈
          </Button>
        </ValidatedForm>
      )}
      {mutation.isError && (
        <p role="alert" className="mt-2 text-destructive">
          {errorMessage(mutation.error)}
        </p>
      )}
    </div>
  )
}
