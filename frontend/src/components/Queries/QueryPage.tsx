import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  Clock3,
  Code2,
  Play,
  Plus,
  ShieldCheck,
  Square,
  Trash2,
} from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"
import {
  type Grouping,
  type PublishedTopic,
  QueriesService,
  type QueryFilter,
  type QueryJobPublic,
  type QueryPlan,
  type QueryPreview,
  TopicsService,
} from "@/client"
import { ResultAnalysis } from "@/components/Assistant/ResultAnalysis"
import { ResultChart } from "@/components/Queries/ResultChart"
import { control, errorMessage, Field } from "@/components/Semantic/shared"
import { Button } from "@/components/ui/button"
import useAuth from "@/hooks/useAuth"
import { PolicyEditor } from "./PolicyEditor"

const statuses: Record<string, string> = {
  queued: "排队中",
  running: "执行中",
  cancelling: "取消中",
  succeeded: "已完成",
  cancelled: "已取消",
  timed_out: "已超时",
  rejected: "授权已变化",
  failed: "执行失败",
  cleanup_pending: "待清理确认",
  expired: "已过期",
}
const active = ["queued", "running", "cancelling"]

export function QueryPage() {
  const { user } = useAuth()
  const [topicId, setTopicId] = useState("")
  const topics = useQuery({
    queryKey: ["query-topics", user?.id],
    queryFn: async () => (await TopicsService.listTopics()).data,
  })
  const selected =
    topicId || topics.data?.find((t) => t.availability === "ready")?.id || ""
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium tracking-widest text-muted-foreground">
            探索与分析
          </p>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight">
            查询验证
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            选择已发布指标，按授权范围查询，查看执行状态与结果。
          </p>
        </div>
      </div>
      <div className="rounded-xl border bg-card p-5">
        <Field label="业务主题">
          <select
            aria-label="业务主题"
            className={`${control} max-w-lg`}
            value={selected}
            onChange={(e) => setTopicId(e.target.value)}
          >
            <option value="">选择一个已发布主题</option>
            {topics.data
              ?.filter((t) => t.availability === "ready")
              .map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name} · v{t.current_version}
                </option>
              ))}
          </select>
        </Field>
        {topics.isError && (
          <p role="alert" className="mt-3 text-sm text-destructive">
            {errorMessage(topics.error)}
          </p>
        )}
      </div>
      {selected ? (
        <QueryWorkspace
          key={`${selected}-${user?.id}`}
          topicId={selected}
          admin={!!user?.is_superuser}
        />
      ) : (
        <p className="rounded-xl border border-dashed p-10 text-center text-muted-foreground">
          发布业务主题并配置查询授权后，即可开始验证。
        </p>
      )}
    </div>
  )
}

