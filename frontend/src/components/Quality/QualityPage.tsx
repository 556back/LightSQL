import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  Activity,
  CheckCircle2,
  ClipboardCheck,
  FlaskConical,
  RefreshCw,
} from "lucide-react"
import { useState } from "react"
import {
  type DatasetInput,
  type FeedbackReviewPublic,
  QualityService,
  type ReviewInput,
  type RunInput,
} from "@/client"
import { control, errorMessage } from "@/components/Semantic/shared"
import { Button } from "@/components/ui/button"

type Dataset = {
  id: string
  name: string
  digest: string
  topic_id: string
  provenance: string
  semantic_version: number
  source_snapshot: string
  dev: number
  blind: number
}
type Summary = {
  total: number
  correct: number
  end_to_end_accuracy: number | null
  coverage: number | null
  answer_precision: number | null
  p95_ms: number
  critical_errors: number
  cost: string | null
  currency: string
  errors: Record<string, number>
  cases: { case_id: string; correct: boolean; error_category: string }[]
}
type Run = {
  id: string
  model: string
  context_variant: string
  evidence: string
  split: string
  created_at: string
  summary: Summary
}
type Operations = {
  query_capacity?: {
    global_limit: number
    source_limit: number
    actor_limit: number
    queue_timeout_seconds: number
    occupied: number
  }
  checked_at: string
  alerts: string[]
  workers: Record<string, { healthy: boolean; last_seen: string | null }>
  queues: Record<
    string,
    { statuses: Record<string, number>; oldest_wait_seconds: number }
  >
  queries: Record<string, number>
  model: {
    turns: number
    prompt_tokens: number
    completion_tokens: number
    statuses: Record<string, number>
  }
  feedback: Record<string, number>
  backup: {
    created_at: string
    restored_at: string | null
    size_bytes: number
  } | null
  disk_free_bytes: number
  notes: string[]
  sources: {
    source_id: string
    status: string
    count: number
    average_ms: number | null
  }[]
}
const date = (value: string | null) =>
  value ? new Date(value).toLocaleString() : "暂无记录"
const percent = (value: number | null) =>
  value === null ? "—" : `${(value * 100).toFixed(1)}%`
const statusLabels: Record<string, string> = {
  pending: "待审核",
  confirmed: "已确认",
  dismissed: "不采纳",
  resolved: "已解决",
}
function download(name: string, data: unknown) {
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }),
  )
  const link = document.createElement("a")
  link.href = url
  link.download = name
  link.click()
  URL.revokeObjectURL(url)
}

export function QualityPage() {
  const [tab, setTab] = useState("operations")
  return (
    <div className="min-w-0 space-y-6">
      <header>
        <p className="text-xs tracking-widest text-muted-foreground">
          QUALITY / 质量与运维
        </p>
        <h1 className="mt-2 text-2xl font-semibold">质量与运维</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          审核业务反馈、对比同一题集的评测结果，检查服务与恢复准备情况。
        </p>
      </header>
      <nav aria-label="质量管理栏目" className="flex flex-wrap gap-2">
        {[
          { id: "operations", name: "运行监控", icon: Activity },
          { id: "feedback", name: "反馈审核", icon: ClipboardCheck },
          { id: "evaluation", name: "质量评测", icon: FlaskConical },
        ].map((item) => (
          <Button
            key={item.id}
            variant={tab === item.id ? "default" : "outline"}
            onClick={() => setTab(item.id)}
          >
            <item.icon className="size-4" />
            {item.name}
          </Button>
        ))}
      </nav>
      {tab === "operations" ? (
        <OperationsPanel />
      ) : tab === "feedback" ? (
        <FeedbackPanel />
      ) : (
        <EvaluationPanel />
      )}
    </div>
  )
}

