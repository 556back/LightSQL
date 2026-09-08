import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Link, useNavigate, useSearch } from "@tanstack/react-router"
import { MessageSquare, Plus, Send, ShieldCheck } from "lucide-react"
import { useState } from "react"
import {
  AssistantService,
  type ConversationPublic,
  QueriesService,
  TopicsService,
  type TurnPublic,
} from "@/client"
import { ResultPanel } from "@/components/Queries/QueryPage"
import { control, errorMessage, Field } from "@/components/Semantic/shared"
import { Button } from "@/components/ui/button"
import useAuth from "@/hooks/useAuth"
import { AnswerEvidence } from "./AnswerEvidence"
import { AnswerFeedback } from "./AnswerFeedback"
import { useConversationStream } from "./useConversationStream"

const statuses: Record<string, string> = {
  planning: "正在规划",
  ready: "待核对计划",
  submitted: "已提交查询",
  clarification: "需要澄清",
  unsupported: "暂不支持",
  failed: "未生成计划",
  expired: "已过期",
}

export function AskPage() {
  const { user } = useAuth()
  const search = useSearch({ from: "/_layout/ask" })
  const navigate = useNavigate()
  const topicId = search.topic || ""
  const conversationId = search.conversation || ""
  const [historySearch, setHistorySearch] = useState("")
  const selectConversation = (id: string, topic = selected) =>
    void navigate({
      to: "/ask",
      search: { topic, conversation: id || undefined },
    })
  const qc = useQueryClient()
  const topics = useQuery({
    queryKey: ["ask-topics", user?.id],
    queryFn: async () => (await TopicsService.listTopics()).data,
  })
  const model = useQuery({
    queryKey: ["model-status"],
    queryFn: async () => (await AssistantService.modelStatus()).data,
    refetchInterval: 5000,
  })
  const history = useQuery({
    queryKey: ["conversations", user?.id],
    queryFn: async () => (await AssistantService.listConversations()).data,
    retry: false,
  })
  const selected =
    topicId || topics.data?.find((t) => t.availability === "ready")?.id || ""
  const create = useMutation({
    mutationFn: async () =>
      (
        await AssistantService.createConversation({
          body: { topic_id: selected },
        })
      ).data,
    onSuccess: (data) => {
      selectConversation(data.id)
      qc.invalidateQueries({ queryKey: ["conversations"] })
    },
  })
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs tracking-widest text-muted-foreground">
            探索与分析
          </p>
          <h1 className="mt-2 text-2xl font-semibold">智能问数</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            用自然语言查明细、做统计、看趋势，自动生成
            SQL、图表与分析。指标口径按需使用。
          </p>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-3 rounded-xl border bg-card p-4 text-sm">
        <ShieldCheck className="size-4 text-emerald-600" />
        <span>
          当前模型：{String(model.data?.name || "正在读取配置…")}
          {model.data?.configured ? ` · ${model.data.model}` : ""}
        </span>
        {user?.is_superuser && (
          <Link
            className="ml-auto text-primary underline underline-offset-4"
            to="/models"
          >
            模型设置
          </Link>
        )}
      </div>
      {!model.data?.configured && !model.isPending && (
        <p className="rounded-lg bg-amber-500/10 p-4 text-sm">
          管理员添加并启用模型配置后，即可生成问答计划。可先选择主题查看可用指标。
        </p>
      )}
      <div className="flex flex-wrap items-end gap-3 rounded-xl border bg-card p-5">
        <div className="min-w-0 flex-1">
          <Field label="数据范围 / 业务主题">
            <select
              aria-label="业务主题"
              className={control}
              value={selected}
              onChange={(e) => {
                selectConversation("", e.target.value)
              }}
            >
              <option value="">选择已发布主题</option>
              {topics.data
                ?.filter((t) => t.availability === "ready")
                .map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name} · v{t.current_version}
                  </option>
                ))}
            </select>
          </Field>
        </div>
        <Button
          disabled={!selected || create.isPending}
          onClick={() => create.mutate()}
        >
          <Plus className="size-4" />
          新建会话
        </Button>
      </div>
      {(topics.isError || create.isError || model.isError) && (
        <p role="alert" className="text-destructive">
          {errorMessage(topics.error || create.error || model.error)}
        </p>
      )}
      <div className="grid min-w-0 gap-6 xl:grid-cols-[220px_minmax(0,1fr)]">
        <aside className="max-h-72 space-y-3 overflow-y-auto rounded-xl border bg-card p-4 xl:max-h-[680px]">
          <h2 className="text-sm font-medium">最近会话</h2>
          <p className="text-xs text-muted-foreground">
            问题与计划保留 24 小时
          </p>
          <input
            aria-label="搜索历史会话"
            className={control}
            value={historySearch}
            onChange={(e) => setHistorySearch(e.target.value)}
            placeholder="搜索问题或反馈"
          />
          {history.isError && (
            <p role="alert" className="text-sm text-destructive">
              {errorMessage(history.error)}
            </p>
          )}
          {history.data
            ?.filter((c) => c.topic_id === selected)
            .filter(
              (c) =>
                !historySearch.trim() ||
                c.turns.some((t) =>
                  `${t.question} ${t.feedback?.comment || ""}`
                    .toLowerCase()
                    .includes(historySearch.trim().toLowerCase()),
                ),
            )
            .map((c) => (
              <button
                type="button"
                key={c.id}
                onClick={() => selectConversation(c.id)}
                className={`w-full rounded-lg border p-3 text-left text-sm ${c.id === conversationId ? "border-primary/50 bg-primary/5" : "bg-card"}`}
              >
                <p className="line-clamp-2 break-words">
                  {c.turns[0]?.question || "新会话"}
                </p>
                <p className="mt-2 text-xs text-muted-foreground">
                  {c.turns.length} 轮 ·{" "}
                  {new Date(c.created_at).toLocaleString()}
                  {c.turns.some((t) => t.feedback) && " · 已反馈"}
                </p>
              </button>
            ))}
          {!history.isPending &&
            !history.isError &&
            !history.data?.some(
              (c) =>
                c.topic_id === selected &&
                (!historySearch.trim() ||
                  c.turns.some((t) =>
                    `${t.question} ${t.feedback?.comment || ""}`
                      .toLowerCase()
                      .includes(historySearch.trim().toLowerCase()),
                  )),
            ) && (
              <p className="text-xs text-muted-foreground">
                没有匹配的有效会话
              </p>
            )}
          <Button variant="ghost" size="sm" onClick={() => history.refetch()}>
            刷新会话
          </Button>
        </aside>
        <div className="min-w-0">
          {conversationId ? (
            <ConversationPanel
              key={`${conversationId}-${user?.id}`}
              id={conversationId}
              enabled={!!model.data?.configured}
              onDeleted={() => selectConversation("")}
            />
          ) : (
            <div className="flex min-h-80 flex-col items-center justify-center rounded-xl border bg-card px-6 py-12 text-center shadow-xs">
              <span className="rounded-2xl bg-primary/8 p-4">
                <MessageSquare className="size-7 text-primary" />
              </span>
              <h2 className="mt-5 text-lg font-semibold">今天想了解什么？</h2>
              <p className="mt-2 text-sm text-muted-foreground">
                {selected
                  ? "例如：本月销售额是多少？按地区看看订单分布。"
                  : "先选择一个已发布主题，确定本次分析的数据范围。"}
              </p>
              {selected ? (
                <Button
                  className="mt-6"
                  disabled={create.isPending}
                  onClick={() => create.mutate()}
                >
                  <Plus className="size-4" />
                  {create.isPending ? "正在创建…" : "开始新会话"}
                </Button>
              ) : (
                <Button className="mt-6" variant="outline" asChild>
                  <Link to="/topics">查看业务主题</Link>
                </Button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function ConversationPanel({
  id,
  enabled,
  onDeleted,
}: {
  id: string
  enabled: boolean
  onDeleted: () => void
}) {
  const qc = useQueryClient()
  const stream = useConversationStream(id)
  const [question, setQuestion] = useState("")
  const [reset, setReset] = useState(false)
  const [mode, setMode] = useState<"auto" | "metrics" | "explore">("auto")
  const [autoExecute, setAutoExecute] = useState(true)
  const [choices, setChoices] = useState<Record<string, string>>({})
  const conversation = useQuery({
    queryKey: ["conversation", id],
    queryFn: async () =>
      (
        await AssistantService.getConversation({
          path: { conversation_id: id },
        })
      ).data,
    retry: false,
    gcTime: 0,
  })
  const data = conversation.data
  const tables = useQuery({
    queryKey: ["ask-tables", data?.topic_id],
    queryFn: async () =>
      (
        await AssistantService.explorationTables({
          path: { topic_id: data?.topic_id || "" },
        })
      ).data,
    enabled: !!data,
    retry: false,
  })
  const catalog = useQuery({
    queryKey: ["ask-catalog", data?.topic_id],
    queryFn: async () =>
      (
        await QueriesService.queryCatalog({
          path: { topic_id: data?.topic_id || "" },
        })
      ).data,
    enabled: !!data,
    retry: false,
    refetchInterval: 5000,
  })
  const update = (next: ConversationPublic) => {
    qc.setQueryData(["conversation", id], next)
    qc.invalidateQueries({ queryKey: ["conversations"] })
  }
  const ask = useMutation({
    mutationFn: async ({
      text,
      entityChoices,
    }: {
      text: string
      entityChoices?: Record<string, string>
    }) =>
      (
        await AssistantService.ask({
          path: { conversation_id: id },
          body: {
            request_id: crypto.randomUUID(),
            expected_revision: data?.revision || 0,
            question: text,
            reset_context: reset,
            mode,
            entity_choices: entityChoices || {},
          },
        })
      ).data,
    onSuccess: (next) => {
      update(next)
      setQuestion("")
      setReset(false)
      setChoices({})
      const turn = next.turns[next.turns.length - 1]
      if (autoExecute && turn?.status === "ready") execute.mutate(turn)
    },
    onSettled: () => qc.invalidateQueries({ queryKey: ["conversation", id] }),
  })
  const execute = useMutation({
    mutationFn: (turn: TurnPublic) =>
      AssistantService.execute({
        path: { conversation_id: id, turn_id: turn.id },
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["conversation", id] }),
  })
  const remove = useMutation({
    mutationFn: () =>
      AssistantService.deleteConversation({ path: { conversation_id: id } }),
    onSuccess: () => {
      qc.removeQueries({ queryKey: ["conversation", id] })
      qc.invalidateQueries({ queryKey: ["conversations"] })
      onDeleted()
    },
  })
  if (stream.error || conversation.isError || catalog.isError)
    return (
      <p role="alert" className="rounded-xl border p-5 text-destructive">
        {stream.error || errorMessage(conversation.error || catalog.error)}
        。请重新选择主题或新建会话。
      </p>
    )
  if (!data) return <p>正在加载会话…</p>
  const latest = data.turns[data.turns.length - 1]
  const busy =
    ask.isPending ||
    execute.isPending ||
    data.turns.some((t) => t.status === "planning")
  const metricLabel = (id: string) =>
    catalog.data?.metrics.find((m) => m.id === id)?.label || id
  const dimensionLabel = (id: string) =>
    catalog.data?.dimensions.find((d) => d.id === id)?.label || id
  return (
    <div className="min-w-0 space-y-4">
      <div className="rounded-xl border bg-card p-4 text-sm" aria-live="polite">
        <p className="text-xs text-muted-foreground">
          {stream.state} · 刷新页面可恢复此会话
        </p>
        <p className="mt-2 font-medium">
          {latest?.query_job_id
            ? stream.jobs.find((j) => j.id === latest.query_job_id)?.message ||
              "正在读取查询状态…"
            : latest?.message || "等待输入业务问题"}
        </p>
        <ol className="mt-3 flex flex-wrap gap-3 text-xs text-muted-foreground">
          <li>{latest ? "✓" : "○"} 接收问题</li>
          <li>
            {latest?.plan || latest?.sql_plan
              ? "✓"
              : latest?.status === "planning"
                ? "◌"
                : "○"}{" "}
            生成并校验计划
          </li>
          <li>{latest?.query_job_id ? "✓" : "○"} 提交只读查询</li>
          <li>
            {stream.jobs.find((j) => j.id === latest?.query_job_id)?.status ===
            "succeeded"
              ? "✓"
              : "○"}{" "}
            返回结果
          </li>
        </ol>
      </div>
      <div className="rounded-xl border bg-card p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-sm font-medium">参考指标（可选）</h2>
          <Button
            size="sm"
            variant="ghost"
            disabled={busy || remove.isPending}
            onClick={() => remove.mutate()}
          >
            删除会话
          </Button>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {catalog.data?.metrics.map((m) => (
            <button
              type="button"
              key={m.id}
              className="rounded-full border px-3 py-1 text-xs hover:bg-muted"
              title={m.description}
              onClick={() => setQuestion((q) => q + m.label)}
            >
              {m.label}
            </button>
          ))}
        </div>
        <p className="mt-3 text-xs text-muted-foreground">
          追问会沿用最近有效计划；勾选“清除上下文”可独立提问。语义更新或授权变化后需新建会话。
        </p>
      </div>
      <details className="rounded-xl border bg-card p-4 text-sm">
        <summary className="cursor-pointer">
          可探索的数据表与字段 · {tables.data?.length || 0} 张表
        </summary>
        {tables.isError && <p role="alert">{errorMessage(tables.error)}</p>}
        {tables.data?.map((table) => (
          <div key={String(table.name)} className="mt-3">
            <p className="font-medium">
              {String(table.description)}（{String(table.name)}）
            </p>
            <p className="break-words text-xs text-muted-foreground">
              {(table.columns as { name: string }[])
                .map((c) => c.name)
                .join("、")}
            </p>
          </div>
        ))}
        {tables.data?.length === 0 && (
          <p className="mt-2 text-muted-foreground">
            当前可使用参考指标；表字段探索需管理员配置成员查询授权。
          </p>
        )}
      </details>
      <div className="flex flex-wrap items-center gap-4 text-xs">
        <label>
          问答方式
          <select
            aria-label="问答方式"
            className={control}
            value={mode}
            onChange={(e) => setMode(e.target.value as typeof mode)}
          >
            <option value="auto">自动：指标口径 + 自由探索</option>
            <option value="explore">自由探索表字段</option>
            <option value="metrics">仅标准指标口径</option>
          </select>
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={autoExecute}
            onChange={(e) => setAutoExecute(e.target.checked)}
          />
          校验通过后自动查询
        </label>
      </div>
      {data.turns.map((turn) => (
        <article
          key={turn.id}
          className="min-w-0 space-y-4 rounded-xl border bg-card p-5"
        >
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span>第 {turn.sequence} 轮</span>
            <span>· {statuses[turn.status]}</span>
            {turn.model && <span>· {turn.model}</span>}
          </div>
          <h3 className="whitespace-pre-wrap break-words font-medium">
            {turn.question}
          </h3>
          <p
            role="status"
            className={`whitespace-pre-wrap break-words text-sm ${turn.status === "failed" ? "text-destructive" : "text-muted-foreground"}`}
          >
            {turn.message}
          </p>
          {turn.plan && (
            <div className="space-y-3 rounded-lg bg-muted/40 p-4 text-sm">
              <p>
                <span className="text-muted-foreground">指标：</span>
                {turn.plan.metrics.map(metricLabel).join("、")}
              </p>
              {turn.plan.metrics.map((id) => (
                <p key={id} className="text-xs leading-5 text-muted-foreground">
                  {metricLabel(id)}：
                  {catalog.data?.metrics.find((m) => m.id === id)?.description}
                </p>
              ))}
              <p>
                <span className="text-muted-foreground">分组：</span>
                {turn.plan.dimensions
                  ?.map(
                    (d) =>
                      `${dimensionLabel(d.dimension_id)}${d.grain !== "value" ? `（${{ day: "日", month: "月", year: "年" }[d.grain || "day"]}）` : ""}`,
                  )
                  .join("、") || "整体汇总"}
              </p>
              <p>
                <span className="text-muted-foreground">时间：</span>
                {turn.plan.time_range
                  ? `${turn.plan.time_range.start} 至 ${turn.plan.time_range.end}（不含结束日期）`
                  : "未额外限定"}
              </p>
              <p className="break-words">
                <span className="text-muted-foreground">附加过滤：</span>
                {turn.plan.filters
                  ?.map(
                    (f) =>
                      `${dimensionLabel(f.dimension_id)} ${f.operator} ${f.values?.join("、")}`,
                  )
                  .join("；") || "无"}
              </p>
              <p>
                <span className="text-muted-foreground">排序：</span>
                {turn.plan.order_by
                  ?.map(
                    (o) =>
                      `${metricLabel(o.field)} ${o.direction === "desc" ? "降序" : "升序"}`,
                  )
                  .join("、") || "未指定"}{" "}
                · 最多 {turn.plan.limit} 行
              </p>
              <details>
                <summary className="cursor-pointer text-xs text-muted-foreground">
                  查看结构化计划
                </summary>
                <pre className="mt-2 overflow-auto text-xs">
                  {JSON.stringify(turn.plan, null, 2)}
                </pre>
              </details>
            </div>
          )}
          {turn.id === latest?.id && turn.ambiguities?.length ? (
            <div className="space-y-3">
              {turn.ambiguities.map((a) => (
                <Field key={a.mention} label={`“${a.mention}”指哪一个？`}>
                  <select
                    aria-label={`实体选择 ${a.mention}`}
                    className={control}
                    value={choices[a.mention] || ""}
                    onChange={(e) =>
                      setChoices((c) => ({ ...c, [a.mention]: e.target.value }))
                    }
                  >
                    <option value="">请选择</option>
                    {a.options.map((o) => (
                      <option key={o.id} value={o.id}>
                        {o.label} · {o.dimension}
                      </option>
                    ))}
                  </select>
                </Field>
              ))}
              <Button
                disabled={
                  busy ||
                  !enabled ||
                  turn.ambiguities.some((a) => !choices[a.mention])
                }
                onClick={() =>
                  ask.mutate({ text: turn.question, entityChoices: choices })
                }
              >
                确认实体并继续
              </Button>
            </div>
          ) : null}
          {turn.status === "ready" && turn.id === latest?.id && (
            <Button
              disabled={execute.isPending || busy}
              onClick={() => execute.mutate(turn)}
            >
              核对无误，执行查询
            </Button>
          )}
          {turn.sql_plan && (
            <details className="rounded-lg bg-muted/40 p-4 text-sm">
              <summary className="cursor-pointer">
                自由探索 SQL · 最多 {turn.sql_plan.limit} 行
              </summary>
              <pre className="mt-3 overflow-auto whitespace-pre-wrap break-all text-xs">
                {turn.sql_plan.sql}
              </pre>
              <p className="mt-2 text-xs text-muted-foreground">
                基于授权表字段查询，具体过滤条件见 SQL。
              </p>
            </details>
          )}
          {turn.query_job_id && (
            <ResultPanel
              jobId={turn.query_job_id}
              chart={turn.chart}
              analysis={{
                conversationId: id,
                turnId: turn.id,
                automatic: !!turn.analysis_requested,
              }}
            />
          )}
          {(turn.plan || turn.sql_plan) && (
            <AnswerEvidence conversationId={id} turnId={turn.id} />
          )}
          {!["planning", "expired"].includes(turn.status) && (
            <AnswerFeedback
              conversationId={id}
              turnId={turn.id}
              saved={turn.feedback}
            />
          )}
        </article>
      ))}
      <form
        className="space-y-3 rounded-xl border bg-card p-5"
        onSubmit={(e) => {
          e.preventDefault()
          if (question.trim()) ask.mutate({ text: question.trim() })
        }}
      >
        <label htmlFor="ask-question" className="text-sm font-medium">
          {data.turns.length ? "继续追问或补充条件" : "你的业务问题"}
        </label>
        <textarea
          id="ask-question"
          className={`${control} mt-2 min-h-28 resize-y`}
          maxLength={2000}
          required
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="例如：列出最近的订单明细；按渠道画金额柱状图并分析差异；看看每天的订单趋势"
          disabled={busy}
        />
        <div className="flex flex-wrap items-center justify-between gap-3">
          <label className="flex items-center gap-2 text-xs text-muted-foreground">
            <input
              type="checkbox"
              checked={reset}
              onChange={(e) => setReset(e.target.checked)}
              disabled={busy}
            />
            清除上下文，独立提问
          </label>
          <Button type="submit" disabled={busy || !enabled || !question.trim()}>
            <Send className="size-4" />
            {busy ? "正在理解问题…" : "发送问题"}
          </Button>
        </div>
        <p className="text-xs leading-5 text-muted-foreground">
          问题及所选范围内的授权表字段会发送到已配置模型；已登记实体在本地解析。SQL
          经只读、字段及行权限校验后执行。请求分析时仅外发本次结果的数值摘要。
        </p>
      </form>
      {(ask.isError || execute.isError || remove.isError) && (
        <p role="alert" className="text-sm text-destructive">
          {errorMessage(ask.error || execute.error || remove.error)}
        </p>
      )}
    </div>
  )
}
