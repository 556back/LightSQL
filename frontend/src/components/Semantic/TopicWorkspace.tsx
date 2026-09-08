import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Link, useBlocker, useNavigate } from "@tanstack/react-router"
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Download,
  FileClock,
  MessageSquare,
  Pencil,
  Plus,
  ShieldCheck,
  Trash2,
  Upload,
} from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"
import {
  CatalogService,
  type PublishedTopic,
  type TopicDetail,
  TopicsService,
  type UserPublic,
  UsersService,
  type ValidationReport,
} from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import useAuth from "@/hooks/useAuth"
import { type Entry, EntryEditor } from "./EntryEditor"
import {
  additiveLabels,
  aggregations,
  control,
  download,
  errorMessage,
  Field,
  type Group,
  groups,
  normalize,
  Status,
} from "./shared"

export function TopicWorkspace({ topicId }: { topicId: string }) {
  const { user } = useAuth()
  const admin = !!user?.is_superuser
  const query = useQuery({
    queryKey: ["topic", topicId, admin],
    queryFn: async () =>
      admin
        ? (await TopicsService.getTopic({ path: { topic_id: topicId } })).data
        : (
            await TopicsService.getPublishedTopic({
              path: { topic_id: topicId },
            })
          ).data,
    enabled: !!user,
    refetchOnWindowFocus: false,
  })
  if (query.isPending)
    return <p className="text-sm text-muted-foreground">正在加载主题…</p>
  if (query.isError)
    return (
      <div role="alert" className="space-y-4 rounded-xl border bg-card p-6">
        <p>{errorMessage(query.error)}</p>
        <Button variant="outline" onClick={() => query.refetch()}>
          重试
        </Button>
        <Link to="/topics" className="ml-4 text-sm text-primary">
          返回主题列表
        </Link>
      </div>
    )
  return admin ? (
    <AdminWorkspace key={topicId} initial={query.data as TopicDetail} />
  ) : (
    <PublishedDictionary topic={query.data as PublishedTopic} />
  )
}