function OperationsPanel() {
  const query = useQuery({
    queryKey: ["quality", "operations"],
    queryFn: async () =>
      (await QualityService.operationsOverview()).data as Operations,
    refetchInterval: 15000,
  })
  if (query.isPending) return <p>正在读取运行状态…</p>
  if (query.isError)
    return <Failure error={query.error} retry={() => query.refetch()} />
  const data = query.data
  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-muted-foreground">
        <span>最近检查：{date(data.checked_at)} · 每 15 秒刷新</span>
        <Button variant="outline" size="sm" onClick={() => query.refetch()}>
          <RefreshCw className="size-4" />
          刷新状态
        </Button>
      </div>
      <section className="rounded-xl border bg-card p-5">
        <h2 className="font-semibold">需要关注</h2>
        {data.alerts.length ? (
          <ul className="mt-3 space-y-2 text-sm">
            {data.alerts.map((alert) => (
              <li key={alert} className="text-amber-700 dark:text-amber-400">
                {alert}
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-3 flex items-center gap-2 text-sm">
            <CheckCircle2 className="size-4 text-emerald-600" />
            当前检查未发现告警
          </p>
        )}
      </section>
      <div className="grid gap-4 md:grid-cols-2">
        {Object.entries(data.workers).map(([kind, worker]) => (
          <section key={kind} className="rounded-xl border p-5">
            <h2 className="font-semibold">
              {kind === "query" ? "查询" : "目录同步"} Worker ·{" "}
              {worker.healthy ? "心跳正常" : "待检查"}
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              最近心跳：{date(worker.last_seen)}
            </p>
            <p className="mt-2 text-sm">
              排队 {data.queues[kind].statuses.queued || 0} 项 · 最老等待{" "}
              {data.queues[kind].oldest_wait_seconds} 秒
            </p>
          </section>
        ))}
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <Stat
          title="近 24 小时查询成功"
          value={String(data.queries.succeeded || 0)}
        />
        <Stat title="近 24 小时规划轮次" value={String(data.model.turns)} />
        <Stat
          title="规划 Token（输入 / 输出）"
          value={`${data.model.prompt_tokens} / ${data.model.completion_tokens}`}
        />
      </div>
      {data.query_capacity && (
        <section className="rounded-xl border p-5">
          <h2 className="font-semibold">查询并发与排队</h2>
          <p className="mt-3 text-sm">
            已占用 {data.query_capacity.occupied} /{" "}
            {data.query_capacity.global_limit} 个执行名额 · 每个数据源最多{" "}
            {data.query_capacity.source_limit} 个 · 每人最多{" "}
            {data.query_capacity.actor_limit} 个
          </p>
          <p className="mt-2 text-sm text-muted-foreground">
            排队超过 {data.query_capacity.queue_timeout_seconds} 秒自动过期。
            取消中和清理未确认的任务继续占用名额；清理未确认的数据源暂停接收查询。
          </p>
        </section>
      )}
      <section className="rounded-xl border p-5">
        <h2 className="font-semibold">备份与容量</h2>
        <div className="mt-3 space-y-2 text-sm">
          <p>最近备份：{date(data.backup?.created_at || null)}</p>
          <p>该备份恢复验证：{date(data.backup?.restored_at || null)}</p>
          <p>
            应用磁盘可用：{(data.disk_free_bytes / 1024 ** 3).toFixed(1)} GiB
          </p>
          <p>待审核反馈：{data.feedback.pending || 0}</p>
        </div>
      </section>
      <details className="rounded-xl border p-5">
        <summary className="cursor-pointer font-medium">
          按数据源查看近 24 小时任务
        </summary>
        <div className="mt-3 space-y-2 text-sm">
          {data.sources.length
            ? data.sources.map((row) => (
                <p className="break-all" key={`${row.source_id}-${row.status}`}>
                  {row.source_id} · {row.status} · {row.count} 项 · 平均{" "}
                  {row.average_ms ?? "—"} ms
                </p>
              ))
            : "暂无查询任务"}
        </div>
      </details>
      <div className="space-y-1 text-xs text-muted-foreground">
        {data.notes.map((note) => (
          <p key={note}>{note}</p>
        ))}
      </div>
    </div>
  )
}
function Stat({ title, value }: { title: string; value: string }) {
  return (
    <section className="rounded-xl border p-5">
      <p className="text-sm text-muted-foreground">{title}</p>
      <p className="mt-3 text-2xl font-semibold">{value}</p>
    </section>
  )
}
function Failure({ error, retry }: { error: unknown; retry: () => void }) {
  return (
    <div role="alert" className="space-y-2">
      <p className="text-sm text-destructive">{errorMessage(error)}</p>
      <Button variant="outline" onClick={retry}>
        重试
      </Button>
    </div>
  )
}

function FeedbackPanel() {
  const [offset, setOffset] = useState(0)
  const query = useQuery({
    queryKey: ["quality", "feedback", offset],
    queryFn: async () =>
      (await QualityService.listFeedback({ query: { offset } })).data,
  })
  const datasets = useQuery({
    queryKey: ["quality", "datasets"],
    queryFn: async () =>
      (await QualityService.listDatasets()).data as Dataset[],
  })
  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        反馈加密保留 90
        天，仅管理员可审核。用户修改后重新进入待审核；已解决记录须关联回归题。审核不会自动发布语义知识。
      </p>
      {query.isPending && <p>正在读取反馈…</p>}
      {query.isError && (
        <Failure error={query.error} retry={() => query.refetch()} />
      )}
      {query.data?.length === 0 && (
        <div className="rounded-xl border p-8 text-center text-muted-foreground">
          暂无反馈，在问数工作台评价回答后会出现在这里。
        </div>
      )}
      {query.data?.map((record) => (
        <ReviewCard
          key={`${record.id}-${record.revision}`}
          record={record}
          datasets={datasets.data || []}
        />
      ))}
      <div className="flex gap-2">
        <Button
          variant="outline"
          disabled={offset === 0}
          onClick={() => setOffset(Math.max(0, offset - 100))}
        >
          上一页
        </Button>
        <Button
          variant="outline"
          disabled={(query.data?.length || 0) < 100}
          onClick={() => setOffset(offset + 100)}
        >
          下一页
        </Button>
      </div>
    </div>
  )
}

function ReviewCard({
  record,
  datasets,
}: {
  record: FeedbackReviewPublic
  datasets: Dataset[]
}) {
  const qc = useQueryClient()
  const [status, setStatus] = useState<ReviewInput["status"]>("confirmed")
  const [note, setNote] = useState("")
  const [datasetId, setDatasetId] = useState("")
  const [caseId, setCaseId] = useState("")
  const snapshot = record.snapshot as {
    question: string
    feedback: { rating: string; category: string; comment: string }
    reviews?: {
      status: string
      note: string
      at: string
      case_id: string | null
    }[]
  }
  const selected = useQuery({
    queryKey: ["quality", "dataset", datasetId],
    enabled: !!datasetId,
    queryFn: async () =>
      (await QualityService.getDataset({ path: { dataset_id: datasetId } }))
        .data as { definition: DatasetInput },
  })
  const mutation = useMutation({
    mutationFn: () =>
      QualityService.reviewFeedback({
        path: { feedback_id: record.id },
        body: {
          expected_revision: record.revision,
          status,
          note,
          dataset_id: datasetId || null,
          case_id: caseId || null,
        },
      }),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["quality", "feedback"] }),
  })
  return (
    <article className="min-w-0 rounded-xl border p-5">
      <div className="flex flex-wrap justify-between gap-2">
        <h2 className="break-words font-medium">{snapshot.question}</h2>
        <span className="text-sm text-muted-foreground">
          {statusLabels[record.status]} · v{record.revision}
        </span>
      </div>
      <p className="mt-2 text-sm">
        {snapshot.feedback.rating === "helpful" ? "有帮助" : "结果有问题"} ·{" "}
        {snapshot.feedback.category}
      </p>
      <p className="mt-2 whitespace-pre-wrap break-words text-sm">
        {snapshot.feedback.comment || "未填写说明"}
      </p>
      <p className="mt-2 text-xs text-muted-foreground">
        保留至 {date(record.expires_at)}
      </p>
      {!!snapshot.reviews?.length && (
        <details className="mt-3 text-sm">
          <summary>审核历史（{snapshot.reviews.length}）</summary>
          {snapshot.reviews.map((review, i) => (
            <p key={`${review.at}-${i}`} className="mt-2 break-words">
              {date(review.at)} · {statusLabels[review.status]} · {review.note}
              {review.case_id ? ` · 回归题 ${review.case_id}` : ""}
            </p>
          ))}
        </details>
      )}
      <form
        className="mt-4 grid gap-3 md:grid-cols-2"
        onSubmit={(event) => {
          event.preventDefault()
          mutation.mutate()
        }}
      >
        <label className="text-sm">
          审核结论
          <select
            aria-label="审核结论"
            className={control}
            value={status}
            onChange={(event) => setStatus(event.target.value as typeof status)}
          >
            {Object.entries(statusLabels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          关联题集
          <select
            aria-label="关联题集"
            className={control}
            value={datasetId}
            onChange={(event) => {
              setDatasetId(event.target.value)
              setCaseId("")
            }}
          >
            <option value="">暂不关联</option>
            {datasets
              .filter((d) => d.topic_id === record.topic_id)
              .map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
          </select>
        </label>
        {datasetId && (
          <label className="text-sm">
            回归题
            <select
              aria-label="回归题"
              className={control}
              value={caseId}
              onChange={(event) => setCaseId(event.target.value)}
            >
              <option value="">选择已核对题目</option>
              {selected.data?.definition.cases.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.id} · {c.question}
                </option>
              ))}
            </select>
          </label>
        )}
        <label className="text-sm md:col-span-2">
          审核说明
          <textarea
            aria-label="审核说明"
            className={`${control} min-h-20`}
            required
            maxLength={2000}
            value={note}
            onChange={(event) => setNote(event.target.value)}
          />
        </label>
        <div>
          <Button
            disabled={
              mutation.isPending ||
              !note.trim() ||
              (!!datasetId && !caseId) ||
              (status === "resolved" && !datasetId)
            }
          >
            保存审核
          </Button>
        </div>
        {mutation.isError && (
          <p role="alert" className="text-sm text-destructive">
            {errorMessage(mutation.error)}
          </p>
        )}
      </form>
    </article>
  )
}

