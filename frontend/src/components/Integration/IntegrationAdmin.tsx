import { useCallback, useEffect, useRef, useState } from "react"
import { ValidatedForm } from "@/components/ui/validated-form"
import useAuth from "@/hooks/useAuth"
import { IntegrationGuide } from "./IntegrationGuide"

type ClientConfig = {
  id?: string
  revision?: number
  name: string
  ceiling_user_id: string
  topic_ids: string[]
  scopes: string[]
  origins: string[]
  enabled: boolean
  max_pending: number
  requests_per_minute: number
  model_calls_per_day: number
  assertion_issuer: string
  assertion_public_key: string
}
const initial: ClientConfig = {
  name: "",
  ceiling_user_id: "",
  topic_ids: [],
  scopes: ["query", "ask", "embed"],
  origins: [],
  enabled: true,
  max_pending: 3,
  requests_per_minute: 120,
  model_calls_per_day: 100,
  assertion_issuer: "",
  assertion_public_key: "",
}
async function internal<T>(
  path: string,
  body?: unknown,
  method = body === undefined ? "GET" : "POST",
): Promise<T> {
  const r = await fetch(`/api/v1${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
      "Content-Type": "application/json",
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok)
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : Array.isArray(data.detail)
          ? data.detail
              .map(
                (item: { loc: string[]; msg: string }) =>
                  `${item.loc.slice(1).join(" / ")}: ${item.msg}`,
              )
              .join("；")
          : data.message || `请求失败（${r.status}），请检查服务状态后重试`,
    )
  return data
}
export function IntegrationAdmin() {
  const { user } = useAuth()
  const [clients, setClients] = useState<ClientConfig[]>([])
  const [users, setUsers] = useState<
    { id: string; email: string; is_superuser: boolean; is_active: boolean }[]
  >([])
  const [topics, setTopics] = useState<{ id: string; name: string }[]>([])
  const [form, setForm] = useState<ClientConfig>(initial)
  const [origins, setOrigins] = useState("")
  const [error, setError] = useState("")
  const [secret, setSecret] = useState("")
  const [subject, setSubject] = useState("")
  const [mappedUser, setMappedUser] = useState("")
  const [identities, setIdentities] = useState<
    { subject: string; user_id: string; enabled: boolean }[]
  >([])
  const [audit, setAudit] = useState<unknown[]>([])
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState("")
  const [search, setSearch] = useState("")
  const [checking, setChecking] = useState(false)
  const [checkSnapshot, setCheckSnapshot] = useState("")
  const formSnapshot = JSON.stringify([form, origins])
  const [check, setCheck] = useState<{
    ok: boolean
    topics: { topic_id: string; name?: string; ok: boolean; message: string }[]
    warnings: string[]
  } | null>(null)
  const selection = useRef(0)
  const [baseline, setBaseline] = useState(JSON.stringify(initial))
  const dirty =
    JSON.stringify(form) !== baseline || origins !== form.origins.join("\n")
  const canLeave = () =>
    (!secret || window.confirm("当前密钥仅显示一次，请确认已保存后继续。")) &&
    (!dirty || window.confirm("有尚未保存的应用配置，确认放弃修改？"))
  const load = useCallback(
    async () => setClients(await internal<ClientConfig[]>("/integrations/")),
    [],
  )
  useEffect(() => {
    if (user?.is_superuser)
      void Promise.all([
        load(),
        (async () => {
          const all: typeof users = []
          for (let skip = 0; ; skip += 100) {
            const page = await internal<{ data: typeof users; count: number }>(
              `/users/?skip=${skip}&limit=100`,
            )
            all.push(...page.data)
            if (!page.data.length || all.length >= page.count) break
          }
          setUsers(all)
        })(),
        internal<typeof topics>("/topics/").then(setTopics),
      ]).catch((e) => setError(e.message))
  }, [user?.is_superuser, load])
  const choose = async (client: ClientConfig) => {
    const request = ++selection.current
    setForm(client)
    setBaseline(JSON.stringify(client))
    setOrigins(client.origins.join("\n"))
    setSecret("")
    setError("")
    setNotice("")
    setCheck(null)
    setIdentities([])
    setAudit([])
    const [nextIdentities, nextAudit] = await Promise.all([
      internal<typeof identities>(`/integrations/${client.id}/identities`),
      internal<unknown[]>(`/integrations/${client.id}/audit`),
    ])
    if (selection.current !== request) return
    setIdentities(nextIdentities)
    setAudit(nextAudit)
  }
  const payload = () => {
    const { id: _id, revision: _revision, ...data } = form
    if (!data.name.trim()) throw new Error("请填写应用名称")
    if (!data.ceiling_user_id) throw new Error("请选择权限上限用户")
    if (!data.topic_ids.length) throw new Error("请至少选择一个开放主题")
    if (!data.scopes.length) throw new Error("请至少选择一种开放能力")
    const values = [...new Set(origins.split(/[\s,，]+/).filter(Boolean))].map(
      (value) => {
        let url: URL
        try {
          url = new URL(value)
        } catch {
          throw new Error(`来源格式无效：${value}`)
        }
        if (
          (url.protocol !== "https:" &&
            !(
              url.protocol === "http:" &&
              ["localhost", "127.0.0.1"].includes(url.hostname)
            )) ||
          url.username ||
          url.password ||
          url.pathname !== "/" ||
          url.search ||
          url.hash ||
          value.includes("*")
        )
          throw new Error(
            `来源须为 HTTPS 域名与端口，不含路径：${value}（本机允许 HTTP）`,
          )
        return url.origin
      },
    )
    return { ...data, name: data.name.trim(), origins: [...new Set(values)] }
  }
  const runCheck = async () => {
    setChecking(true)
    setError("")
    setCheck(null)
    setCheckSnapshot(formSnapshot)
    try {
      setCheck(await internal("/integrations/check", payload()))
    } catch (e) {
      setError(e instanceof Error ? e.message : "检查失败")
    } finally {
      setChecking(false)
    }
  }
  const updateIdentity = async (body: {
    subject: string
    user_id: string
    enabled?: boolean
  }) => {
    if (dirty) {
      setError("请先保存应用配置，再修改身份映射。")
      return
    }
    setBusy(true)
    setError("")
    try {
      await internal(`/integrations/${form.id}/identities`, body, "PUT")
      const updated = await internal<ClientConfig[]>("/integrations/")
      setClients(updated)
      const current = updated.find((c) => c.id === form.id)
      if (current) await choose(current)
      setSubject("")
      setMappedUser("")
      setNotice("身份映射已更新，业务后端需重新获取令牌。")
    } catch (e) {
      setError(e instanceof Error ? e.message : "身份映射更新失败")
    } finally {
      setBusy(false)
    }
  }
  const save = async () => {
    if (secret) {
      setError("请先保存并隐藏当前一次性密钥，再修改应用配置。")
      return
    }
    setBusy(true)
    setError("")
    try {
      const { id, revision } = form
      const body = payload()
      const saved = await internal<ClientConfig & { client_secret?: string }>(
        id ? `/integrations/${id}` : "/integrations/",
        id ? { ...body, expected_revision: revision } : body,
        id ? "PUT" : "POST",
      )
      const { client_secret, ...publicConfig } = saved
      await choose(publicConfig).catch(() =>
        setError("应用已保存，但身份和审计加载失败，请稍后刷新。"),
      )
      setSecret(client_secret || "")
      setNotice(
        id
          ? "应用配置已保存，请让业务后端重新获取令牌。"
          : "应用创建成功，请立即保存下方密钥，并运行接入检查。",
      )
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存失败")
    } finally {
      setBusy(false)
    }
  }
  if (!user) return <p>正在验证管理权限…</p>
  if (!user.is_superuser)
    return <p role="alert">仅管理员可以管理外部系统接入。</p>
  const eligible = users.filter(
    (u) =>
      u.is_active && !u.is_superuser && !u.email.endsWith("@internal.invalid"),
  )
  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-2xl font-semibold">外部系统接入</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          登记应用，配置权限上限与嵌入来源。应用凭证仅供业务系统后端保管。
        </p>
      </header>
      <ol className="grid gap-3 text-sm sm:grid-cols-3">
        {[
          "1 · 准备普通用户、已发布主题与查询授权",
          "2 · 登记应用，保存后端凭证",
          "3 · 检查配置，复制示例进行联调",
        ].map((step) => (
          <li key={step} className="rounded-xl border bg-card p-4">
            {step}
          </li>
        ))}
      </ol>
      {notice && (
        <p role="status" className="rounded-lg bg-muted p-3 text-sm">
          {notice}
        </p>
      )}
      {error && (
        <p role="alert" className="text-destructive">
          {error}
        </p>
      )}
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className="rounded border px-3 py-2"
          onClick={() => {
            if (!canLeave()) return
            ++selection.current
            setForm(initial)
            setBaseline(JSON.stringify(initial))
            setOrigins("")
            setSecret("")
            setIdentities([])
            setAudit([])
            setCheck(null)
            setError("")
            setNotice("")
          }}
          disabled={busy || checking}
        >
          新应用
        </button>
        <input
          aria-label="搜索接入应用"
          placeholder="搜索接入应用…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="rounded border bg-background px-3 py-2 text-sm"
        />
        {clients
          .filter((c) => c.name.toLowerCase().includes(search.toLowerCase()))
          .map((c) => (
            <button
              type="button"
              key={c.id}
              disabled={busy || checking}
              aria-pressed={form.id === c.id}
              className={`rounded border px-3 py-2 ${form.id === c.id ? "border-primary bg-primary/10" : ""}`}
              onClick={() => {
                if (canLeave()) void choose(c).catch((e) => setError(e.message))
              }}
            >
              {c.name} · {c.enabled ? "启用" : "停用"}
            </button>
          ))}
      </div>
      <ValidatedForm
        className="grid gap-4 rounded-xl border bg-card p-5 sm:grid-cols-2"
        onSubmit={(e) => {
          e.preventDefault()
          void save()
        }}
      >
        <fieldset
          disabled={busy || checking}
          className="col-span-full grid min-w-0 gap-4 sm:grid-cols-2"
        >
          <h2 className="font-semibold sm:col-span-2">
            {form.id ? "编辑应用" : "登记新应用"}
          </h2>
          {!eligible.length && (
            <p className="text-sm text-amber-700 sm:col-span-2">
              暂无可选普通用户。请先在用户管理中创建并启用普通用户，然后配置主题成员和查询权限。
            </p>
          )}
          <label className="space-y-2 text-sm">
            应用名称
            <input
              required
              maxLength={80}
              className="block w-full rounded border bg-background p-2"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </label>
          <label className="space-y-2 text-sm">
            权限上限用户
            <select
              required
              disabled={Boolean(form.id)}
              className="block w-full rounded border bg-background p-2"
              value={form.ceiling_user_id}
              onChange={(e) =>
                setForm({ ...form, ceiling_user_id: e.target.value })
              }
            >
              <option value="">选择已配置主题查询权限的普通用户</option>
              {eligible.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.email}
                </option>
              ))}
            </select>
          </label>
          <fieldset className="space-y-2 rounded border p-3">
            <legend className="text-sm">开放主题</legend>
            {!topics.length && (
              <p className="text-sm text-muted-foreground">
                暂无主题，请先到业务主题中创建并发布主题。
              </p>
            )}
            {topics.map((t) => (
              <label key={t.id} className="flex gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.topic_ids.includes(t.id)}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      topic_ids: e.target.checked
                        ? [...form.topic_ids, t.id]
                        : form.topic_ids.filter((id) => id !== t.id),
                    })
                  }
                />
                {t.name}
              </label>
            ))}
          </fieldset>
          <fieldset className="space-y-2 rounded border p-3">
            <legend className="text-sm">开放能力</legend>
            {Object.entries({
              query: "指标查询",
              ask: "自然语言问数",
              explore: "自由探索",
              analysis: "结果分析",
              embed: "嵌入界面",
            }).map(([id, label]) => (
              <label key={id} className="flex gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.scopes.includes(id)}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      scopes: e.target.checked
                        ? [...form.scopes, id]
                        : form.scopes.filter((s) => s !== id),
                    })
                  }
                />
                {label}
              </label>
            ))}
          </fieldset>
          <label className="space-y-2 text-sm sm:col-span-2">
            允许嵌入的来源（每行一个完整源）
            <span className="block text-xs text-muted-foreground">
              例如 https://erp.example.com 或
              http://localhost:3000。支持多行、逗号分隔，末尾斜线自动整理。纯
              API 接入可留空。
            </span>
            <textarea
              className="resize-none block min-h-20 w-full rounded border bg-background p-2"
              placeholder="https://erp.example.com"
              value={origins}
              onChange={(e) => setOrigins(e.target.value)}
            />
          </label>
          {(
            [
              ["max_pending", "最多在途任务"],
              ["requests_per_minute", "每分钟请求额度"],
              ["model_calls_per_day", "24 小时模型调用额度"],
            ] as const
          ).map(([key, label]) => (
            <label key={key} className="text-sm">
              {label}
              <input
                type="number"
                required
                min={
                  key === "model_calls_per_day"
                    ? 0
                    : key === "requests_per_minute"
                      ? 10
                      : 1
                }
                max={
                  key === "model_calls_per_day"
                    ? 10000
                    : key === "requests_per_minute"
                      ? 600
                      : 20
                }
                step={1}
                className="mt-2 block w-full rounded border bg-background p-2"
                value={form[key]}
                onChange={(e) =>
                  setForm({ ...form, [key]: Number(e.target.value) })
                }
              />
            </label>
          ))}
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={form.enabled}
              onChange={(e) => setForm({ ...form, enabled: e.target.checked })}
            />
            启用此应用
          </label>
          <details className="space-y-3 sm:col-span-2">
            <summary>代表用户调用：可信身份签发配置</summary>
            <input
              aria-label="身份签发方"
              className="w-full rounded border bg-background p-2"
              placeholder="issuer"
              value={form.assertion_issuer}
              onChange={(e) =>
                setForm({ ...form, assertion_issuer: e.target.value })
              }
            />
            <textarea
              aria-label="身份签名公钥"
              className="resize-none min-h-32 w-full rounded border bg-background p-2 font-mono text-xs"
              placeholder="RSA PUBLIC KEY / PUBLIC KEY PEM"
              value={form.assertion_public_key}
              onChange={(e) =>
                setForm({ ...form, assertion_public_key: e.target.value })
              }
            />
          </details>
          <button
            disabled={busy || checking}
            type="submit"
            className="rounded-lg bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50"
          >
            {busy ? "正在保存…" : "保存应用"}
          </button>
          <button
            type="button"
            disabled={busy || checking}
            onClick={() => void runCheck()}
            className="rounded-lg border px-4 py-2"
          >
            {checking ? "正在检查…" : "检查接入配置"}
          </button>
        </fieldset>
      </ValidatedForm>
      {check && checkSnapshot === formSnapshot && (
        <section
          aria-label="接入检查结果"
          className="space-y-2 rounded-xl border p-5"
          role="status"
        >
          <h2 className="font-semibold">
            {check.ok ? "配置检查通过" : "接入配置需要处理"}
          </h2>
          <p className="text-xs text-muted-foreground">
            检查当前表单的主题发布和权限配置，不执行 SQL
            或调用模型。运行时仍需验证数据源、模型和 Worker。
          </p>
          {check.topics.map((item) => (
            <p key={item.topic_id} className="text-sm">
              {item.ok ? "✓" : "!"}{" "}
              {item.name ||
                topics.find((t) => t.id === item.topic_id)?.name ||
                item.topic_id}
              ：{item.message}
            </p>
          ))}
          {check.warnings.map((warning) => (
            <p key={warning} className="text-sm text-amber-700">
              {warning}
            </p>
          ))}
        </section>
      )}
      {form.id && (
        <section className="space-y-3 rounded-xl border p-5">
          <p className="break-all text-sm">
            应用 ID：{form.id} · 配置版本：{form.revision}
          </p>
          <p className="text-sm">
            配置变更会使已有令牌和查询授权快照失效。密钥轮换立即作废旧密钥。
          </p>
          <button
            type="button"
            disabled={busy || checking}
            className="rounded border px-3 py-2 text-sm"
            onClick={() => {
              if (dirty) {
                setError("请先保存应用配置，再轮换密钥。")
                return
              }
              if (
                !window.confirm(
                  "轮换后旧密钥、令牌和查询授权快照立即失效。确认业务系统已准备更新凭证？",
                )
              )
                return
              setBusy(true)
              void internal<{ client_secret: string; revision: number }>(
                `/integrations/${form.id}/rotate-secret`,
                {},
              )
                .then(async (data) => {
                  setSecret(data.client_secret)
                  setForm({ ...form, revision: data.revision })
                  setBaseline(
                    JSON.stringify({ ...form, revision: data.revision }),
                  )
                  await load()
                })
                .catch((e) => setError(e.message))
                .finally(() => setBusy(false))
            }}
          >
            轮换应用密钥
          </button>
          {secret && (
            <div className="rounded border border-amber-500 p-3">
              <p className="text-sm">请立即保存密钥，之后不再回显。</p>
              <code className="block break-all select-all text-sm">
                {secret}
              </code>
              <button
                type="button"
                className="mr-4 mt-2 text-sm underline"
                onClick={async () => {
                  try {
                    await navigator.clipboard.writeText(secret)
                    setNotice("密钥已复制，请保存到业务后端。")
                  } catch {
                    setError("无法访问剪贴板，请手动选中密钥复制。")
                  }
                }}
              >
                复制密钥
              </button>
              <button
                type="button"
                className="mt-2 text-sm underline"
                onClick={() => setSecret("")}
              >
                已保存，隐藏密钥
              </button>
            </div>
          )}
          <a
            className="block text-sm underline"
            href="/api/integration/v1/openapi.json"
            target="_blank"
            rel="noreferrer"
          >
            查看对外 API 契约
          </a>
        </section>
      )}
      {form.id && (
        <IntegrationGuide
          client={clients.find((c) => c.id === form.id) || form}
          onNotice={setNotice}
        />
      )}
      {form.id && (
        <section className="space-y-3 rounded-xl border p-5">
          <h2 className="font-semibold">外部用户映射</h2>
          <p className="text-sm text-muted-foreground">
            固定应用调用使用
            $app。个人问数需登记外部主体，并提供经配置公钥验证的短期身份声明。
          </p>
          {identities.map((i) => (
            <div key={i.subject} className="flex flex-wrap gap-3 text-sm">
              <span>
                {i.subject} →{" "}
                {users.find((u) => u.id === i.user_id)?.email || i.user_id} ·{" "}
                {i.enabled ? "启用" : "停用"}
              </span>
              {i.subject !== "$app" && (
                <button
                  type="button"
                  disabled={busy || checking || Boolean(secret)}
                  className="underline"
                  onClick={() =>
                    void updateIdentity({
                      subject: i.subject,
                      user_id: i.user_id,
                      enabled: !i.enabled,
                    })
                  }
                >
                  {i.enabled ? "停用" : "启用"}
                </button>
              )}
            </div>
          ))}
          <div className="flex flex-wrap gap-2">
            <input
              aria-label="外部用户标识"
              className="rounded border bg-background p-2 text-sm"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="外部 subject"
            />
            <select
              aria-label="映射内部用户"
              className="rounded border bg-background p-2 text-sm"
              value={mappedUser}
              onChange={(e) => setMappedUser(e.target.value)}
            >
              <option value="">选择内部用户</option>
              {eligible.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.email}
                </option>
              ))}
            </select>
            <button
              type="button"
              disabled={
                busy ||
                checking ||
                Boolean(secret) ||
                !subject.trim() ||
                subject.trim() === "$app" ||
                !mappedUser
              }
              className="rounded border px-3 py-2 text-sm"
              onClick={() =>
                void updateIdentity({
                  subject: subject.trim(),
                  user_id: mappedUser,
                })
              }
            >
              登记映射
            </button>
          </div>
          {secret && (
            <p className="text-sm text-muted-foreground">
              请先保存并隐藏一次性密钥，再管理身份映射。
            </p>
          )}
          <details>
            <summary>最近审计</summary>
            <pre className="max-h-80 overflow-auto text-xs">
              {JSON.stringify(audit, null, 2)}
            </pre>
          </details>
        </section>
      )}
    </div>
  )
}
