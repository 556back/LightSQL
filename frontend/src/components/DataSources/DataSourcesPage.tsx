import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  ArrowRight,
  CheckCircle2,
  Database,
  Ellipsis,
  KeyRound,
  Loader2,
  Plus,
  ShieldCheck,
  Unplug,
  XCircle,
} from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"
import { type DataSourcePublic, DatasourcesService } from "@/client"
import { DataJourney } from "@/components/Common/DataJourney"
import { PageHeader } from "@/components/Common/PageHeader"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { SearchInput } from "@/components/ui/search-input"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import useAuth from "@/hooks/useAuth"
import { SourceEditor } from "./SourceEditor"
import {
  DatabaseIcon,
  databaseLabel,
  dateLabel,
  errorMessage,
  kinds,
  Status,
} from "./shared"

export function DataSourcesPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState("")
  const [page, setPage] = useState(1)
  const [kindFilter, setKindFilter] = useState("all")
  const [editor, setEditor] = useState<DataSourcePublic | "new" | null>(null)
  const [detailId, setDetailId] = useState<string | null>(null)
  const [deleting, setDeleting] = useState<DataSourcePublic | null>(null)
  const query = useQuery({
    queryKey: ["datasources"],
    queryFn: async () => (await DatasourcesService.listDatasources()).data,
    enabled: !!user?.is_superuser,
  })
  const refresh = () =>
    queryClient.invalidateQueries({ queryKey: ["datasources"] })
  const test = useMutation({
    mutationFn: async (id: string) =>
      (await DatasourcesService.testDatasource({ path: { source_id: id } }))
        .data,
    onSuccess: (result) => {
      refresh()
      result.success
        ? toast.success("连接成功，基础读取测试通过")
        : toast.error(result.message)
    },
    onError: (err) => toast.error(errorMessage(err)),
  })
  const toggle = useMutation({
    mutationFn: async (source: DataSourcePublic) =>
      DatasourcesService.updateDatasource({
        path: { source_id: source.id },
        body: {
          name: source.name,
          database_type: source.database_type,
          host: source.host,
          port: source.port,
          database: source.database,
          username: source.username,
          description: source.description,
          tls_mode: source.tls_mode,
          enabled: !source.enabled,
          expected_revision: source.revision,
        },
      }),
    onSuccess: () => {
      refresh()
      toast.success("数据源状态已更新")
    },
    onError: (err) => toast.error(errorMessage(err)),
  })
  const remove = useMutation({
    mutationFn: async (source: DataSourcePublic) =>
      DatasourcesService.deleteDatasource({
        path: { source_id: source.id },
        query: { expected_revision: source.revision },
      }),
    onSuccess: () => {
      refresh()
      setDeleting(null)
      setDetailId(null)
      toast.success("连接配置已删除")
    },
    onError: (err) => toast.error(errorMessage(err)),
  })
  const sources = query.data?.data ?? []
  const detail = sources.find((source) => source.id === detailId)
  const visible = sources.filter(
    (source) =>
      (kindFilter === "all" || source.database_type === kindFilter) &&
      `${source.name} ${source.host} ${source.database}`
        .toLowerCase()
        .includes(search.toLowerCase()),
  )
  const pageCount = Math.max(1, Math.ceil(visible.length / 10))
  const activePage = Math.min(page, pageCount)
  const pageSources = visible.slice((activePage - 1) * 10, activePage * 10)
  const connected = sources.filter(
    (source) => source.enabled && source.status === "connected",
  ).length
  const pending = sources.filter(
    (source) => source.enabled && source.status !== "connected",
  ).length
  if (user && !user.is_superuser)
    return (
      <div className="rounded-xl border bg-card p-10 text-center">
        <ShieldCheck className="mx-auto mb-4 size-9 text-muted-foreground" />
        <h1 className="text-xl font-semibold">数据源由管理员维护</h1>
        <p className="mt-2 text-muted-foreground">
          请联系管理员配置你需要使用的数据连接。
        </p>
      </div>
    )
  return (
    <div className="mx-auto max-w-[1280px] space-y-7 pb-8">
      <PageHeader
        eyebrow="数据准备 / 数据管理"
        title="数据库连接"
        description="管理业务数据库的连接信息。连接成功后，前往数据表目录选择要分析的表。"
        action={
          <Button
            className="h-10 px-4"
            onClick={() => setEditor("new")}
            disabled={!user?.is_superuser}
          >
            <Plus className="size-4" />
            添加数据源
          </Button>
        }
      />
      <DataJourney current="/datasources" />
      <div className="grid gap-4 sm:grid-cols-3">
        {[
          {
            title: "已添加数据源",
            value: sources.length,
            text: "统一管理所有连接",
            icon: Database,
            tone: "text-primary bg-primary/8",
          },
          {
            title: "连接正常",
            value: connected,
            text: "最近一次连接测试通过",
            icon: CheckCircle2,
            tone: "text-emerald-600 bg-emerald-50 dark:bg-emerald-950",
          },
          {
            title: "待检查",
            value: pending,
            text: "未测试或需要检查的连接",
            icon: Unplug,
            tone: "text-amber-600 bg-amber-50 dark:bg-amber-950",
          },
        ].map(({ title, value, text, icon: Icon, tone }) => (
          <div
            key={title}
            className="flex items-start justify-between rounded-xl border bg-card p-5 shadow-xs"
          >
            <div>
              <p className="text-sm text-muted-foreground">{title}</p>
              <p className="my-2 font-mono text-3xl font-semibold tracking-tight">
                {query.isPending ? "—" : value.toString().padStart(2, "0")}
              </p>
              <p className="text-xs text-muted-foreground">{text}</p>
            </div>
            <span className={`rounded-lg p-2.5 ${tone}`}>
              <Icon className="size-4" />
            </span>
          </div>
        ))}
      </div>
      <section
        className="overflow-hidden rounded-xl border bg-card shadow-xs"
        aria-label="数据源列表"
      >
        <div className="flex flex-wrap items-center justify-between gap-4 border-b px-5 py-4">
          <div className="flex items-center gap-3">
            <h2 className="font-semibold">我的数据源</h2>
            <span className="rounded-md bg-muted px-2 py-0.5 font-mono text-xs text-muted-foreground">
              {sources.length}
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            <SearchInput
              label="搜索数据源"
              value={search}
              onValueChange={(value) => {
                setSearch(value)
                setPage(1)
              }}
              className="w-full sm:w-64"
              placeholder="搜索名称、地址或数据库"
            />
            <select
              aria-label="数据库类型筛选"
              value={kindFilter}
              onChange={(e) => {
                setKindFilter(e.target.value)
                setPage(1)
              }}
              className="h-10 rounded-md border bg-background px-3 text-sm"
            >
              <option value="all">全部类型</option>
              {Object.entries(kinds).map(([key, value]) => (
                <option key={key} value={key}>
                  {value.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        {query.isError ? (
          <div role="alert" className="p-8 text-center">
            <p className="mb-3 text-destructive">{errorMessage(query.error)}</p>
            <Button variant="outline" onClick={() => query.refetch()}>
              重新加载
            </Button>
          </div>
        ) : query.isPending ? (
          <div className="flex items-center justify-center gap-2 p-16 text-muted-foreground">
            <Loader2 className="size-4 animate-spin" />
            正在读取数据源…
          </div>
        ) : visible.length === 0 ? (
          <div className="px-6 py-16 text-center">
            <div className="mx-auto mb-4 flex size-14 items-center justify-center rounded-2xl bg-primary/5">
              <Database className="size-6 text-primary" />
            </div>
            <h3 className="font-medium">
              {sources.length
                ? "没有找到匹配的数据源"
                : "从连接第一个数据库开始"}
            </h3>
            <p className="mb-5 mt-2 text-sm text-muted-foreground">
              {sources.length
                ? "试试其他关键词，或切换数据库类型。"
                : "支持 PostgreSQL、MySQL、Oracle，连接信息会安全保存。"}
            </p>
            {!sources.length && (
              <Button variant="outline" onClick={() => setEditor("new")}>
                <Plus className="size-4" />
                添加数据源
              </Button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[840px] text-left text-sm">
              <thead className="bg-muted/30 text-xs text-muted-foreground">
                <tr>
                  <th className="px-5 py-3 font-medium">数据源</th>
                  <th className="px-4 py-3 font-medium">连接地址</th>
                  <th className="px-4 py-3 font-medium">连接状态</th>
                  <th className="px-4 py-3 font-medium">最近检查</th>
                  <th className="px-5 py-3 text-right font-medium">操作</th>
                </tr>
              </thead>
              <tbody>
                {pageSources.map((source) => (
                  <tr
                    key={source.id}
                    className="group border-t transition-colors hover:bg-muted/25"
                  >
                    <td className="px-5 py-5">
                      <button
                        type="button"
                        className="flex items-center gap-3 text-left"
                        onClick={() => setDetailId(source.id)}
                      >
                        <DatabaseIcon kind={source.database_type} />
                        <span>
                          <span className="block font-medium group-hover:text-primary">
                            {source.name}
                          </span>
                          <span className="mt-1 block text-xs text-muted-foreground">
                            {kinds[source.database_type].label}
                            <span className="mx-2 text-border">/</span>
                            {source.database}
                          </span>
                        </span>
                      </button>
                    </td>
                    <td className="px-4 py-5">
                      <span className="font-mono text-xs">
                        {source.host}:{source.port}
                      </span>
                      <span className="mt-1.5 flex items-center gap-1 text-xs text-muted-foreground">
                        <KeyRound className="size-3" />
                        {source.username}
                      </span>
                    </td>
                    <td className="px-4 py-5">
                      <Status source={source} />
                    </td>
                    <td className="px-4 py-5">
                      <span className="text-xs text-muted-foreground">
                        {dateLabel(source.last_tested_at)}
                      </span>
                      {source.latency_ms !== null && (
                        <span className="mt-1.5 block font-mono text-[11px] text-muted-foreground">
                          {source.latency_ms} ms
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-5">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          size="sm"
                          variant="ghost"
                          disabled={
                            !source.enabled ||
                            test.isPending ||
                            toggle.isPending
                          }
                          onClick={() => test.mutate(source.id)}
                        >
                          {test.isPending && test.variables === source.id ? (
                            <Loader2 className="size-3.5 animate-spin" />
                          ) : (
                            <Unplug className="size-3.5" />
                          )}
                          测试
                        </Button>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              aria-label={`管理 ${source.name}`}
                            >
                              <Ellipsis className="size-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem
                              onClick={() => setDetailId(source.id)}
                            >
                              查看详情
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => setEditor(source)}>
                              编辑连接
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              disabled={toggle.isPending}
                              onClick={() => toggle.mutate(source)}
                            >
                              {source.enabled ? "停用数据源" : "启用数据源"}
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              className="text-destructive"
                              onClick={() => setDeleting(source)}
                            >
                              删除连接
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {visible.length > 10 && (
          <nav
            aria-label="数据源分页"
            className="flex flex-wrap items-center justify-end gap-3 border-t px-5 py-3 text-xs text-muted-foreground"
          >
            <span>
              第 {activePage} / {pageCount} 页 · {visible.length} 个结果
            </span>
            <Button
              size="sm"
              variant="outline"
              disabled={activePage === 1}
              onClick={() => setPage(activePage - 1)}
            >
              上一页
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={activePage === pageCount}
              onClick={() => setPage(activePage + 1)}
            >
              下一页
            </Button>
          </nav>
        )}
        <div className="flex flex-wrap justify-between gap-2 border-t bg-muted/15 px-5 py-3 text-xs text-muted-foreground">
          <span>
            共 {sources.length} 个数据源 ·{" "}
            {sources.filter((s) => !s.enabled).length} 个已停用
          </span>
          <span>连接状态以最近一次测试为准</span>
        </div>
      </section>
      <section
        className="grid gap-5 rounded-xl border border-primary/15 bg-primary/[0.035] p-6 md:grid-cols-[1.3fr_1fr_1fr]"
        aria-label="连接说明"
      >
        <div className="flex gap-3">
          <div className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
            <ShieldCheck className="size-4 text-primary" />
          </div>
          <div>
            <h3 className="text-sm font-semibold">让每一次连接都有边界</h3>
            <p className="mt-2 text-xs leading-6 text-muted-foreground">
              连接凭证加密保存，仅管理员可配置。
              <br />
              基础连接测试不会修改业务数据。
            </p>
          </div>
        </div>
        <div className="border-primary/10 md:border-l md:pl-6">
          <p className="mb-2 text-sm font-medium">使用专用只读账号</p>
          <p className="text-xs leading-6 text-muted-foreground">
            请在数据库侧授予必要读取权限。
            <br />
            连接成功不代表账号已通过权限审计。
          </p>
        </div>
        <div className="border-primary/10 md:border-l md:pl-6">
          <p className="mb-2 text-sm font-medium">清晰描述数据用途</p>
          <p className="text-xs leading-6 text-muted-foreground">
            为连接设置易懂的名称与备注，
            <br />
            方便后续管理主题和业务指标。
          </p>
        </div>
      </section>
      {editor && (
        <SourceEditor
          source={editor === "new" ? null : editor}
          onClose={() => setEditor(null)}
        />
      )}
      <Sheet
        open={!!detail}
        onOpenChange={(open) => {
          if (!open) setDetailId(null)
        }}
      >
        <SheetContent className="overflow-y-auto sm:max-w-[460px]">
          {detail && (
            <>
              <SheetHeader className="border-b px-6 pb-6 pt-8">
                <DatabaseIcon kind={detail.database_type} />
                <SheetTitle className="mt-3 text-xl">{detail.name}</SheetTitle>
                <SheetDescription>
                  {kinds[detail.database_type].label} 连接详情
                </SheetDescription>
              </SheetHeader>
              <div className="space-y-6 p-6">
                <Status source={detail} />
                <dl className="space-y-5">
                  {[
                    ["主机地址", `${detail.host}:${detail.port}`],
                    [databaseLabel(detail.database_type), detail.database],
                    ["连接账号", detail.username],
                    ["密码", "已加密保存 · 不可查看"],
                    [
                      "传输加密",
                      detail.tls_mode === "verify-full"
                        ? "TLS · 验证服务器证书"
                        : "未启用 TLS",
                    ],
                    ["最近测试", dateLabel(detail.last_tested_at)],
                    ["备注", detail.description || "暂无备注"],
                  ].map(([label, value]) => (
                    <div key={label}>
                      <dt className="mb-1 text-xs text-muted-foreground">
                        {label}
                      </dt>
                      <dd className="break-all text-sm">{value}</dd>
                    </div>
                  ))}
                </dl>
                {detail.last_error && (
                  <div
                    role="alert"
                    className="flex gap-2 rounded-lg bg-destructive/10 p-3 text-sm text-destructive"
                  >
                    <XCircle className="mt-0.5 size-4 shrink-0" />
                    {detail.last_error}
                  </div>
                )}
                <p className="rounded-lg bg-muted p-3 text-xs leading-5 text-muted-foreground">
                  此处展示连接测试结果。读取范围与账号权限需要在后续接入过程中单独确认。
                </p>
                <div className="flex gap-3">
                  <Button
                    disabled={!detail.enabled || test.isPending}
                    onClick={() => test.mutate(detail.id)}
                  >
                    {test.isPending ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      <Unplug className="size-4" />
                    )}
                    重新测试
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setEditor(detail)
                      setDetailId(null)
                    }}
                  >
                    编辑连接
                    <ArrowRight className="size-4" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
      <Dialog
        open={!!deleting}
        onOpenChange={(open) => {
          if (!open && !remove.isPending) setDeleting(null)
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>删除连接配置？</DialogTitle>
            <DialogDescription>
              将移除“{deleting?.name}
              ”的连接配置。源数据库和其中的数据不会被删除。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleting(null)}
              disabled={remove.isPending}
            >
              取消
            </Button>
            <Button
              variant="destructive"
              disabled={remove.isPending}
              onClick={() => deleting && remove.mutate(deleting)}
            >
              {remove.isPending && <Loader2 className="size-4 animate-spin" />}
              删除连接
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
