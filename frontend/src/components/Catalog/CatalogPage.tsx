import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Link, useNavigate, useSearch } from "@tanstack/react-router"
import {
  BookOpen,
  ChevronRight,
  Columns3,
  GitBranch,
  History,
  KeyRound,
  Loader2,
  RefreshCw,
  Search,
  Settings2,
  ShieldCheck,
  Table2,
} from "lucide-react"
import { useEffect, useState } from "react"
import { toast } from "sonner"
import {
  CatalogService,
  type DataSourcePublic,
  DatasourcesService,
  type SyncJobPublic,
  type TableMeta,
} from "@/client"
import { DataJourney } from "@/components/Common/DataJourney"
import {
  databaseLabel,
  dateLabel,
  errorMessage,
  kinds,
} from "@/components/DataSources/shared"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useAuth from "@/hooks/useAuth"
import { objectKey, ScopeEditor } from "./ScopeEditor"

const statusLabels: Record<string, string> = {
  queued: "等待同步",
  running: "同步中",
  succeeded: "同步成功",
  failed: "同步失败",
  superseded: "已失效",
}
const isActive = (job: SyncJobPublic) =>
  ["queued", "running"].includes(job.status)

export function CatalogPage() {
  const { user } = useAuth()
  const { source: sourceId } = useSearch({ from: "/_layout/catalog" })
  const navigate = useNavigate()
  const sources = useQuery({
    queryKey: ["datasources"],
    queryFn: async () => (await DatasourcesService.listDatasources()).data,
    enabled: !!user?.is_superuser,
  })
  const source =
    sources.data?.data.find((s) => s.id === sourceId) ?? sources.data?.data[0]
  if (user && !user.is_superuser)
    return (
      <div className="rounded-xl border bg-card p-10 text-center">
        <ShieldCheck className="mx-auto mb-4 size-9 text-muted-foreground" />
        <h1 className="text-xl font-semibold">数据表目录由管理员维护</h1>
        <p className="mt-2 text-muted-foreground">
          请联系管理员配置业务表的同步范围。
        </p>
      </div>
    )
  return (
    <div className="mx-auto max-w-[1360px] space-y-6 pb-8">
      <div className="flex flex-wrap items-end justify-between gap-5">
        <div>
          <div className="mb-3 flex items-center gap-2 text-xs text-muted-foreground">
            数据管理
            <ChevronRight className="size-3" />
            <span className="text-foreground">数据表目录</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">数据表目录</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            选择允许使用的表，查看字段和表之间的关联。这里管理数据结构，业务含义在「业务主题」中配置。
          </p>
        </div>
        <div className="w-full sm:w-64">
          <label
            htmlFor="catalog-source"
            className="mb-2 block text-xs text-muted-foreground"
          >
            当前数据源
          </label>
          <select
            id="catalog-source"
            className="h-10 w-full rounded-lg border bg-card px-3 text-sm"
            value={source?.id ?? ""}
            onChange={(e) =>
              navigate({
                to: "/catalog",
                search: { source: e.target.value },
                replace: true,
              })
            }
          >
            {!source && (
              <option value="">
                {sources.isPending ? "加载中…" : "暂无数据源"}
              </option>
            )}
            {sources.data?.data.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
                {!s.enabled ? "（已停用）" : ""}
              </option>
            ))}
          </select>
        </div>
      </div>
      <DataJourney current="/catalog" />
      {sources.isError ? (
        <Failure error={sources.error} retry={() => sources.refetch()} />
      ) : sources.isPending ? (
        <Loading />
      ) : source ? (
        <SourceCatalog
          key={`${source.id}:${source.revision}`}
          source={source}
        />
      ) : (
        <div className="rounded-xl border p-12 text-center">
          <BookOpen className="mx-auto mb-4 size-10 text-muted-foreground" />
          <h2 className="font-medium">先连接一个数据库</h2>
          <p className="my-3 text-sm text-muted-foreground">
            添加数据源后，即可选择表和视图并同步结构。
          </p>
          <Button asChild>
            <Link to="/datasources">前往数据源</Link>
          </Button>
        </div>
      )}
    </div>
  )
}

