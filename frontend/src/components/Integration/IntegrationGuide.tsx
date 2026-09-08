import { useState } from "react"

type Props = {
  client: { id?: string; topic_ids: string[]; scopes: string[] }
  onNotice: (message: string) => void
}

export function IntegrationGuide({ client, onNotice }: Props) {
  const [tab, setTab] = useState<"api" | "embed">("api")
  const base = window.location.origin
  const api = `# 在业务后端运行；先安装 httpx，并设置 LIGHTSQL_CLIENT_SECRET 环境变量。
# 此示例仅验证认证与可见主题，不调用模型、不执行查询。
import os
import httpx

base = ${JSON.stringify(`${base}/api/integration/v1`)}
with httpx.Client(timeout=30) as client:
    response = client.post(base + "/token", json={
        "client_id": ${JSON.stringify(client.id)},
        "client_secret": os.environ["LIGHTSQL_CLIENT_SECRET"],
    })
    response.raise_for_status()
    headers = {"Authorization": "Bearer " + response.json()["access_token"]}
    response = client.get(base + "/topics", headers=headers)
    response.raise_for_status()
    print(response.json())
    # 提交查询：POST /queries，携带唯一 Idempotency-Key。
    # 指标 ID 可从 GET /topics/{topic_id}/catalog 获取。
    # 获得 task_id 后轮询 /tasks/{task_id}，成功后读取 /result。
`
  const embed = `<!-- 放到业务系统页面；票据接口需由业务后端实现 -->
<div id="lightsql" style="height:720px"></div>
<script src="${base}/lightsql-embed.js"></script>
<script>
const widget = LightSQL.mount({
  container: document.getElementById("lightsql"),
  baseUrl: ${JSON.stringify(base)},
  clientId: ${JSON.stringify(client.id)},
  topicId: ${JSON.stringify(client.topic_ids[0] || "")},
  title: "智能问数",
  async getTicket(context) {
    const response = await fetch("/api/lightsql/ticket", {
      method: "POST",
      credentials: "same-origin",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(context),
    });
    if (!response.ok) throw new Error("票据获取失败，请检查登录状态和后端日志");
    return response.json();
  },
  onError: (error) => console.error(error.message),
});
// 页面卸载或用户退出时，调用 widget.destroy()，并在业务后端撤销会话。
</script>`
  const copy = async (value: string) => {
    try {
      await navigator.clipboard.writeText(value)
      onNotice("已复制。示例使用最近保存的配置；请在目标系统配置密钥和接口。")
    } catch {
      onNotice("浏览器不允许访问剪贴板，请选中内容后手动复制。")
    }
  }
  return (
    <section className="min-w-0 space-y-4 rounded-xl border bg-card p-5">
      <h2 className="font-semibold">接入示例</h2>
      <p className="text-sm text-muted-foreground">
        基于最近保存的应用配置生成。当前地址为 {base}
        ，部署后请使用业务系统可访问的 LightSQL HTTPS 地址。
      </p>
      <div className="flex flex-wrap items-center gap-2 text-sm">
        <code className="break-all">{client.id}</code>
        <button
          type="button"
          className="rounded border px-3 py-1"
          onClick={() => void copy(client.id || "")}
        >
          复制应用 ID
        </button>
        <a
          className="underline"
          href="/api/integration/v1/openapi.json"
          target="_blank"
          rel="noreferrer"
        >
          API 契约
        </a>
      </div>
      <div className="flex gap-2">
        <button
          type="button"
          aria-pressed={tab === "api"}
          onClick={() => setTab("api")}
          className={`rounded border px-3 py-2 text-sm ${tab === "api" ? "bg-primary/10" : ""}`}
        >
          后端 API 自检
        </button>
        <button
          type="button"
          aria-pressed={tab === "embed"}
          onClick={() => setTab("embed")}
          className={`rounded border px-3 py-2 text-sm ${tab === "embed" ? "bg-primary/10" : ""}`}
        >
          嵌入页面
        </button>
        <button
          type="button"
          className="ml-auto text-sm underline"
          onClick={() => void copy(tab === "api" ? api : embed)}
        >
          复制代码
        </button>
      </div>
      {tab === "embed" && (
        <div className="space-y-2 text-sm text-muted-foreground">
          {!client.scopes.includes("embed") && (
            <p className="text-amber-700">
              此应用尚未开启嵌入界面能力，请修改并保存。
            </p>
          )}
          <p>
            先将宿主来源加入白名单。业务后端的 /api/lightsql/ticket
            应验证宿主登录与 CSRF，使用应用凭证换取令牌，再调用 /embed/tickets
            返回票据。个人接入需使用服务端签发的
            subject_assertion；不要把应用密钥放进这段页面代码。
          </p>
        </div>
      )}
      <pre className="max-h-96 overflow-auto rounded-lg bg-muted p-4 text-xs">
        <code>{tab === "api" ? api : embed}</code>
      </pre>
      <details className="text-sm">
        <summary className="cursor-pointer">联调排错速查</summary>
        <ul className="mt-3 space-y-2 text-muted-foreground">
          <li>
            401：检查应用 ID、密钥和令牌有效期；修改配置或轮换密钥后重新取令牌。
          </li>
          <li>
            403 /
            主题列表为空：检查应用能力、主题成员、已发布语义版本及查询授权；个人身份取双方权限交集。
          </li>
          <li>
            409：刷新应用配置；同一幂等键不能提交不同请求，追问需使用最新会话版本。
          </li>
          <li>
            429：检查在途任务、每分钟额度和 24 小时模型额度，降低轮询频率。
          </li>
          <li>
            任务持续 queued / querying：检查 integration-worker 和 query-worker
            的进程与日志。
          </li>
          <li>
            嵌入授权失败：核对协议、域名和端口；localhost 与 127.0.0.1
            是不同来源。票据须在 60 秒内使用且只能消费一次。
          </li>
        </ul>
      </details>
    </section>
  )
}