function PublishedDictionary({ topic }: { topic: PublishedTopic }) {
  const [search, setSearch] = useState("")
  const label = (id: string) =>
    topic.dimensions.find((d) => d.id === id)?.label ?? id
  const metrics = topic.metrics.filter((m) =>
    `${m.label} ${m.aliases.join(" ")} ${m.description}`.includes(search),
  )
  return (
    <div className="space-y-6">
      <Link
        className="inline-flex items-center gap-2 text-sm text-muted-foreground"
        to="/topics"
      >
        <ArrowLeft className="size-4" />
        业务主题
      </Link>
      <div>
        <p className="text-xs text-muted-foreground">
          指标目录 · 已发布 v{topic.version}
        </p>
        <h1 className="mt-2 text-2xl font-semibold">{topic.name}</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          {topic.description}
        </p>
        <p className="mt-3 text-xs text-muted-foreground">
          业务责任人：{topic.owner} · {topic.timezone}
        </p>
        <Button className="mt-4" asChild>
          <Link to="/ask" search={{ topic: topic.id }}>
            <MessageSquare className="size-4" />
            使用这个主题问数
          </Link>
        </Button>
      </div>
      <input
        aria-label="搜索指标"
        className={`${control} max-w-sm`}
        placeholder="搜索指标、别名或业务口径"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      <div className="grid gap-4 lg:grid-cols-2">
        {metrics.map((m) => (
          <article
            key={m.id}
            className="space-y-3 rounded-xl border bg-card p-5"
          >
            <div className="flex items-center justify-between gap-3">
              <h2 className="font-semibold">{m.label}</h2>
              <span className="text-xs text-muted-foreground">{m.unit}</span>
            </div>
            <p className="text-sm leading-6 text-muted-foreground">
              {m.description}
            </p>
            <p className="text-xs text-muted-foreground">
              {aggregations[m.aggregation]} · {additiveLabels[m.additivity]} ·
              时间归属：{m.time_dimension ? label(m.time_dimension) : "未指定"}
            </p>
            {!!m.aliases.length && (
              <p className="text-xs">别名：{m.aliases.join("、")}</p>
            )}
            <div className="flex flex-wrap gap-2">
              {m.allowed_dimensions.map((id) => (
                <span
                  key={id}
                  className="rounded-md bg-muted px-2 py-1 text-xs"
                >
                  {label(id)}
                </span>
              ))}
            </div>
          </article>
        ))}
      </div>
      {!metrics.length && (
        <p className="text-sm text-muted-foreground">没有匹配的指标。</p>
      )}
      <section className="rounded-xl border bg-card p-5">
        <h2 className="mb-4 font-medium">业务维度</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {topic.dimensions.map((d) => (
            <div key={d.id}>
              <p className="text-sm font-medium">{d.label}</p>
              <p className="mt-1 text-xs leading-5 text-muted-foreground">
                {d.description || d.aliases.join("、") || d.value_type}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

function AdminWorkspace({ initial }: { initial: TopicDetail }) {
  const cache = useQueryClient()
  const navigate = useNavigate()
  const [server, setServer] = useState(initial)
  const [definition, setDefinition] = useState(() =>
    normalize(initial.definition),
  )
  const [meta, setMeta] = useState({
    name: initial.name,
    description: initial.description,
    enabled: initial.enabled,
  })
  const [members, setMembers] = useState(initial.member_ids)
  const [active, setActive] = useState<
    Group | "settings" | "members" | "versions"
  >(initial.definition.models?.length ? "metrics" : "models")
  const [advanced, setAdvanced] = useState(false)
  const [search, setSearch] = useState("")
  const [editor, setEditor] = useState<{ group: Group; entry?: Entry } | null>(
    null,
  )
  const [removing, setRemoving] = useState<{
    group: Group
    entry: Entry
  } | null>(null)
  const [report, setReport] = useState<ValidationReport | null>(null)
  const [modal, setModal] = useState<"publish" | "import" | "delete" | null>(
    null,
  )
  const [text, setText] = useState("")
  const [restore, setRestore] = useState<number | null>(null)
  const path = { topic_id: server.id }
  const dirty =
    JSON.stringify(definition) !==
      JSON.stringify(normalize(server.definition)) ||
    meta.name !== server.name ||
    meta.description !== server.description ||
    meta.enabled !== server.enabled
  const memberDirty =
    [...members].sort().join() !== [...server.member_ids].sort().join()
  const blocker = useBlocker({
    shouldBlockFn: () => dirty || memberDirty,
    enableBeforeUnload: dirty || memberDirty,
    withResolver: true,
  })
  const catalog = useQuery({
    queryKey: ["topic-catalog", server.source_id],
    queryFn: async () =>
      (
        await CatalogService.getCatalog({
          path: { source_id: server.source_id! },
        })
      ).data,
  })
  const releases = useQuery({
    queryKey: ["topic-releases", server.id],
    queryFn: async () => (await TopicsService.listReleases({ path })).data,
    enabled: active === "versions",
  })
  const users = useQuery({
    queryKey: ["topic-members-users"],
    queryFn: async () => {
      const result: UserPublic[] = []
      for (let skip = 0; ; skip += 100) {
        const page = (
          await UsersService.readUsers({ query: { skip, limit: 100 } })
        ).data
        result.push(...page.data)
        if (result.length >= page.count || !page.data.length) return result
      }
    },
    enabled: active === "members",
  })
  const accept = (next: TopicDetail, preserveMembers = false) => {
    setServer(next)
    setDefinition(normalize(next.definition))
    setMeta({
      name: next.name,
      description: next.description,
      enabled: next.enabled,
    })
    if (!preserveMembers) setMembers(next.member_ids)
    setReport(null)
    cache.setQueryData(["topic", server.id, true], next)
    cache.invalidateQueries({ queryKey: ["topics"] })
    cache.invalidateQueries({ queryKey: ["topic-releases", server.id] })
  }
  const operation = useMutation({
    mutationFn: async (fn: () => Promise<void>) => fn(),
    onError: (e) => toast.error(errorMessage(e)),
  })
  const run = (fn: () => Promise<void>) => operation.mutate(fn)
  const busy = operation.isPending
  const locked = busy || dirty || memberDirty
  const refresh = async () =>
    accept((await TopicsService.getTopic({ path })).data)
  const exportFile = async (format: "yaml" | "json", version = 0) => {
    if (!version && dirty) {
      download(
        `topic-${server.id}-working.json`,
        JSON.stringify(definition, null, 2),
      )
      toast.success("已导出当前未保存的语义配置（JSON）")
      return
    }
    const data = (
      await TopicsService.exportDefinition({ path, query: { format, version } })
    ).data
    download(data.filename, data.content)
  }
  const rowSummary = (group: Group, row: Entry) => {
    if (group === "metrics" && "aggregation" in row)
      return `${aggregations[row.aggregation]} · ${row.unit} · ${additiveLabels[row.additivity ?? "additive"]}`
    if (group === "dimensions" && "column" in row)
      return `${row.model_id}.${row.column} · ${"value_type" in row ? row.value_type : ""}`
    if (group === "models" && "relation" in row)
      return `${row.relation.schema_name}.${row.relation.name} · ${row.grain}`
    if (group === "filters" && "operator" in row)
      return `${row.dimension_id} · ${row.operator} · ${(row.values ?? []).join(" / ") || "空值条件"}`
    if (group === "relations" && "from_model" in row)
      return `${row.from_model} → ${row.to_model} · ${row.from_columns.join(" + ")} = ${row.to_columns.join(" + ")}`
    if (group === "entities" && "value" in row)
      return `${row.dimension_id} · ${(row.aliases ?? []).join("、") || "暂无别名"} · 本地编码`
    return ""
  }
  const group = groups.find((g) => g.key === active)
  return (
    <div className="space-y-6">
      <Link
        to="/topics"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground"
      >
        <ArrowLeft className="size-4" />
        业务主题
      </Link>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="mb-2 flex items-center gap-3">
            <span className="text-xs text-muted-foreground">主题配置</span>
            <Status value={server.availability} />
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">
            {server.name}
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            {server.source_name} ·{" "}
            {server.current_version
              ? `发布版本 v${server.current_version}`
              : "尚未发布"}{" "}
            · 草稿修订 {server.revision}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {server.availability === "ready" && (
            <Button variant="outline" asChild>
              <Link to="/ask" search={{ topic: server.id }}>
                <MessageSquare className="size-4" />
                开始问数
              </Link>
            </Button>
          )}
          <Button
            variant="outline"
            disabled={locked}
            onClick={() =>
              run(async () => {
                setReport(
                  (
                    await TopicsService.validateDraft({
                      path,
                      body: { expected_revision: server.revision },
                    })
                  ).data,
                )
              })
            }
          >
            <ShieldCheck className="size-4" />
            校验草稿
          </Button>
          <Button
            variant="outline"
            disabled={busy || !dirty}
            onClick={() =>
              run(async () => {
                accept(
                  (
                    await TopicsService.saveDraft({
                      path,
                      body: {
                        ...meta,
                        definition,
                        expected_revision: server.revision,
                      },
                    })
                  ).data,
                )
                toast.success("草稿已保存")
              })
            }
          >
            保存草稿
          </Button>
          <Button
            disabled={locked || !server.enabled}
            onClick={() => {
              operation.reset()
              setModal("publish")
              setText("")
            }}
          >
            发布版本
          </Button>
        </div>
      </div>
      {operation.error && !modal && restore === null && (
        <p
          role="alert"
          className="rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive"
        >
          {errorMessage(operation.error)}
        </p>
      )}
      {(dirty || memberDirty) && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-amber-500/25 bg-amber-500/5 px-4 py-3 text-sm">
          <span>
            {dirty
              ? "工作区有未保存的修改，请先保存草稿再校验或发布。"
              : "成员权限有未保存的修改，请先保存授权。"}
          </span>
          {dirty && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => run(() => exportFile("json"))}
            >
              导出工作区备份
            </Button>
          )}
        </div>
      )}
      {server.availability === "needs_review" && (
        <p className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-4 text-sm">
          已发布版本的目录绑定发生变化，业务目录暂不可用。请检查字段和范围，校验后重新发布。
        </p>
      )}
      {report && (
        <section
          aria-label="校验报告"
          className={`rounded-xl border p-4 ${report.valid ? "border-emerald-500/30 bg-emerald-500/5" : "border-amber-500/30 bg-amber-500/5"}`}
        >
          <h2 className="flex items-center gap-2 text-sm font-medium">
            <CheckCircle2 className="size-4" />
            {report.valid ? "校验通过" : "校验未通过"} · 修订{" "}
            {report.draft_revision} / 目录 v{report.catalog_version}
            {dirty ? "（工作区已修改，请保存后重验）" : ""}
          </h2>
          <p className="mt-2 text-xs text-muted-foreground">
            发布时会基于最新目录再次校验。结构检查不执行业务查询。
          </p>
          {report.issues.length > 0 && (
            <ul className="mt-3 max-h-64 space-y-2 overflow-y-auto">
              {report.issues.map((i, index) => (
                <li key={`${i.path}-${i.code}-${index}`} className="text-sm">
                  <span className="mr-2 text-xs font-medium">
                    {i.severity === "error" ? "需修正" : "提示"}
                  </span>
                  <code className="mr-2 text-xs">{i.path}</code>
                  {i.message}
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
      <section
        aria-label="主题配置引导"
        className="overflow-hidden rounded-xl border bg-card"
      >
        <div className="flex flex-wrap items-center justify-between gap-2 border-b px-5 py-4">
          <div>
            <h2 className="text-sm font-semibold">
              把数据整理成可提问的业务主题
            </h2>
            <p className="mt-1 text-xs leading-5 text-muted-foreground">
              先选表，再按需添加维度和指标。保存草稿后检查并发布，即可开始问数。
            </p>
          </div>
          <span className="text-xs text-muted-foreground">
            维度和指标可按分析需要补充
          </span>
        </div>
        <div className="grid gap-2 p-3 sm:grid-cols-3">
          {(
            [
              {
                key: "models",
                title: "选择数据表",
                hint: "例如：订单表、客户表",
              },
              {
                key: "dimensions",
                title: "添加分析维度",
                hint: "例如：日期、地区、客户",
              },
              {
                key: "metrics",
                title: "定义统计指标",
                hint: "例如：销售额、订单数",
              },
            ] as const
          ).map((step, index) => (
            <button
              type="button"
              key={step.key}
              aria-pressed={active === step.key}
              onClick={() => {
                setActive(step.key)
                setSearch("")
              }}
              className={`flex items-start gap-3 rounded-lg p-3 text-left transition-colors ${active === step.key ? "bg-primary/8" : "hover:bg-muted/60"}`}
            >
              <span
                className={`flex size-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${active === step.key ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}
              >
                {index + 1}
              </span>
              <span>
                <span className="block text-sm font-medium">
                  {step.title}
                  <span className="ml-2 text-xs font-normal text-muted-foreground">
                    {definition[step.key].length} 项
                  </span>
                </span>
                <span className="mt-1 block text-xs text-muted-foreground">
                  {step.hint}
                </span>
              </span>
            </button>
          ))}
        </div>
      </section>
      <nav
        aria-label="主题配置分类"
        className="flex flex-wrap items-center gap-1 border-b pb-2"
      >
        {[
          ...groups
            .filter(
              (g) =>
                advanced &&
                !["models", "dimensions", "metrics"].includes(g.key),
            )
            .map((g) => ({
              key: g.key,
              label: `${g.label} ${definition[g.key].length}`,
            })),
          { key: "settings", label: "主题设置" },
          { key: "members", label: "成员权限" },
          { key: "versions", label: "版本历史" },
        ].map((tab) => (
          <button
            type="button"
            aria-current={active === tab.key ? "page" : undefined}
            key={tab.key}
            onClick={() => {
              setActive(tab.key as typeof active)
              setSearch("")
            }}
            className={`shrink-0 rounded-lg px-3 py-2 text-sm ${active === tab.key ? "bg-primary/10 font-medium text-primary" : "text-muted-foreground hover:bg-muted"}`}
          >
            {tab.label}
          </button>
        ))}
        <Button
          variant="ghost"
          size="sm"
          className="sm:ml-auto"
          aria-expanded={advanced}
          onClick={() => setAdvanced(!advanced)}
        >
          {advanced ? "收起高级配置" : "高级配置：关联、条件与别名"}
        </Button>
      </nav>
      {group && (
        <section className="space-y-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="font-semibold">
                {group.label}
                <span className="ml-2 text-sm font-normal text-muted-foreground">
                  {definition[group.key].length}
                </span>
              </h2>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
                {group.hint}
              </p>
            </div>
            <Button
              variant="outline"
              disabled={busy}
              onClick={() => setEditor({ group: group.key })}
            >
              <Plus className="size-4" />
              添加{group.label}
            </Button>
          </div>
          <input
            aria-label="搜索配置"
            className={`${control} max-w-sm`}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="搜索业务名称、标识或别名"
          />
          <div className="grid gap-3 xl:grid-cols-2">
            {definition[group.key]
              .filter((row) =>
                `${row.id} ${row.label} ${"aliases" in row ? row.aliases?.join(" ") : ""}`.includes(
                  search,
                ),
              )
              .map((row) => (
                <article
                  key={row.id}
                  className="flex min-w-0 items-start gap-3 rounded-xl border bg-card p-5 shadow-xs"
                >
                  <div className="min-w-0 flex-1">
                    <h3 className="font-medium">{row.label}</h3>
                    <p className="mt-1 break-all font-mono text-[11px] text-muted-foreground">
                      {row.id}
                    </p>
                    <p className="mt-3 break-words text-xs leading-5 text-muted-foreground">
                      {rowSummary(group.key, row)}
                    </p>
                    {"description" in row && (
                      <p className="mt-2 line-clamp-2 text-sm leading-6">
                        {row.description}
                      </p>
                    )}
                  </div>
                  <div className="flex shrink-0 flex-col">
                    <Button
                      size="icon"
                      variant="ghost"
                      aria-label={`编辑 ${row.label}`}
                      disabled={busy}
                      onClick={() =>
                        setEditor({ group: group.key, entry: row })
                      }
                    >
                      <Pencil className="size-4" />
                    </Button>
                    <Button
                      size="icon"
                      variant="ghost"
                      aria-label={`删除 ${row.label}`}
                      disabled={busy}
                      onClick={() =>
                        setRemoving({ group: group.key, entry: row })
                      }
                    >
                      <Trash2 className="size-4 text-muted-foreground" />
                    </Button>
                  </div>
                </article>
              ))}
          </div>
          {!definition[group.key].length && (
            <div className="rounded-xl border border-dashed py-12 text-center text-sm text-muted-foreground">
              尚未配置{group.label}。
              {group.key === "metrics"
                ? "例如添加「销售额」，选择订单金额字段并求和。"
                : "点击上方按钮开始配置。"}
            </div>
          )}
          {!!definition[group.key].length &&
            !definition[group.key].some((row) =>
              `${row.id} ${row.label} ${"aliases" in row ? row.aliases?.join(" ") : ""}`.includes(
                search,
              ),
            ) && (
              <p className="rounded-xl border border-dashed p-8 text-center text-sm text-muted-foreground">
                没有匹配的配置。
                <button
                  type="button"
                  className="ml-2 text-primary underline"
                  onClick={() => setSearch("")}
                >
                  清除搜索
                </button>
              </p>
            )}
          {group.key === "models" &&
            !catalog.isPending &&
            !catalog.isError &&
            !catalog.data?.tables.length && (
              <div className="rounded-lg bg-muted p-4 text-sm">
                还没有可选的数据表。
                <Link
                  to="/catalog"
                  search={{ source: server.source_id ?? undefined }}
                  className="ml-2 text-primary underline"
                >
                  前往数据表目录选择并同步
                </Link>
              </div>
            )}
          {(group.key === "models" || group.key === "dimensions") &&
            definition[group.key].length > 0 && (
              <Button
                variant="outline"
                onClick={() => {
                  setActive(group.key === "models" ? "dimensions" : "metrics")
                  setSearch("")
                }}
              >
                下一步：
                {group.key === "models" ? "添加分析维度" : "定义统计指标"}
                <ArrowRight className="size-4" />
              </Button>
            )}
          {catalog.isError && (
            <p role="alert" className="text-sm text-destructive">
              目录加载失败，模型与字段选择暂不可用。
              <button
                type="button"
                className="ml-2 underline"
                onClick={() => catalog.refetch()}
              >
                重试
              </button>
            </p>
          )}
        </section>
      )}
      {active === "settings" && (
        <section className="space-y-5 rounded-xl border bg-card p-5">
          <h2 className="font-semibold">主题设置</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="主题名称">
              <input
                aria-label="主题名称"
                className={control}
                maxLength={80}
                value={meta.name}
                onChange={(e) => setMeta({ ...meta, name: e.target.value })}
              />
            </Field>
            <Field label="业务责任人">
              <input
                aria-label="业务责任人"
                className={control}
                maxLength={120}
                value={definition.owner}
                onChange={(e) =>
                  setDefinition({ ...definition, owner: e.target.value })
                }
              />
            </Field>
          </div>
          <Field label="主题说明">
            <textarea
              aria-label="主题说明"
              className={control}
              rows={3}
              maxLength={500}
              value={meta.description}
              onChange={(e) =>
                setMeta({ ...meta, description: e.target.value })
              }
            />
          </Field>
          <Field label="业务时区" hint="IANA 时区，例如 Asia/Shanghai、UTC。">
            <input
              aria-label="业务时区"
              className={control}
              value={definition.timezone}
              onChange={(e) =>
                setDefinition({ ...definition, timezone: e.target.value })
              }
            />
          </Field>
          <label className="flex gap-2 text-sm">
            <input
              type="checkbox"
              checked={meta.enabled}
              onChange={(e) => setMeta({ ...meta, enabled: e.target.checked })}
            />
            启用主题（保存停用后成员立即失去访问权限）
          </label>
          <label className="flex gap-2 text-sm">
            <input
              type="checkbox"
              checked={definition.external_allowed}
              onChange={(e) =>
                setDefinition({
                  ...definition,
                  external_allowed: e.target.checked,
                })
              }
            />
            允许此数据范围用于模型问答（授权语义及表字段）
          </label>
          <p className="text-xs leading-5 text-muted-foreground">
            标准指标使用单独的语义外发配置；自由探索使用授权表字段，敏感维度字段排除。成员的明细字段需在查询授权中单独勾选。指标可以留空，仅配置数据模型也可发布。
          </p>
          <div className="flex flex-wrap gap-2 border-t pt-5">
            <Button
              variant="outline"
              disabled={busy}
              onClick={() => run(() => exportFile("yaml"))}
            >
              <Download className="size-4" />
              导出 YAML
            </Button>
            <Button
              variant="outline"
              disabled={busy}
              onClick={() => run(() => exportFile("json"))}
            >
              导出 JSON
            </Button>
            <Button
              variant="outline"
              disabled={locked}
              onClick={() => {
                operation.reset()
                setModal("import")
                setText("")
              }}
            >
              <Upload className="size-4" />
              导入语义配置
            </Button>
            {server.current_version === 0 && (
              <Button
                variant="ghost"
                disabled={locked}
                onClick={() => setModal("delete")}
              >
                删除未发布主题
              </Button>
            )}
          </div>
        </section>
      )}
      {active === "members" && (
        <section className="space-y-4 rounded-xl border bg-card p-5">
          <h2 className="font-semibold">主题成员</h2>
          <p className="text-sm leading-6 text-muted-foreground">
            普通成员只能查看获授权主题的已发布业务目录。管理员始终可以维护全部主题。
          </p>
          <p className="text-xs text-muted-foreground">
            已选择 {members.length} 人，最多 200 人。保存授权立即生效。
          </p>
          {users.isPending ? (
            <p className="text-sm">正在加载用户…</p>
          ) : users.isError ? (
            <Button variant="outline" onClick={() => users.refetch()}>
              用户加载失败，重试
            </Button>
          ) : (
            <div className="grid max-h-80 gap-3 overflow-y-auto sm:grid-cols-2">
              {users.data
                .filter((u) => !u.is_superuser)
                .map((u) => (
                  <label
                    key={u.id}
                    className="flex items-start gap-3 rounded-lg border p-3 text-sm"
                  >
                    <input
                      type="checkbox"
                      className="mt-1"
                      disabled={!u.is_active && !members.includes(u.id)}
                      checked={members.includes(u.id)}
                      onChange={(e) =>
                        setMembers(
                          e.target.checked
                            ? [...members, u.id]
                            : members.filter((id) => id !== u.id),
                        )
                      }
                    />
                    <span className="min-w-0 break-all">
                      {u.full_name || u.email}
                      <span className="mt-1 block text-xs text-muted-foreground">
                        {u.full_name ? u.email : "普通成员"}
                        {!u.is_active ? " · 已停用" : ""}
                      </span>
                    </span>
                  </label>
                ))}
            </div>
          )}
          <Button
            disabled={busy || dirty || !memberDirty || members.length > 200}
            onClick={() =>
              run(async () => {
                accept(
                  (
                    await TopicsService.saveMembers({
                      path,
                      body: {
                        expected_revision: server.revision,
                        user_ids: members,
                      },
                    })
                  ).data,
                )
                toast.success("成员权限已保存")
              })
            }
          >
            保存授权
          </Button>
          {dirty && (
            <p className="text-xs text-muted-foreground">
              请先保存语义草稿再修改授权。
            </p>
          )}
        </section>
      )}
      {active === "versions" && (
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <FileClock className="size-5" />
            <h2 className="font-semibold">不可变的发布记录</h2>
          </div>
          <p className="text-sm leading-6 text-muted-foreground">
            恢复历史版本会覆盖已保存草稿，重新校验发布后才会替换成员正在使用的版本。
          </p>
          {releases.isPending ? (
            <p className="text-sm">正在加载版本…</p>
          ) : releases.isError ? (
            <Button variant="outline" onClick={() => releases.refetch()}>
              版本加载失败，重试
            </Button>
          ) : (
            releases.data?.map((r) => (
              <article
                key={r.id}
                className="space-y-3 rounded-xl border bg-card p-5"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h3 className="font-medium">
                    v{r.version}
                    {r.version === server.current_version ? " · 当前发布" : ""}
                  </h3>
                  <span className="text-xs text-muted-foreground">
                    {new Date(r.created_at).toLocaleString("zh-CN")} · 目录 v
                    {r.catalog_version}
                  </span>
                </div>
                <p className="text-sm">{r.note}</p>
                <div className="text-xs leading-6 text-muted-foreground">
                  {r.changes.map((c) => (
                    <p key={c}>{c}</p>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={locked}
                    onClick={() => setRestore(r.version)}
                  >
                    恢复到草稿
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={busy}
                    onClick={() => run(() => exportFile("yaml", r.version))}
                  >
                    导出此版本
                  </Button>
                </div>
              </article>
            ))
          )}
          {releases.data?.length === 0 && (
            <p className="rounded-xl border border-dashed p-10 text-center text-sm text-muted-foreground">
              尚无发布记录。
            </p>
          )}
        </section>
      )}
      {editor && (
        <EntryEditor
          group={editor.group}
          entry={editor.entry}
          definition={definition}
          tables={catalog.data?.tables ?? []}
          onClose={() => setEditor(null)}
          onSave={(row) => {
            const key = editor.group
            setDefinition((d) => ({
              ...d,
              [key]: editor.entry
                ? d[key].map((r) => (r.id === editor.entry?.id ? row : r))
                : [...d[key], row],
            }))
            setEditor(null)
          }}
        />
      )}
      <Dialog
        open={!!removing}
        onOpenChange={(open) => !open && setRemoving(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>删除配置“{removing?.entry.label}”？</DialogTitle>
            <DialogDescription>
              引用此配置的指标、过滤或关联需同步调整。删除先应用到工作区，发布版本保持可用。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRemoving(null)}>
              取消
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                if (removing)
                  setDefinition((d) => ({
                    ...d,
                    [removing.group]: d[removing.group].filter(
                      (r) => r.id !== removing.entry.id,
                    ),
                  }))
                setRemoving(null)
              }}
            >
              删除配置
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <Dialog
        open={modal !== null}
        onOpenChange={(open) => !open && !busy && setModal(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {modal === "publish"
                ? `发布语义版本 v${server.current_version + 1}`
                : modal === "import"
                  ? "导入语义配置"
                  : "删除未发布主题"}
            </DialogTitle>
            <DialogDescription>
              {modal === "publish"
                ? "服务端将锁定当前修订，检查最新授权目录与语义规则。通过后成员将使用新版本。"
                : modal === "import"
                  ? "粘贴 JSON 或 YAML，最大 200 KB。导入覆盖已保存语义草稿，之后仍须校验发布。"
                  : "此操作删除当前未发布主题及其成员授权。"}
            </DialogDescription>
          </DialogHeader>
          <form
            className="space-y-4"
            onSubmit={(e) => {
              e.preventDefault()
              run(async () => {
                if (modal === "publish") {
                  await TopicsService.publishTopic({
                    path,
                    body: { expected_revision: server.revision, note: text },
                  })
                  await refresh()
                  toast.success("语义版本已发布")
                } else if (modal === "import") {
                  accept(
                    (
                      await TopicsService.importDefinition({
                        path,
                        body: {
                          expected_revision: server.revision,
                          content: text,
                        },
                      })
                    ).data,
                    true,
                  )
                  toast.success("已导入草稿，请校验")
                } else {
                  await TopicsService.deleteDraftTopic({
                    path,
                    query: { expected_revision: server.revision },
                  })
                  cache.invalidateQueries({ queryKey: ["topics"] })
                  navigate({ to: "/topics" })
                }
                setModal(null)
              })
            }}
          >
            {operation.error && (
              <p
                role="alert"
                className="rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive"
              >
                {errorMessage(operation.error)}
              </p>
            )}
            {modal !== "delete" && (
              <Field
                label={modal === "publish" ? "发布说明" : "JSON / YAML 内容"}
              >
                <textarea
                  aria-label={
                    modal === "publish" ? "发布说明" : "JSON / YAML 内容"
                  }
                  className={`${control} ${modal === "import" ? "font-mono text-xs" : ""}`}
                  rows={modal === "import" ? 12 : 3}
                  required
                  maxLength={modal === "import" ? 200000 : 300}
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                />
              </Field>
            )}
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                disabled={busy}
                onClick={() => setModal(null)}
              >
                取消
              </Button>
              <Button
                type="submit"
                disabled={busy || (modal !== "delete" && !text.trim())}
              >
                {busy
                  ? "处理中…"
                  : modal === "publish"
                    ? "确认发布"
                    : modal === "import"
                      ? "导入到草稿"
                      : "确认删除"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      <Dialog
        open={restore !== null}
        onOpenChange={(open) => !open && !busy && setRestore(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>将 v{restore} 恢复到草稿？</DialogTitle>
            <DialogDescription>
              当前已保存的语义草稿将被替换，线上发布版本保持不变。可以先导出当前草稿备份。
            </DialogDescription>
          </DialogHeader>
          {operation.error && (
            <p role="alert" className="text-sm text-destructive">
              {errorMessage(operation.error)}
            </p>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              disabled={busy}
              onClick={() => setRestore(null)}
            >
              取消
            </Button>
            <Button
              disabled={busy}
              onClick={() =>
                run(async () => {
                  accept(
                    (
                      await TopicsService.restoreRelease({
                        path: { ...path, version: restore! },
                        body: { expected_revision: server.revision },
                      })
                    ).data,
                  )
                  setRestore(null)
                  toast.success("历史定义已恢复到草稿，请重新校验发布")
                })
              }
            >
              确认恢复
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <Dialog
        open={blocker.status === "blocked"}
        onOpenChange={(open) => !open && blocker.reset?.()}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>离开未保存的工作区？</DialogTitle>
            <DialogDescription>
              未保存的语义配置或成员权限将丢失。请返回保存，或确认放弃修改。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => blocker.reset?.()}>
              继续编辑
            </Button>
            <Button variant="destructive" onClick={() => blocker.proceed?.()}>
              放弃并离开
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