function SourceCatalog({ source }: { source: DataSourcePublic }) {
  const qc = useQueryClient()
  const path = { source_id: source.id }
  const [scopeOpen, setScopeOpen] = useState(false)
  const [search, setSearch] = useState("")
  const [kind, setKind] = useState("all")
  const [selected, setSelected] = useState("")
  const catalog = useQuery({
    queryKey: ["catalog", source.id],
    queryFn: async () => (await CatalogService.getCatalog({ path })).data,
  })
  const jobs = useQuery({
    queryKey: ["catalog-jobs", source.id],
    queryFn: async () => (await CatalogService.listSyncJobs({ path })).data,
    refetchInterval: (query) =>
      query.state.data?.some(isActive) ? 1500 : 5000,
  })
  const latest = jobs.data?.[0]
  useEffect(() => {
    if (latest && !isActive(latest))
      qc.invalidateQueries({ queryKey: ["catalog", source.id] })
  }, [latest, qc, source.id])
  const sync = useMutation({
    mutationFn: () => CatalogService.syncCatalog({ path }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["catalog-jobs", source.id] })
      toast.success("同步任务已提交")
    },
    onError: (e) => toast.error(errorMessage(e)),
  })
  const data = catalog.data
  const tables = data?.tables ?? []
  const incompleteCount = tables.filter((t) => t.warnings?.length).length
  const shown = tables.filter(
    (t) =>
      (kind === "all" || t.kind === kind) &&
      `${t.schema_name}.${t.name} ${t.comment ?? ""} ${t.columns.map((c) => `${c.name} ${c.comment ?? ""}`).join(" ")}`
        .toLowerCase()
        .includes(search.toLowerCase()),
  )
  const detail = shown.find((t) => objectKey(t) === selected) ?? shown[0]
  const busy = jobs.data?.some(
    (job) =>
      isActive(job) &&
      job.scope_revision === data?.revision &&
      job.source_revision === source.revision,
  )
  if (catalog.isError)
    return <Failure error={catalog.error} retry={() => catalog.refetch()} />
  if (!data) return <Loading />
  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border bg-card px-5 py-4">
        <div className="flex flex-wrap items-center gap-3 text-sm">
          <span className="rounded-md bg-primary/8 px-2.5 py-1 font-medium text-primary">
            {kinds[source.database_type].label}
          </span>
          <span className="text-muted-foreground">
            {databaseLabel(source.database_type)}：{source.database}
          </span>
          <span className="text-xs text-muted-foreground">
            目录版本 v{data.version}
          </span>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setScopeOpen(true)}
            disabled={!source.enabled}
          >
            <Settings2 className="size-4" />
            选择数据表
          </Button>
          <Button
            onClick={() => sync.mutate()}
            disabled={
              !source.enabled ||
              !data.scope.length ||
              data.needs_confirmation ||
              sync.isPending ||
              !!busy
            }
          >
            {busy || sync.isPending ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <RefreshCw className="size-4" />
            )}
            {busy ? "正在同步" : "更新表结构"}
          </Button>
        </div>
      </div>
      {!source.enabled ? (
        <Notice>
          数据源已停用，目录已隐藏。请在数据源页面启用后重新确认范围。
        </Notice>
      ) : data.needs_confirmation ? (
        <Notice>
          连接配置已变化，旧目录已隐藏。请打开“选择数据表”重新确认当前数据库的表。
        </Notice>
      ) : data.needs_sync && data.scope.length > 0 ? (
        <Notice>
          已选数据表有更新。请点击“更新表结构”，获取最新字段和关联。
        </Notice>
      ) : null}
      {latest && (
        <div
          role="status"
          className={`flex flex-wrap items-center gap-3 rounded-lg border px-4 py-3 text-sm ${latest.status === "failed" ? "border-destructive/30 bg-destructive/5" : "bg-muted/20"}`}
        >
          <span className="font-medium">
            {statusLabels[latest.status] ?? latest.status}
          </span>
          <span className="text-muted-foreground">{latest.message}</span>
          {latest.status === "queued" && (
            <span className="text-xs text-muted-foreground">
              长时间等待时，请联系管理员检查同步服务。
            </span>
          )}
          <span className="ml-auto text-xs text-muted-foreground">
            {dateLabel(latest.finished_at ?? latest.created_at)}
          </span>
        </div>
      )}
      {incompleteCount > 0 && (
        <Notice>
          有 {incompleteCount}{" "}
          个对象的键元数据不完整，请查看对应对象的提示；关联数量仅统计已取得完整映射的外键。
        </Notice>
      )}
      <div className="grid grid-cols-3 gap-2 sm:gap-4">
        {[
          {
            label: "可用数据表",
            value: tables.length,
            sub: `${tables.filter((t) => t.kind === "table").length} 张表 · ${tables.filter((t) => t.kind === "view").length} 个视图`,
            icon: Table2,
          },
          {
            label: "字段总数",
            value: tables.reduce((sum, t) => sum + t.columns.length, 0),
            sub: "包含类型、注释与主键信息",
            icon: Columns3,
          },
          {
            label: "关联关系",
            value: tables.reduce(
              (sum, t) => sum + (t.foreign_keys?.length ?? 0),
              0,
            ),
            sub: "来自授权对象之间的数据库外键",
            icon: GitBranch,
          },
        ].map(({ label, value, sub, icon: Icon }) => (
          <div
            key={label}
            className="flex min-w-0 justify-between rounded-xl border bg-card p-3 shadow-xs sm:p-5"
          >
            <div>
              <p className="text-xs text-muted-foreground sm:text-sm">
                {label}
              </p>
              <p className="my-2 text-2xl font-semibold tabular-nums sm:text-3xl">
                {value.toString().padStart(2, "0")}
              </p>
              <p className="hidden text-xs text-muted-foreground sm:block">
                {sub}
              </p>
            </div>
            <Icon className="hidden size-5 shrink-0 text-primary/70 sm:block" />
          </div>
        ))}
      </div>
      <Tabs defaultValue="catalog">
        <TabsList>
          <TabsTrigger value="catalog">
            <BookOpen className="size-4" />
            数据目录
          </TabsTrigger>
          <TabsTrigger value="history">
            <History className="size-4" />
            同步记录
          </TabsTrigger>
        </TabsList>
        <TabsContent value="catalog" className="mt-3">
          <div className="grid min-w-0 overflow-hidden rounded-xl border bg-card shadow-xs lg:grid-cols-[260px_minmax(0,1fr)]">
            <aside className="border-b lg:border-b-0 lg:border-r">
              <div className="space-y-3 border-b p-4">
                <div className="relative">
                  <Search className="absolute left-3 top-3 size-4 text-muted-foreground" />
                  <Input
                    aria-label="搜索目录"
                    className="pl-9"
                    placeholder="搜索表、字段或注释"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>
                <div className="flex gap-1">
                  {[
                    ["all", "全部"],
                    ["table", "表"],
                    ["view", "视图"],
                  ].map(([value, label]) => (
                    <Button
                      key={value}
                      size="sm"
                      variant={kind === value ? "secondary" : "ghost"}
                      onClick={() => setKind(value)}
                    >
                      {label}
                    </Button>
                  ))}
                </div>
              </div>
              <div className="max-h-60 overflow-y-auto p-2 lg:max-h-[540px]">
                {shown.map((t) => (
                  <button
                    key={objectKey(t)}
                    type="button"
                    aria-pressed={detail === t}
                    onClick={() => setSelected(objectKey(t))}
                    className={`mb-1 flex w-full items-start gap-3 rounded-lg px-3 py-3 text-left ${detail === t ? "bg-primary/8 text-primary" : "hover:bg-muted/50"}`}
                  >
                    <Table2 className="mt-1 size-4 shrink-0" />
                    <span className="min-w-0 flex-1">
                      <span className="block break-all font-mono text-sm font-medium">
                        {t.name}
                      </span>
                      <span className="mt-1 block text-xs text-muted-foreground">
                        {t.schema_name} · {t.kind === "view" ? "视图" : "表"} ·{" "}
                        {t.columns.length} 字段
                      </span>
                    </span>
                  </button>
                ))}
                {!shown.length && (
                  <p className="p-5 text-sm text-muted-foreground">
                    {tables.length ? "没有匹配的表或字段" : "目录尚无对象"}
                  </p>
                )}
              </div>
              <p className="border-t p-4 text-xs text-muted-foreground">
                已授权 {data.scope.length} 个对象 · 当前显示 {shown.length} 个
              </p>
            </aside>
            {detail ? (
              <TableDetail key={objectKey(detail)} table={detail} />
            ) : (
              <div className="flex min-h-[420px] flex-col items-center justify-center px-8 text-center">
                <BookOpen className="mb-4 size-12 text-primary/30" />
                <h2 className="text-lg font-semibold">
                  {tables.length
                    ? "没有匹配的结果"
                    : data.scope.length
                      ? "等待结构同步"
                      : "建立你的业务数据目录"}
                </h2>
                <p className="mt-3 max-w-sm text-sm leading-7 text-muted-foreground">
                  {tables.length
                    ? "试试其他表名、字段名或业务注释。"
                    : data.scope.length
                      ? "同步完成后，可在这里查看字段定义、中文注释与表之间的关联。"
                      : "先选择允许纳入问数的表和视图，再同步数据库结构。"}
                </p>
                {!data.scope.length && (
                  <Button
                    className="mt-5"
                    onClick={() => setScopeOpen(true)}
                    disabled={!source.enabled}
                  >
                    选择表和视图
                  </Button>
                )}
              </div>
            )}
          </div>
        </TabsContent>
        <TabsContent value="history" className="mt-3">
          {jobs.isError ? (
            <Failure error={jobs.error} retry={() => jobs.refetch()} />
          ) : jobs.isPending ? (
            <Loading />
          ) : (
            <JobHistory jobs={jobs.data ?? []} />
          )}
        </TabsContent>
      </Tabs>
      {tables.length > 0 && !data.needs_sync && !data.needs_confirmation && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-primary/20 bg-primary/5 p-4">
          <div>
            <p className="text-sm font-medium">
              数据表已准备好，下一步整理业务含义
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              在业务主题中选择这些表，设置日期、地区等分析维度，以及销售额等指标。
            </p>
          </div>
          <Button variant="outline" asChild>
            <Link to="/topics" search={{ source: source.id }}>
              前往业务主题
              <ChevronRight className="size-4" />
            </Link>
          </Button>
        </div>
      )}
      <div className="flex flex-wrap justify-between gap-2 text-xs text-muted-foreground">
        <span>仅采集结构，未读取业务行数据。字段注释保留在本地。</span>
        <span>
          最近成功同步：
          {data.synced_at ? dateLabel(data.synced_at) : "尚未同步"}
        </span>
      </div>
      {scopeOpen && (
        <ScopeEditor catalog={data} onClose={() => setScopeOpen(false)} />
      )}
    </>
  )
}

