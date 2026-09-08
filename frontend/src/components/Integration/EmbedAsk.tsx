import { useCallback, useEffect, useRef, useState } from "react"
import { ResultChart } from "@/components/Queries/ResultChart"
import {
  createIntegrationApi,
  IntegrationError,
  type Result,
  type Task,
} from "./api"

const active = new Set([
  "queued",
  "planning",
  "querying",
  "analyzing",
  "cancelling",
  "cleanup_pending",
])
type Topic = { id: string; name: string }
type Session = {
  access_token: string
  expires_in: number
  session_id: string
  principal_id: string
  topic_id: string | null
}
type Config = { name: string; origins: string[]; scopes: string[] }

export function EmbedAsk() {
  const [config, setConfig] = useState<Config | null>(null)
  const [authorized, setAuthorized] = useState(false)
  const [error, setError] = useState("")
  const [topics, setTopics] = useState<Topic[]>([])
  const [topic, setTopic] = useState("")
  const [fixedTopic, setFixedTopic] = useState(false)
  const [question, setQuestion] = useState("")
  const [tasks, setTasks] = useState<Task[]>([])
  const [results, setResults] = useState<Record<string, Result>>({})
  const [conversation, setConversation] = useState<string | null>(null)
  const [mode, setMode] = useState("metrics")
  const [analysis, setAnalysis] = useState(false)
  const [busy, setBusy] = useState(false)
  const [choices, setChoices] = useState<Record<string, string>>({})
  const [appearance, setAppearance] = useState({
    title: "智能问数",
    welcome: "选择业务主题，开始提问。",
    theme: "light",
  })
  const token = useRef("")
  const session = useRef<Session | null>(null)
  const channel = useRef<{ origin: string; instanceId: string } | null>(null)
  const challenge = useRef(crypto.randomUUID().replace(/-/g, ""))
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const generation = useRef(0)
  const pending = useRef<{ body: unknown; key: string } | null>(null)
  const notified = useRef(new Set<string>())
  const api = useRef(createIntegrationApi(() => token.current)).current
  const send = useCallback(
    (type: string, payload: Record<string, unknown> = {}) => {
      if (channel.current)
        window.parent.postMessage(
          {
            version: 1,
            instanceId: channel.current.instanceId,
            type,
            ...payload,
          },
          channel.current.origin,
        )
    },
    [],
  )
  const reset = useCallback(() => {
    generation.current++
    token.current = ""
    setAuthorized(false)
    setTasks([])
    setResults({})
    setTopics([])
    setConversation(null)
    setChoices({})
    pending.current = null
  }, [])
  useEffect(() => {
    const id = new URLSearchParams(location.search).get("client_id")
    let stopped = false
    fetch(`/api/integration/v1/embed/config/${encodeURIComponent(id || "")}`, {
      credentials: "omit",
      cache: "no-store",
    })
      .then(async (r) => {
        if (!r.ok) throw new Error("嵌入应用不可用")
        const data = await r.json()
        if (!stopped) setConfig(data)
      })
      .catch((e) => {
        if (!stopped) setError(e.message)
      })
    return () => {
      stopped = true
    }
  }, [])
  useEffect(() => {
    if (!config) return
    let exchanging = false
    const receive = async (event: MessageEvent) => {
      const message = event.data
      if (
        event.source !== window.parent ||
        !config.origins.includes(event.origin) ||
        !message ||
        message.version !== 1 ||
        typeof message.instanceId !== "string"
      )
        return
      if (
        channel.current &&
        (channel.current.origin !== event.origin ||
          channel.current.instanceId !== message.instanceId)
      )
        return
      if (message.type === "init") {
        channel.current = {
          origin: event.origin,
          instanceId: message.instanceId,
        }
        if (!token.current) send("ready", { challenge: challenge.current })
        return
      }
      if (!channel.current) return
      if (message.type === "context") {
        const options = message.options || {}
        setAppearance({
          title: String(options.title || "智能问数").slice(0, 80),
          welcome: String(options.welcome || "选择业务主题，开始提问。").slice(
            0,
            300,
          ),
          theme: options.theme === "dark" ? "dark" : "light",
        })
        if (typeof options.question === "string")
          setQuestion(options.question.slice(0, 2000))
        return
      }
      if (message.type === "destroy") {
        try {
          if (session.current)
            await api(
              `/embed/sessions/${session.current.session_id}`,
              undefined,
              "DELETE",
            )
          send("destroyed")
        } catch {
          send("error", {
            message: "请由宿主后端撤销会话",
            sessionId: session.current?.session_id,
          })
        }
        reset()
        return
      }
      if (
        message.type !== "authenticate" ||
        typeof message.ticket !== "string" ||
        exchanging
      )
        return
      exchanging = true
      try {
        const next = await api<Session>("/embed/sessions", {
          ticket: message.ticket,
          challenge: challenge.current,
        })
        if (
          session.current &&
          session.current.principal_id !== next.principal_id
        )
          reset()
        session.current = next
        token.current = next.access_token
        setAuthorized(true)
        setError("")
        setFixedTopic(Boolean(next.topic_id))
        const data = await api<Topic[]>("/topics")
        setTopics(data)
        setTopic(
          (current) =>
            next.topic_id ||
            (data.some((t) => t.id === current) ? current : data[0]?.id || ""),
        )
        send("authenticated", { sessionId: next.session_id })
        if (timer.current) clearTimeout(timer.current)
        timer.current = setTimeout(
          () => send("auth_required", { challenge: challenge.current }),
          (next.expires_in - 60) * 1000,
        )
      } catch (e) {
        setError(e instanceof Error ? e.message : "身份验证失败")
        send("error", { message: "身份验证失败" })
      } finally {
        exchanging = false
      }
    }
    window.addEventListener("message", receive)
    return () => {
      window.removeEventListener("message", receive)
      if (timer.current) clearTimeout(timer.current)
    }
  }, [config, api, reset, send])
  useEffect(() => {
    const observer = new ResizeObserver(() =>
      send("resize", { height: document.documentElement.scrollHeight }),
    )
    observer.observe(document.body)
    return () => observer.disconnect()
  }, [send])
  useEffect(() => {
    if (!authorized) return
    let stopped = false
    let handle: ReturnType<typeof setTimeout>
    const run = async () => {
      const epoch = generation.current
      try {
        const data = await api<Task[]>("/tasks")
        if (stopped || generation.current !== epoch) return
        setTasks(data.reverse())
        const visible = data
          .filter(
            (t) =>
              t.conversation_id === conversation &&
              ["succeeded", "analyzing"].includes(t.status),
          )
          .slice(-5)
        const next: Record<string, Result> = {}
        for (const task of visible) {
          try {
            next[task.task_id] = await api<Result>(
              `/tasks/${task.task_id}/result`,
            )
          } catch (e) {
            if (e instanceof IntegrationError && e.status === 409) continue
            throw e
          }
        }
        if (!stopped && generation.current === epoch) {
          setResults(next)
          for (const task of visible) {
            if (
              task.status === "succeeded" &&
              next[task.task_id] &&
              !notified.current.has(task.task_id)
            ) {
              notified.current.add(task.task_id)
              send("task_completed", { taskId: task.task_id })
            }
          }
        }
      } catch (e) {
        if (!stopped) {
          setResults({})
          setTasks([])
          if (e instanceof IntegrationError && e.status === 401) {
            setAuthorized(false)
            send("auth_required", { challenge: challenge.current })
          }
          setError(e instanceof Error ? e.message : "暂时无法读取会话")
        }
      } finally {
        if (!stopped) handle = setTimeout(run, 5000)
      }
    }
    void run()
    return () => {
      stopped = true
      clearTimeout(handle)
    }
  }, [authorized, api, conversation, send])
  const visible = tasks.filter(
    (t) => t.conversation_id === conversation && t.conversation_id,
  )
  const latest = visible[visible.length - 1]
  const submit = async () => {
    if (busy || !topic || !question.trim()) return
    setBusy(true)
    setError("")
    const body = {
      topic_id: topic,
      question: question.trim(),
      mode,
      include_analysis: analysis,
      conversation_id: conversation,
      expected_revision: latest?.revision || 0,
      entity_choices: choices,
    }
    if (
      !pending.current ||
      JSON.stringify(pending.current.body) !== JSON.stringify(body)
    )
      pending.current = { body, key: crypto.randomUUID() }
    const epoch = generation.current
    try {
      const task = await api<Task>(
        "/answers",
        pending.current.body,
        "POST",
        pending.current.key,
      )
      if (epoch !== generation.current) return
      // A newly queued answer exposes its deterministic conversation UUID.
      setConversation(task.conversation_id)
      setTasks((current) => [
        ...current.filter((t) => t.task_id !== task.task_id),
        task,
      ])
      setQuestion("")
      setChoices({})
      pending.current = null
    } catch (e) {
      setError(e instanceof Error ? e.message : "提交失败，可使用相同问题重试")
    } finally {
      setBusy(false)
    }
  }
  const newConversation = () => {
    setConversation(null)
    setResults({})
    setChoices({})
    pending.current = null
  }
  return (
    <main
      className={`${appearance.theme === "dark" ? "dark" : ""} min-h-screen bg-background text-foreground`}
    >
      <div className="mx-auto flex min-h-screen max-w-5xl flex-col gap-4 p-4 sm:p-6">
        <header className="flex items-center justify-between gap-3">
          <div>
            <h1 className="text-xl font-semibold">{appearance.title}</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {appearance.welcome}
            </p>
          </div>
          <button
            type="button"
            className="rounded-lg border px-3 py-2 text-sm"
            onClick={newConversation}
          >
            新对话
          </button>
        </header>
        {!authorized && (
          <p role="status" className="rounded-lg border p-4">
            正在等待宿主系统验证身份…
          </p>
        )}
        {error && (
          <p
            role="alert"
            className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive"
          >
            {error}
          </p>
        )}
        {authorized && (
          <>
            <div className="flex flex-wrap gap-2">
              <select
                aria-label="业务主题"
                className="min-w-0 flex-1 rounded-lg border bg-background p-2"
                disabled={fixedTopic}
                value={topic}
                onChange={(e) => {
                  setTopic(e.target.value)
                  newConversation()
                }}
              >
                <option value="">选择主题</option>
                {topics.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
              <select
                aria-label="历史会话"
                className="max-w-56 rounded-lg border bg-background p-2"
                value={conversation || ""}
                onChange={(e) => {
                  setConversation(e.target.value || null)
                  setTopic(
                    tasks.find((t) => t.conversation_id === e.target.value)
                      ?.topic_id || topic,
                  )
                  setResults({})
                }}
              >
                <option value="">新对话 / 历史</option>
                {tasks
                  .filter(
                    (t, i, all) =>
                      t.conversation_id &&
                      all.findIndex(
                        (x) => x.conversation_id === t.conversation_id,
                      ) === i,
                  )
                  .map((t) => (
                    <option key={t.task_id} value={t.conversation_id || ""}>
                      {t.question.slice(0, 30)}
                    </option>
                  ))}
              </select>
            </div>
            <section aria-live="polite" className="min-h-40 flex-1 space-y-4">
              {!visible.length && (
                <p className="py-12 text-center text-sm text-muted-foreground">
                  输入业务问题，查询你有权访问的数据。
                </p>
              )}
              {visible.map((task) => (
                <article
                  key={task.task_id}
                  className="min-w-0 space-y-3 rounded-xl border p-4"
                >
                  <p className="font-medium">{task.question}</p>
                  <p className="text-sm text-muted-foreground">
                    {task.message}
                  </p>
                  {active.has(task.status) && (
                    <button
                      type="button"
                      className="rounded border px-3 py-1 text-sm"
                      onClick={() =>
                        void api(`/tasks/${task.task_id}/cancel`, {}).catch(
                          (e) => setError(e.message),
                        )
                      }
                    >
                      取消
                    </button>
                  )}
                  {task.clarification?.ambiguities.map((a) => (
                    <label key={a.mention} className="block text-sm">
                      {a.mention}
                      <select
                        className="ml-2 rounded border bg-background p-2"
                        value={choices[a.mention] || ""}
                        onChange={(e) =>
                          setChoices((c) => ({
                            ...c,
                            [a.mention]: e.target.value,
                          }))
                        }
                      >
                        <option value="">请选择后继续提问</option>
                        {a.options.map((o) => (
                          <option key={o.id} value={o.id}>
                            {o.label}
                          </option>
                        ))}
                      </select>
                    </label>
                  ))}
                  {results[task.task_id] && (
                    <ResultView result={results[task.task_id]} />
                  )}
                </article>
              ))}
            </section>
            <form
              className="sticky bottom-0 space-y-3 rounded-xl border bg-background p-3"
              onSubmit={(e) => {
                e.preventDefault()
                void submit()
              }}
            >
              <textarea
                aria-label="问题"
                className="min-h-20 w-full resize-y rounded-lg border bg-background p-3 text-sm"
                maxLength={2000}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="例如：上个月各区域净销售额是多少？"
              />
              <div className="flex flex-wrap items-center gap-3 text-sm">
                <select
                  aria-label="查询模式"
                  className="rounded border bg-background p-2"
                  value={mode}
                  onChange={(e) => setMode(e.target.value)}
                >
                  <option value="metrics">标准指标</option>
                  {config?.scopes.includes("explore") && (
                    <>
                      <option value="auto">自动选择</option>
                      <option value="explore">自由探索</option>
                    </>
                  )}
                </select>
                {config?.scopes.includes("analysis") && (
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={analysis}
                      onChange={(e) => setAnalysis(e.target.checked)}
                    />
                    分析结果
                  </label>
                )}
                <button
                  type="submit"
                  disabled={
                    busy ||
                    !question.trim() ||
                    !topic ||
                    visible.some((t) => active.has(t.status))
                  }
                  className="ml-auto rounded-lg bg-primary px-5 py-2 text-primary-foreground disabled:opacity-50"
                >
                  {busy ? "正在提交…" : "发送"}
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </main>
  )
}

function ResultView({ result }: { result: Result }) {
  return (
    <div className="min-w-0 space-y-3">
      <ResultChart result={result} preferred={result.chart} />
      {result.truncated && (
        <p className="text-sm text-amber-700">结果已截断，分析仅覆盖返回行。</p>
      )}
      <div className="max-h-96 overflow-auto rounded-lg border">
        <table className="w-full whitespace-nowrap text-sm">
          <thead>
            <tr>
              {result.columns.map((c) => (
                <th key={c.id} className="bg-muted p-3 text-left">
                  {c.label}
                  {c.unit ? `（${c.unit}）` : ""}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {result.rows.map((row, i) => (
              <tr key={JSON.stringify([i, row])}>
                {row.map((v, j) => (
                  <td key={result.columns[j].id} className="border-t p-3">
                    {v === null ? "NULL" : String(v)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {!result.rows.length && (
          <p className="p-3 text-sm">没有符合条件的数据。</p>
        )}
      </div>
      {result.analysis && (
        <div className="space-y-2 text-sm">
          <p className="text-muted-foreground">{result.analysis.scope}</p>
          {(result.analysis.findings || []).map((f) => (
            <p key={f.interpretation}>
              {f.interpretation}{" "}
              {f.fact_ids
                .map((id) => {
                  const fact = result.analysis?.facts.find((x) => x.id === id)
                  return fact ? `${fact.label}：${fact.value}` : ""
                })
                .join("；")}{" "}
              {f.next_step}
            </p>
          ))}
        </div>
      )}
      {result.analysis_status === "failed" && (
        <p className="text-sm">分析未完成，查询结果仍可核对。</p>
      )}
      <details className="text-sm">
        <summary className="cursor-pointer">
          核对口径与来源 · v{result.semantic_version}
        </summary>
        <div className="mt-2 space-y-2 text-muted-foreground">
          <p>
            业务主题：{String(result.evidence?.topic || "—")} · 时区：
            {String(result.evidence?.timezone || "—")}
          </p>
          {(["metrics", "fixed_filters", "sources", "notes"] as const).map(
            (key) => {
              const items = result.evidence?.[key]
              return Array.isArray(items)
                ? items.map((item, index) => (
                    <p key={`${key}-${index}`}>{String(item)}</p>
                  ))
                : null
            },
          )}
        </div>
        <p>结果有效期：{new Date(result.expires_at).toLocaleString()}</p>
      </details>
    </div>
  )
}