function QueryWorkspace({
  topicId,
  admin,
}: {
  topicId: string
  admin: boolean
}) {
  const [policyOpen, setPolicyOpen] = useState(false)
  const [jobId, setJobId] = useState("")
  const query = useQuery({
    queryKey: ["query-catalog", topicId],
    queryFn: async () =>
      (await QueriesService.queryCatalog({ path: { topic_id: topicId } })).data,
    retry: false,
    refetchInterval: 5000,
  })
  const history = useQuery({
    queryKey: ["queries", topicId],
    queryFn: async () =>
      (await QueriesService.listJobs({ query: { topic_id: topicId } })).data,
    refetchInterval: 1500,
  })
  return (
    <>
      {admin && (
        <div className="flex justify-end">
          <Button variant="outline" onClick={() => setPolicyOpen(!policyOpen)}>
            <ShieldCheck className="size-4" />
            {policyOpen ? "收起查询授权" : "管理查询授权"}
          </Button>
        </div>
      )}
      {admin && policyOpen && <PolicyEditor topicId={topicId} />}
      {query.isError ? (
        <div
          role="alert"
          className="rounded-xl border border-destructive/30 p-5 text-sm"
        >
          <p>{errorMessage(query.error)}</p>
          <Button
            variant="outline"
            className="mt-3"
            onClick={() => query.refetch()}
          >
            重新加载
          </Button>
        </div>
      ) : query.data ? (
        <Builder
          key={query.data.version}
          topic={query.data}
          onSubmitted={setJobId}
        />
      ) : (
        <p>正在加载可查询指标…</p>
      )}
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_280px]">
        {jobId ? (
          <ResultPanel key={jobId} jobId={jobId} />
        ) : (
          <div className="flex min-h-64 flex-col items-center justify-center rounded-xl border border-dashed p-8 text-center">
            <Play className="mb-4 size-7 text-muted-foreground" />
            <h2 className="font-medium">等待第一条查询</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              执行后在这里查看状态、数据和口径说明。
            </p>
          </div>
        )}
        <aside className="rounded-xl border bg-card p-4">
          <h2 className="mb-4 flex items-center gap-2 font-medium">
            <Clock3 className="size-4" />
            最近查询
          </h2>
          {history.isError && (
            <p role="alert" className="text-sm text-destructive">
              查询记录加载失败
            </p>
          )}
          <div className="max-h-[560px] space-y-2 overflow-auto">
            {history.data?.length === 0 && (
              <p className="text-sm text-muted-foreground">暂无查询记录</p>
            )}
            {history.data?.map((j) => (
              <button
                type="button"
                key={j.id}
                onClick={() => setJobId(j.id)}
                className={`w-full rounded-lg border p-3 text-left text-sm transition-colors hover:bg-muted ${jobId === j.id ? "border-primary bg-primary/5" : "border-transparent"}`}
              >
                <div className="flex justify-between gap-2">
                  <span>{statuses[j.status] || j.status}</span>
                  <span className="text-xs text-muted-foreground">
                    v{j.semantic_version}
                  </span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  {new Date(j.created_at).toLocaleTimeString()} · {j.row_count}{" "}
                  行{j.truncated ? " · 截断" : ""}
                </p>
              </button>
            ))}
          </div>
        </aside>
      </div>
      {admin && <Operations />}
    </>
  )
}