function EvaluationPanel() {
  const qc = useQueryClient()
  const [datasetId, setDatasetId] = useState("")
  const [split, setSplit] = useState("dev")
  const [error, setError] = useState("")
  const datasets = useQuery({
    queryKey: ["quality", "datasets"],
    queryFn: async () =>
      (await QualityService.listDatasets()).data as Dataset[],
  })
  const runs = useQuery({
    queryKey: ["quality", "runs", datasetId],
    enabled: !!datasetId,
    queryFn: async () =>
      (await QualityService.listRuns({ query: { dataset_id: datasetId } }))
        .data as Run[],
  })
  const upload = useMutation({
    mutationFn: async ({
      file,
      kind,
    }: {
      file: File
      kind: "dataset" | "run"
    }) => {
      if (file.size > 2_000_000) throw new Error("文件不能超过 2 MB")
      const body = JSON.parse(await file.text())
      if (kind === "dataset") {
        const response = await QualityService.createDataset({
          body: body as DatasetInput,
        })
        setDatasetId(String(response.data.id))
      } else await QualityService.createRun({ body: body as RunInput })
    },
    onSuccess: () => {
      setError("")
      qc.invalidateQueries({ queryKey: ["quality"] })
    },
    onError: (e) => setError(errorMessage(e)),
  })
  const exportData = async () => {
    try {
      download(
        "lightsql-gold.json",
        (await QualityService.getDataset({ path: { dataset_id: datasetId } }))
          .data,
      )
    } catch (e) {
      setError(errorMessage(e))
    }
  }
  return (
    <div className="space-y-5">
      <section className="rounded-xl border p-5">
        <h2 className="font-semibold">金标题集与运行记录</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          导入经核对的题集及逐题运行结果，服务端按实际结果计算分数。仅比较同一题集、集合和数据快照；A
          完整语义、B 匿名化、C 逻辑语义与本地实体、D 内部模型。回放仅验证流程。
        </p>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {[
            { kind: "dataset" as const, label: "导入金标题集 JSON" },
            { kind: "run" as const, label: "导入评测运行 JSON" },
          ].map((item) => (
            <label key={item.kind} className="text-sm">
              {item.label}
              <input
                aria-label={item.label}
                className={`${control} mt-2`}
                type="file"
                accept="application/json,.json"
                disabled={upload.isPending}
                onChange={(event) => {
                  const file = event.target.files?.[0]
                  if (file) upload.mutate({ file, kind: item.kind })
                  event.target.value = ""
                }}
              />
            </label>
          ))}
        </div>
        {error && (
          <p role="alert" className="mt-3 text-sm text-destructive">
            {error}
          </p>
        )}
        <div className="mt-4 flex flex-wrap items-end gap-3">
          <label className="min-w-0 basis-full text-sm sm:flex-1 sm:basis-0">
            比较题集
            <select
              aria-label="比较题集"
              className={control}
              value={datasetId}
              onChange={(event) => setDatasetId(event.target.value)}
            >
              <option value="">选择题集</option>
              {datasets.data?.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} ·{" "}
                  {d.provenance === "synthetic" ? "合成" : "业务审核"} · 开发{" "}
                  {d.dev} / 盲测 {d.blind}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            集合
            <select
              aria-label="评测集合"
              className={control}
              value={split}
              onChange={(event) => setSplit(event.target.value)}
            >
              <option value="dev">开发集</option>
              <option value="blind">盲测集</option>
            </select>
          </label>
          <Button variant="outline" disabled={!datasetId} onClick={exportData}>
            导出题集
          </Button>
        </div>
        {datasets.isError && (
          <Failure error={datasets.error} retry={() => datasets.refetch()} />
        )}
      </section>
      {!datasetId && (
        <p className="py-6 text-center text-muted-foreground">
          选择或导入题集，开始核对评测记录。
        </p>
      )}
      {runs.isError && (
        <Failure error={runs.error} retry={() => runs.refetch()} />
      )}
      {!!datasetId &&
        runs.data?.filter((run) => run.split === split).length === 0 && (
          <p className="py-6 text-center text-muted-foreground">
            该集合尚无评测运行。
          </p>
        )}
      {runs.data
        ?.filter((run) => run.split === split)
        .map((run) => (
          <article key={run.id} className="min-w-0 rounded-xl border p-5">
            <h3 className="break-words font-semibold">
              {run.model} · {run.context_variant} ·{" "}
              {run.evidence === "live_model"
                ? "真实模型（导入记录）"
                : run.evidence === "protocol_replay"
                  ? "协议回放 · 非质量结论"
                  : "人工记录"}
            </h3>
            <p className="mt-1 text-xs text-muted-foreground">
              {date(run.created_at)} · 正确 {run.summary.correct} /{" "}
              {run.summary.total} · 关键错误 {run.summary.critical_errors}
            </p>
            <div className="mt-4 grid grid-cols-2 gap-4 text-sm md:grid-cols-4">
              <p>
                端到端正确率
                <br />
                <strong>{percent(run.summary.end_to_end_accuracy)}</strong>
              </p>
              <p>
                可回答题覆盖率
                <br />
                <strong>{percent(run.summary.coverage)}</strong>
              </p>
              <p>
                已回答精度
                <br />
                <strong>{percent(run.summary.answer_precision)}</strong>
              </p>
              <p>
                P95 / 费用
                <br />
                <strong>
                  {run.summary.p95_ms} ms /{" "}
                  {run.summary.cost === null
                    ? "未提供"
                    : `${run.summary.cost} ${run.summary.currency}`}
                </strong>
              </p>
            </div>
            <details className="mt-4 text-sm">
              <summary className="cursor-pointer">逐题错误分析</summary>
              {run.summary.cases.map((c) => (
                <p key={c.case_id} className="mt-2 break-words">
                  {c.case_id} · {c.correct ? "通过" : c.error_category}
                </p>
              ))}
            </details>
            <Button
              className="mt-4"
              variant="outline"
              size="sm"
              onClick={async () => {
                try {
                  download(
                    `run-${run.id}.json`,
                    (await QualityService.getRun({ path: { run_id: run.id } }))
                      .data,
                  )
                } catch (e) {
                  setError(errorMessage(e))
                }
              }}
            >
              导出运行证据
            </Button>
          </article>
        ))}
      <p className="text-xs text-muted-foreground">
        运行记录中的模型、脱敏方式、费用和关键错误由导入者负责核对；此页面不自动认证模型身份或宣布上线达标。缺少费用显示为未知。
      </p>
    </div>
  )
}