function TableDetail({ table }: { table: TableMeta }) {
  const [fieldSearch, setFieldSearch] = useState("")
  const columns = table.columns.filter((c) =>
    `${c.name} ${c.comment ?? ""}`
      .toLowerCase()
      .includes(fieldSearch.toLowerCase()),
  )
  return (
    <section className="min-w-0">
      <div className="border-b p-6">
        <p className="mb-2 text-xs text-muted-foreground">
          {table.schema_name} / {table.kind === "view" ? "视图" : "数据表"}
        </p>
        <h2 className="break-all font-mono text-xl font-semibold">
          {table.name}
        </h2>
        <p className="mt-2 text-sm text-muted-foreground">
          {table.comment || "数据库未提供对象注释"}
        </p>
        {table.warnings?.map((warning) => (
          <div key={warning} className="mt-4">
            <Notice>{warning}</Notice>
          </div>
        ))}
      </div>
      <Tabs defaultValue="columns" className="p-5">
        <div className="flex flex-wrap justify-between gap-3">
          <TabsList>
            <TabsTrigger value="columns">
              字段 {table.columns.length}
            </TabsTrigger>
            <TabsTrigger value="relations">
              关联 {table.foreign_keys?.length ?? 0}
            </TabsTrigger>
          </TabsList>
        </div>
        <TabsContent value="columns">
          <Input
            className="my-3 max-w-xs"
            aria-label="搜索字段"
            placeholder="搜索字段名或注释"
            value={fieldSearch}
            onChange={(e) => setFieldSearch(e.target.value)}
          />
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b text-xs text-muted-foreground">
                <tr>
                  <th className="py-3 pr-4 font-medium">字段</th>
                  <th className="py-3 pr-4 font-medium">数据库类型</th>
                  <th className="py-3 pr-4 font-medium">可空</th>
                  <th className="py-3 font-medium">业务注释</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {columns.map((c) => (
                  <tr key={c.name}>
                    <td className="py-4 pr-4">
                      <span className="inline-flex items-center gap-2 font-mono">
                        {c.primary_key && (
                          <KeyRound
                            aria-label="主键"
                            className="size-3.5 shrink-0 text-amber-600"
                          />
                        )}
                        {c.name}
                      </span>
                    </td>
                    <td className="py-4 pr-4 font-mono text-xs text-muted-foreground">
                      {c.data_type}
                    </td>
                    <td className="py-4 pr-4 text-muted-foreground">
                      {c.nullable ? "是" : "否"}
                    </td>
                    <td className="py-4">
                      {c.comment || (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!columns.length && (
              <p className="py-8 text-sm text-muted-foreground">
                没有匹配的字段。
              </p>
            )}
          </div>
        </TabsContent>
        <TabsContent value="relations" className="space-y-3 pt-4">
          {table.foreign_keys?.map((fk) => (
            <div key={fk.name} className="rounded-lg border p-4">
              <p className="flex items-center gap-2 text-sm font-medium">
                <GitBranch className="size-4 text-primary" />
                {fk.name}
              </p>
              <div className="mt-3 space-y-2">
                {fk.columns.map((column, i) => (
                  <p
                    key={column}
                    className="break-all font-mono text-xs leading-6"
                  >
                    {table.name}.{column}{" "}
                    <span className="px-2 text-muted-foreground">→</span>{" "}
                    {fk.target_schema}.{fk.target_table}.{fk.target_columns[i]}
                  </p>
                ))}
              </div>
              <p className="mt-3 text-xs text-muted-foreground">
                数据库外键 ·{" "}
                {fk.columns.length > 1
                  ? "复合关联，所有字段需一起匹配"
                  : "单字段关联"}
              </p>
            </div>
          ))}
          {!table.foreign_keys?.length && (
            <p className="py-10 text-center text-sm text-muted-foreground">
              {table.warnings?.length
                ? "当前账号未取得完整的外键字段映射。"
                : "当前授权范围内未发现数据库外键关系。"}
              <br />
              <span className="mt-2 inline-block">
                业务关联将在语义层模块中维护。
              </span>
            </p>
          )}
        </TabsContent>
      </Tabs>
    </section>
  )
}

function JobHistory({ jobs }: { jobs: SyncJobPublic[] }) {
  if (!jobs.length)
    return (
      <div className="rounded-xl border bg-card p-12 text-center text-sm text-muted-foreground">
        还没有同步记录。配置范围后，点击“立即同步”。
      </div>
    )
  return (
    <div className="space-y-3">
      {jobs.map((job) => (
        <details key={job.id} className="rounded-xl border bg-card p-5">
          <summary className="flex cursor-pointer flex-wrap items-center gap-3">
            <span
              className={`rounded-md px-2 py-1 text-xs font-medium ${job.status === "succeeded" ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300" : job.status === "failed" ? "bg-destructive/10 text-destructive" : "bg-muted text-muted-foreground"}`}
            >
              {statusLabels[job.status] ?? job.status}
            </span>
            <span className="text-sm">{job.message}</span>
            <span className="ml-auto text-xs text-muted-foreground">
              {dateLabel(job.created_at)} · {job.changes.length} 项变更
            </span>
          </summary>
          <div className="mt-5 space-y-3 border-t pt-4">
            <p className="text-xs text-muted-foreground">
              范围版本 {job.scope_revision} ·{" "}
              {job.version ? `目录 v${job.version}` : "未发布目录"} · 任务{" "}
              {job.id.slice(0, 8)}
            </p>
            {job.changes.map((change, i) => (
              <div
                key={`${change.path}:${change.detail}:${i}`}
                className="rounded-lg bg-muted/30 p-3"
              >
                <p className="break-all text-sm">
                  <span className="mr-2 font-medium">
                    {
                      { added: "+ 新增", removed: "− 移出", changed: "~ 变更" }[
                        change.action
                      ]
                    }
                  </span>
                  <span className="font-mono">{change.path}</span>
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {change.detail}
                </p>
                {change.before && (
                  <pre className="mt-2 whitespace-pre-wrap break-all text-xs text-muted-foreground">
                    变更前：{change.before}
                  </pre>
                )}
                {change.after && (
                  <pre className="mt-2 whitespace-pre-wrap break-all text-xs">
                    变更后：{change.after}
                  </pre>
                )}
              </div>
            ))}
            {!job.changes.length && (
              <p className="text-sm text-muted-foreground">
                {job.status === "succeeded"
                  ? "与上次成功快照一致，没有结构变更。"
                  : "此任务尚未发布结构变更。"}
              </p>
            )}
          </div>
        </details>
      ))}
    </div>
  )
}

function Notice({ children }: { children: React.ReactNode }) {
  return (
    <p
      role="status"
      className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200"
    >
      {children}
    </p>
  )
}
function Loading() {
  return (
    <div className="flex justify-center gap-2 rounded-xl border p-12 text-sm text-muted-foreground">
      <Loader2 className="size-4 animate-spin" />
      正在加载…
    </div>
  )
}
function Failure({ error, retry }: { error: unknown; retry: () => void }) {
  return (
    <div role="alert" className="rounded-xl border p-8 text-center">
      <p className="mb-3 text-sm text-destructive">{errorMessage(error)}</p>
      <Button variant="outline" onClick={retry}>
        重新加载
      </Button>
    </div>
  )
}