function Builder({
  topic,
  onSubmitted,
}: {
  topic: PublishedTopic
  onSubmitted: (id: string) => void
}) {
  const qc = useQueryClient()
  const [metrics, setMetrics] = useState<string[]>(
    [topic.metrics[0]?.id].filter(Boolean),
  )
  const [groups, setGroups] = useState<Grouping[]>([])
  const [filters, setFilters] = useState<(QueryFilter & { key: string })[]>([])
  const [start, setStart] = useState("")
  const [end, setEnd] = useState("")
  const [limit, setLimit] = useState(100)
  const [timeout, setTimeout] = useState(15)
  const [sort, setSort] = useState("")
  const [direction, setDirection] = useState<"asc" | "desc">("desc")
  const [preview, setPreview] = useState<{
    signature: string
    data: QueryPreview
  } | null>(null)
  const permitted = topic.dimensions.filter(
    (d) =>
      metrics.length > 0 &&
      metrics.every((m) =>
        topic.metrics
          .find((x) => x.id === m)
          ?.allowed_dimensions.includes(d.id),
      ),
  )
  const chosen = topic.metrics.filter((m) => metrics.includes(m.id))
  const timeDimension = topic.dimensions.find(
    (d) => d.id === chosen[0]?.time_dimension,
  )
  const plan: QueryPlan = {
    metrics,
    dimensions: groups,
    filters: filters.map(({ key: _key, ...f }) => f),
    limit,
    timeout_seconds: timeout,
    order_by: sort ? [{ field: sort, direction }] : [],
    time_range: start || end ? { start, end } : null,
  }
  const signature = JSON.stringify(plan)
  const previewMutation = useMutation({
    mutationFn: async () =>
      (
        await QueriesService.preview({
          path: { topic_id: topic.id },
          body: plan,
        })
      ).data,
    onSuccess: (data) => {
      if (data) setPreview({ signature, data })
    },
  })
  const run = useMutation({
    mutationFn: async () =>
      (
        await QueriesService.submit({
          body: { topic_id: topic.id, request_id: crypto.randomUUID(), plan },
        })
      ).data,
    onSuccess: (data) => {
      if (data) {
        onSubmitted(data.id)
        qc.invalidateQueries({ queryKey: ["queries", topic.id] })
        toast.success("查询已提交")
      }
    },
  })
  const error = run.error || previewMutation.error
  function toggleMetric(id: string) {
    setMetrics((values) =>
      values.includes(id) ? values.filter((x) => x !== id) : [...values, id],
    )
    setGroups([])
    setFilters([])
    setSort("")
    setPreview(null)
  }
  return (
    <section className="rounded-xl border bg-card p-5 sm:p-6">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-2">
        <h2 className="font-semibold">配置查询</h2>
        <p className="text-xs text-muted-foreground">
          发布 v{topic.version} · {topic.timezone} · {topic.owner}
        </p>
      </div>
      <Field label="指标（最多 10 个）">
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {topic.metrics.map((m) => (
            <label
              key={m.id}
              className={`flex cursor-pointer items-start gap-3 rounded-lg border p-3 ${metrics.includes(m.id) ? "border-primary/60 bg-primary/5" : ""}`}
            >
              <input
                aria-label={m.label}
                type="checkbox"
                className="mt-1 accent-primary"
                checked={metrics.includes(m.id)}
                disabled={!metrics.includes(m.id) && metrics.length >= 10}
                onChange={() => toggleMetric(m.id)}
              />
              <span>
                <span className="text-sm">{m.label}</span>
                <span className="ml-2 text-xs font-normal text-muted-foreground">
                  {m.unit}
                </span>
                <span className="mt-1 block text-xs font-normal leading-5 text-muted-foreground">
                  {m.description}
                </span>
              </span>
            </label>
          ))}
        </div>
      </Field>
      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <Field label="分组维度">
          <div className="flex flex-wrap gap-2">
            {permitted.map((d) => {
              const group = groups.find((g) => g.dimension_id === d.id)
              return (
                <div
                  key={d.id}
                  className="flex items-center gap-2 rounded-md border px-3 py-2"
                >
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      aria-label={`按${d.label}分组`}
                      checked={!!group}
                      disabled={!group && groups.length >= 5}
                      onChange={() => {
                        setGroups((values) =>
                          group
                            ? values.filter((g) => g.dimension_id !== d.id)
                            : [
                                ...values,
                                { dimension_id: d.id, grain: "value" },
                              ],
                        )
                        setSort("")
                      }}
                    />
                    {d.label}
                  </label>
                  {group && d.value_type === "date" && (
                    <select
                      aria-label={`${d.label}粒度`}
                      value={group.grain}
                      onChange={(e) =>
                        setGroups((values) =>
                          values.map((g) =>
                            g.dimension_id === d.id
                              ? {
                                  ...g,
                                  grain: e.target.value as Grouping["grain"],
                                }
                              : g,
                          ),
                        )
                      }
                      className="bg-transparent text-xs"
                    >
                      <option value="value">原值</option>
                      <option value="day">日</option>
                      <option value="month">月</option>
                      <option value="year">年</option>
                    </select>
                  )}
                </div>
              )
            })}
            {!permitted.length && (
              <p className="text-xs text-muted-foreground">
                当前指标没有共同可用的分组维度。
              </p>
            )}
          </div>
        </Field>
        <Field
          label={`时间范围${timeDimension ? ` · ${timeDimension.label}` : ""}`}
          hint="起点包含，终点不包含；留空查询全部已授权日期。"
        >
          <div className="grid grid-cols-2 gap-2">
            <input
              aria-label="开始日期"
              type={timeDimension?.value_type === "datetime" ? "text" : "date"}
              placeholder="ISO 时间（含时区）"
              disabled={!timeDimension}
              className={control}
              value={start}
              onChange={(e) => setStart(e.target.value)}
            />
            <input
              aria-label="结束日期"
              type={timeDimension?.value_type === "datetime" ? "text" : "date"}
              placeholder="ISO 时间（含时区）"
              disabled={!timeDimension}
              className={control}
              value={end}
              onChange={(e) => setEnd(e.target.value)}
            />
          </div>
        </Field>
      </div>
      <div className="mt-5 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">附加过滤</span>
          <Button
            size="sm"
            variant="ghost"
            disabled={!permitted.length || filters.length >= 20}
            onClick={() =>
              setFilters((values) => [
                ...values,
                {
                  key: crypto.randomUUID(),
                  dimension_id: permitted[0].id,
                  operator: "eq",
                  values: [""],
                },
              ])
            }
          >
            <Plus className="size-3.5" />
            添加过滤
          </Button>
        </div>
        {filters.map((f) => (
          <div key={f.key} className="flex flex-wrap items-center gap-2">
            <select
              aria-label="过滤维度"
              className={`${control} flex-1`}
              value={f.dimension_id}
              onChange={(e) =>
                setFilters((values) =>
                  values.map((x) =>
                    x.key === f.key
                      ? { ...x, dimension_id: e.target.value }
                      : x,
                  ),
                )
              }
            >
              {permitted.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.label}
                </option>
              ))}
            </select>
            <select
              aria-label="过滤操作"
              className={`${control} w-36`}
              value={f.operator}
              onChange={(e) =>
                setFilters((values) =>
                  values.map((x) =>
                    x.key === f.key
                      ? {
                          ...x,
                          operator: e.target.value as QueryFilter["operator"],
                          values: ["is_null", "is_not_null"].includes(
                            e.target.value,
                          )
                            ? []
                            : [""],
                        }
                      : x,
                  ),
                )
              }
            >
              {Object.entries({
                eq: "等于",
                in: "属于集合",
                gt: "大于",
                gte: "大于等于",
                lt: "小于",
                lte: "小于等于",
                between: "区间 [起,止)",
                is_null: "为空",
                is_not_null: "非空",
              }).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
            {!["is_null", "is_not_null"].includes(f.operator) && (
              <input
                aria-label="过滤值"
                className={`${control} flex-[2]`}
                value={f.values?.join(",")}
                placeholder={
                  f.operator === "in" || f.operator === "between"
                    ? "多个值用英文逗号分隔"
                    : "过滤值"
                }
                onChange={(e) =>
                  setFilters((values) =>
                    values.map((x) =>
                      x.key === f.key
                        ? {
                            ...x,
                            values: ["in", "between"].includes(x.operator)
                              ? e.target.value.split(",")
                              : [e.target.value],
                          }
                        : x,
                    ),
                  )
                }
              />
            )}
            <Button
              variant="ghost"
              size="icon"
              aria-label="删除过滤"
              onClick={() =>
                setFilters((values) => values.filter((x) => x.key !== f.key))
              }
            >
              <Trash2 className="size-4" />
            </Button>
          </div>
        ))}
      </div>
      <div className="mt-5 grid gap-3 sm:grid-cols-4">
        <Field label="结果行数">
          <input
            className={control}
            aria-label="结果行数"
            type="number"
            min={1}
            max={1000}
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
          />
        </Field>
        <Field label="执行时限（秒）">
          <input
            className={control}
            aria-label="执行时限"
            type="number"
            min={1}
            max={30}
            value={timeout}
            onChange={(e) => setTimeout(Number(e.target.value))}
          />
        </Field>
        <Field label="排序字段">
          <select
            aria-label="排序字段"
            className={control}
            value={sort}
            onChange={(e) => setSort(e.target.value)}
          >
            <option value="">默认分组顺序</option>
            {[
              ...chosen,
              ...topic.dimensions.filter((d) =>
                groups.some((g) => g.dimension_id === d.id),
              ),
            ].map((x) => (
              <option key={x.id} value={x.id}>
                {x.label}
              </option>
            ))}
          </select>
        </Field>
        <Field label="排序方向">
          <select
            aria-label="排序方向"
            className={control}
            value={direction}
            onChange={(e) => setDirection(e.target.value as "asc" | "desc")}
          >
            <option value="desc">从高到低</option>
            <option value="asc">从低到高</option>
          </select>
        </Field>
      </div>
      <div className="mt-6 flex flex-wrap gap-3">
        <Button
          variant="outline"
          disabled={!metrics.length || previewMutation.isPending}
          onClick={() => {
            run.reset()
            previewMutation.mutate()
          }}
        >
          <Code2 className="size-4" />
          {previewMutation.isPending ? "校验中…" : "校验并预览"}
        </Button>
        <Button
          disabled={
            !metrics.length || run.isPending || Boolean(start) !== Boolean(end)
          }
          onClick={() => {
            previewMutation.reset()
            run.mutate()
          }}
        >
          <Play className="size-4" />
          {run.isPending ? "提交中…" : "执行查询"}
        </Button>
        <span className="self-center text-xs text-muted-foreground">
          固定业务过滤自动生效
        </span>
      </div>
      {error && (
        <p
          role="alert"
          className="mt-4 rounded-lg bg-destructive/10 p-3 text-sm text-destructive"
        >
          {errorMessage(error)}
        </p>
      )}
      {preview?.signature === signature && (
        <div className="mt-4 rounded-lg border bg-muted/30 p-4 text-sm">
          <p className="flex items-center gap-2 font-medium">
            <ShieldCheck className="size-4 text-emerald-600" />
            校验通过 · {preview.data.policy_label}
          </p>
          <p className="mt-2 text-muted-foreground">
            {preview.data.columns.map((c) => c.label).join(" / ")} · 最多{" "}
            {preview.data.limit} 行 · {preview.data.timeout_seconds} 秒
          </p>
          {preview.data.sql && (
            <details className="mt-3">
              <summary className="cursor-pointer">参数化 SQL（管理员）</summary>
              <pre className="mt-2 max-h-60 overflow-auto whitespace-pre-wrap break-all rounded-md bg-background p-3 text-xs">
                {preview.data.sql}
              </pre>
              <p className="mt-2 text-xs text-muted-foreground">
                {preview.data.parameter_count} 个绑定参数，预览不显示实际值。
              </p>
            </details>
          )}
        </div>
      )}
    </section>
  )
}

