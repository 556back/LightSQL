import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Check, Cpu, Plus } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"
import {
  AssistantService,
  type GatewayInput,
  type GatewayInputWritable,
  type GatewayPublic,
} from "@/client"
import { control, errorMessage, Field } from "@/components/Semantic/shared"
import { Button } from "@/components/ui/button"
import { ValidatedForm } from "@/components/ui/validated-form"

type WritableGateway = GatewayInputWritable
const blank: WritableGateway = {
  name: "",
  provider: "zhipu",
  base_url: "https://open.bigmodel.cn/api/paas/v4",
  model: "",
  api_key: "",
  timeout_seconds: 45,
  max_tokens: 4096,
  json_mode: true,
  thinking: "default",
  expected_revision: 0,
}
const labels = {
  zhipu: "智谱",
  deepseek: "DeepSeek",
  qwen: "千问",
  custom: "自定义兼容接口",
}

export function ModelSettings() {
  const qc = useQueryClient()
  const [editing, setEditing] = useState<GatewayPublic | null>(null)
  const [showForm, setShowForm] = useState(false)
  const configs = useQuery({
    queryKey: ["model-gateways"],
    queryFn: async () => (await AssistantService.listGateways()).data,
  })
  const refresh = () => {
    qc.invalidateQueries({ queryKey: ["model-gateways"] })
    qc.invalidateQueries({ queryKey: ["model-status"] })
  }
  const action = useMutation({
    mutationFn: async ({
      config,
      kind,
    }: {
      config: GatewayPublic
      kind: "activate" | "test"
    }) => {
      const options = {
        path: { gateway_id: config.id },
        body: { expected_revision: config.revision },
      }
      if (kind === "activate") {
        await AssistantService.activateGateway(options)
        toast.success("已切换当前模型")
        return
      }
      const { data } = await AssistantService.testGateway(options)
      if (data.success) toast.success(`${data.message} · ${data.elapsed_ms} ms`)
      else toast.error(data.message)
    },
    onSuccess: refresh,
  })
  const deactivate = useMutation({
    mutationFn: () => AssistantService.deactivateGateway(),
    onSuccess: refresh,
  })
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs tracking-widest text-muted-foreground">
            系统管理
          </p>
          <h1 className="mt-2 text-2xl font-semibold">模型设置</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            配置智谱、DeepSeek、千问或企业批准的兼容接口。模型名称按服务账号可用范围填写。
          </p>
        </div>
        <Button
          onClick={() => {
            setEditing(null)
            setShowForm(true)
          }}
        >
          <Plus className="size-4" />
          添加模型配置
        </Button>
      </div>
      <div className="rounded-xl border bg-card p-5 text-sm leading-6">
        <p>
          每次问答使用当前启用配置。测试连接只发送固定测试内容，不包含业务语义和查询结果。
        </p>
        <p className="text-muted-foreground">
          密钥加密保存且不回显；编辑时留空保留原密钥。修改服务地址或厂商时需重新填写密钥。
        </p>
      </div>
      {(configs.isError || action.isError || deactivate.isError) && (
        <p role="alert" className="text-destructive">
          {errorMessage(configs.error || action.error || deactivate.error)}
        </p>
      )}
      {showForm && (
        <GatewayForm
          key={editing?.id || "new"}
          config={editing}
          onClose={() => setShowForm(false)}
          onSaved={() => {
            setShowForm(false)
            refresh()
          }}
        />
      )}
      {configs.isPending ? (
        <p>正在加载模型配置…</p>
      ) : configs.data?.length === 0 ? (
        <div className="rounded-xl border border-dashed p-12 text-center">
          <Cpu className="mx-auto mb-4 size-8 text-muted-foreground" />
          <h2 className="font-medium">尚未配置模型</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            添加服务地址、模型名称和 API Key，测试通过后启用。
          </p>
        </div>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {configs.data?.map((config) => (
            <section
              key={config.id}
              className="min-w-0 rounded-xl border bg-card p-5"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h2 className="break-words font-semibold">{config.name}</h2>
                  <p className="mt-1 break-all text-sm text-muted-foreground">
                    {labels[config.provider as keyof typeof labels]} ·{" "}
                    {config.model}
                  </p>
                </div>
                {config.active && (
                  <span className="flex shrink-0 items-center gap-1 rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-700">
                    <Check className="size-3" />
                    当前启用
                  </span>
                )}
              </div>
              <p className="mt-4 break-all text-xs text-muted-foreground">
                {config.base_url}
              </p>
              <p className="mt-2 text-xs text-muted-foreground">
                {config.timeout_seconds} 秒超时 · {config.max_tokens} tokens ·{" "}
                {config.json_mode ? "JSON 模式" : "提示词 JSON"} · 密钥已保存
              </p>
              <div className="mt-5 flex flex-wrap gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setEditing(config)
                    setShowForm(true)
                  }}
                >
                  编辑
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={action.isPending}
                  onClick={() => action.mutate({ config, kind: "test" })}
                >
                  测试连接
                </Button>
                {!config.active && (
                  <Button
                    size="sm"
                    disabled={action.isPending}
                    onClick={() => action.mutate({ config, kind: "activate" })}
                  >
                    启用此配置
                  </Button>
                )}
                {config.active && (
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={deactivate.isPending}
                    onClick={() => deactivate.mutate()}
                  >
                    停用模型调用
                  </Button>
                )}
              </div>
            </section>
          ))}
        </div>
      )}
      {action.isPending && (
        <p role="status" className="text-sm text-muted-foreground">
          正在处理，请稍候…
        </p>
      )}
    </div>
  )
}