export function ResultPanel({
  jobId,
  chart = "auto",
  analysis,
}: {
  jobId: string
  chart?: string
  analysis?: { conversationId: string; turnId: string; automatic: boolean }
}) {
  const qc = useQueryClient()
  const job = useQuery({
    queryKey: ["query-job", jobId],
    queryFn: async () =>
      (await QueriesService.getJob({ path: { job_id: jobId } })).data,
    refetchInterval: (q) =>
      q.state.data && active.includes(q.state.data.status) ? 750 : false,
  })
  const result = useQuery({
    queryKey: ["query-result", jobId],
    queryFn: async () =>
      (await QueriesService.result({ path: { job_id: jobId } })).data,
    enabled: job.data?.status === "succeeded",
    retry: false,
    staleTime: 0,
    gcTime: 0,
    refetchInterval: 2000,
  })
  const cancel = useMutation({
    mutationFn: () => QueriesService.cancel({ path: { job_id: jobId } }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["query-job", jobId] }),
  })
  if (job.isError) return <p role="alert">{errorMessage(job.error)}</p>
  const record = job.data
  if (!record) return <p>正在加载查询…</p>
  return (
    <section className="min-w-0 rounded-xl border bg-card p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="font-semibold">
            查询结果{" "}
            <span className="ml-2 text-sm font-normal text-muted-foreground">
              {statuses[record.status]}
            </span>
          </h2>
          <p className="mt-2 text-xs text-muted-foreground">
            语义 v{record.semantic_version} · {record.elapsed_ms ?? "—"} ms ·{" "}
            {record.row_count} 行 · 结果保留至{" "}
            {new Date(record.expires_at).toLocaleString()}
          </p>
        </div>
        {active.includes(record.status) && (
          <Button
            size="sm"
            variant="outline"
            disabled={cancel.isPending || record.status === "cancelling"}
            onClick={() => cancel.mutate()}
          >
            <Square className="size-3" />
            取消查询
          </Button>
        )}
      </div>
      <p className="my-4 text-sm">{record.message}</p>
      {cancel.isError && (
        <p role="alert" className="text-sm text-destructive">
          {errorMessage(cancel.error)}
        </p>
      )}
      {result.isError ? (
        <p
          role="alert"
          className="rounded-lg bg-destructive/10 p-4 text-sm text-destructive"
        >
          {errorMessage(result.error)}
        </p>
      ) : record.status === "succeeded" && result.data ? (
        <>
          <ResultChart result={result.data} preferred={chart} />
          {result.data.truncated && (
            <p className="mb-3 rounded-md bg-amber-500/10 p-3 text-sm text-amber-800 dark:text-amber-300">
              已达到结果上限，只展示部分分组；请缩小范围或增加行数。
            </p>
          )}
          <div className="max-h-[480px] overflow-auto rounded-lg border">
            <table className="w-full whitespace-nowrap text-sm">
              <thead className="sticky top-0 bg-muted">
                <tr>
                  {result.data.columns.map((c) => (
                    <th key={c.id} className="px-4 py-3 text-left font-medium">
                      {c.label}
                      {c.unit && (
                        <span className="ml-1 text-xs text-muted-foreground">
                          ({c.unit})
                        </span>
                      )}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.data.rows.map((row, i) => (
                  <tr key={`${jobId}-${i}`} className="border-t">
                    {row.map((value, j) => (
                      <td
                        key={result.data?.columns[j].id}
                        className={`px-4 py-3 ${result.data?.columns[j].value_type === "number" ? "font-mono tabular-nums" : ""}`}
                      >
                        {value === null ? (
                          <span className="text-muted-foreground">NULL</span>
                        ) : (
                          String(value)
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {result.data.rows.length === 0 && (
              <p className="p-8 text-center text-muted-foreground">
                当前筛选范围没有数据
              </p>
            )}
          </div>
          <ul className="mt-4 space-y-1 text-xs leading-5 text-muted-foreground">
            {result.data.notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
          {analysis && <ResultAnalysis {...analysis} />}
        </>
      ) : null}
      {record.sql && (
        <details className="mt-4 text-xs">
          <summary className="cursor-pointer text-muted-foreground">
            查看执行 SQL
          </summary>
          <pre className="mt-2 overflow-auto whitespace-pre-wrap break-all rounded-lg bg-muted/40 p-3">
            {record.sql}
          </pre>
        </details>
      )}
    </section>
  )
}

function Operations() {
  const [open, setOpen] = useState(false)
  const audit = useQuery({
    queryKey: ["query-audit"],
    queryFn: async () => (await QueriesService.audit()).data,
    enabled: open,
    refetchInterval: open ? 5000 : false,
  })
  const cleanup = useQuery({
    queryKey: ["query-cleanup"],
    queryFn: async () => (await QueriesService.pendingCleanup()).data,
    enabled: open,
    refetchInterval: open ? 5000 : false,
  })
  return (
    <section className="rounded-xl border bg-card p-5">
      <button
        type="button"
        className="flex items-center gap-2 text-sm font-medium"
        onClick={() => setOpen(!open)}
      >
        <ShieldCheck className="size-4" />
        {open ? "收起" : "查看"}执行审计与清理
      </button>
      {open && (
        <div className="mt-4 space-y-3">
          {cleanup.data?.map((job) => (
            <CleanupRow key={job.id} job={job} />
          ))}
          {audit.isError && <p role="alert">{errorMessage(audit.error)}</p>}
          <div className="max-h-64 overflow-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr>
                  <th className="p-2">时间</th>
                  <th>动作</th>
                  <th>任务</th>
                </tr>
              </thead>
              <tbody>
                {audit.data?.map((e) => (
                  <tr key={e.id} className="border-t">
                    <td className="p-2">
                      {e.created_at
                        ? new Date(e.created_at).toLocaleString()
                        : "—"}
                    </td>
                    <td>{statuses[e.action] || e.action}</td>
                    <td className="font-mono">
                      {e.job_id?.slice(0, 8) || "授权配置"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  )
}

function CleanupRow({ job }: { job: QueryJobPublic }) {
  const qc = useQueryClient()
  const [note, setNote] = useState("")
  const confirm = useMutation({
    mutationFn: () =>
      QueriesService.confirmCleanup({
        path: { job_id: job.id },
        body: { note },
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["query-cleanup"] })
      qc.invalidateQueries({ queryKey: ["query-audit"] })
    },
  })
  return (
    <div className="space-y-3 rounded-lg border border-amber-500/40 p-4">
      <p className="text-sm">
        任务 {job.id.slice(0, 8)} 尚未确认源库结束。请先由 DBA
        核实会话停止，再记录依据并解除占用。
      </p>
      <input
        aria-label="清理确认依据"
        className={control}
        placeholder="填写源库会话检查与清理依据（至少 10 字）"
        value={note}
        onChange={(e) => setNote(e.target.value)}
      />
      <Button
        variant="outline"
        size="sm"
        disabled={note.trim().length < 10 || confirm.isPending}
        onClick={() => confirm.mutate()}
      >
        确认源库已结束并解除占用
      </Button>
      {confirm.isError && (
        <p role="alert" className="text-sm text-destructive">
          {errorMessage(confirm.error)}
        </p>
      )}
    </div>
  )
}