function GatewayForm({
  config,
  onClose,
  onSaved,
}: {
  config: GatewayPublic | null
  onClose: () => void
  onSaved: () => void
}) {
  const [form, setForm] = useState<WritableGateway>(
    config
      ? {
          name: config.name,
          provider: config.provider as GatewayInput["provider"],
          base_url: config.base_url,
          model: config.model,
          api_key: "",
          timeout_seconds: config.timeout_seconds,
          max_tokens: config.max_tokens,
          json_mode: config.json_mode,
          thinking: config.thinking as GatewayInput["thinking"],
          expected_revision: config.revision,
        }
      : blank,
  )
  const presets = useQuery({
    queryKey: ["model-presets"],
    queryFn: async () => (await AssistantService.gatewayPresets()).data,
  })
  const patch = (value: Partial<WritableGateway>) =>
    setForm((current) => ({ ...current, ...value }))
  const save = useMutation({
    mutationFn: async () => {
      const body = form
      if (config)
        return AssistantService.updateGateway({
          path: { gateway_id: config.id },
          body,
        })
      return AssistantService.createGateway({ body })
    },
    onSuccess: () => {
      setForm(blank)
      toast.success("模型配置已保存")
      onSaved()
    },
  })
  return (
    <ValidatedForm
      onSubmit={(e) => {
        e.preventDefault()
        save.mutate()
      }}
      className="space-y-5 rounded-xl border bg-card p-5"
    >
      <h2 className="font-semibold">
        {config ? "编辑模型配置" : "添加模型配置"}
      </h2>
      <div className="grid gap-4 md:grid-cols-2">
        <Field label="配置名称">
          <input
            aria-label="配置名称"
            className={control}
            required
            maxLength={80}
            value={form.name}
            onChange={(e) => patch({ name: e.target.value })}
            placeholder="例如：经营分析主模型"
          />
        </Field>
        <Field label="模型厂商">
          <select
            aria-label="模型厂商"
            className={control}
            value={form.provider}
            onChange={(e) => {
              const provider = e.target.value as GatewayInput["provider"]
              patch({
                provider,
                base_url:
                  presets.data?.find((p) => p.provider === provider)
                    ?.base_url || "",
                api_key: "",
              })
            }}
          >
            {Object.entries(labels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </Field>
        <Field label="服务基础地址">
          <input
            aria-label="服务基础地址"
            className={control}
            type="url"
            required
            value={form.base_url}
            onChange={(e) => patch({ base_url: e.target.value })}
            list="gateway-endpoints"
            placeholder="https://model.example.com/v1"
          />
          <datalist id="gateway-endpoints">
            {presets.data
              ?.filter((p) => p.provider === form.provider)
              .map((p) => (
                <option key={p.base_url} value={p.base_url}>
                  {p.label}
                </option>
              ))}
          </datalist>
        </Field>
        <Field label="模型名称">
          <input
            aria-label="模型名称"
            className={control}
            required
            maxLength={120}
            value={form.model}
            onChange={(e) => patch({ model: e.target.value })}
            placeholder="填写服务商提供的模型 ID"
          />
        </Field>
        <Field label={config ? "API Key（留空保留）" : "API Key"}>
          <input
            aria-label="API Key"
            className={control}
            type="password"
            autoComplete="new-password"
            required={!config}
            value={form.api_key || ""}
            onChange={(e) => patch({ api_key: e.target.value })}
          />
        </Field>
        <Field label="思考模式">
          <select
            aria-label="思考模式"
            className={control}
            value={form.thinking}
            onChange={(e) =>
              patch({ thinking: e.target.value as GatewayInput["thinking"] })
            }
          >
            <option value="default">遵循模型默认</option>
            <option value="disabled">关闭思考（模型需支持）</option>
            <option value="enabled">开启思考（模型需支持）</option>
          </select>
        </Field>
        <Field label="生成超时（秒）">
          <input
            aria-label="生成超时"
            className={control}
            type="number"
            required
            min={5}
            max={90}
            value={form.timeout_seconds}
            onChange={(e) => patch({ timeout_seconds: Number(e.target.value) })}
          />
        </Field>
        <Field label="最大输出 tokens">
          <input
            aria-label="最大输出 tokens"
            className={control}
            type="number"
            required
            min={256}
            max={16384}
            value={form.max_tokens}
            onChange={(e) => patch({ max_tokens: Number(e.target.value) })}
          />
        </Field>
      </div>
      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={form.json_mode}
          onChange={(e) => patch({ json_mode: e.target.checked })}
        />
        启用 JSON 输出模式
      </label>
      <p className="text-xs leading-5 text-muted-foreground">
        千问请核对地域与 API Key。基础地址不包含
        /chat/completions。自定义服务需由部署端配置允许地址。关闭 JSON
        模式后仍进行本地结构校验。
      </p>
      {save.isError && (
        <p role="alert" className="text-sm text-destructive">
          {errorMessage(save.error)}
        </p>
      )}
      <div className="flex gap-2">
        <Button type="submit" disabled={save.isPending}>
          {save.isPending ? "正在保存…" : "保存配置"}
        </Button>
        <Button type="button" variant="outline" onClick={onClose}>
          取消
        </Button>
      </div>
    </ValidatedForm>
  )
}
