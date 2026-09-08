import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Link, useNavigate, useSearch } from "@tanstack/react-router"
import { ArrowRight, Layers3, MessageSquare, Plus, Search } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"
import { DatasourcesService, TopicsService } from "@/client"
import { DataJourney } from "@/components/Common/DataJourney"
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
import { control, errorMessage, Field, Status } from "./shared"

export function TopicsPage() {
  const intent = useSearch({ from: "/_layout/topics/" })
  const { user } = useAuth()
  const navigate = useNavigate()
  const cache = useQueryClient()
  const [search, setSearch] = useState("")
  const [status, setStatus] = useState("all")
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState({
    name: "",
    description: "",
    owner: "",
    source_id: "",
  })
  const topics = useQuery({
    queryKey: ["topics"],
    queryFn: async () => (await TopicsService.listTopics()).data,
  })
  const sources = useQuery({
    queryKey: ["datasources"],
    queryFn: async () => (await DatasourcesService.listDatasources()).data,
    enabled: !!user?.is_superuser,
  })
  const create = useMutation({
    mutationFn: async () =>
      (await TopicsService.createTopic({ body: form })).data,
    onSuccess: (topic) => {
      cache.invalidateQueries({ queryKey: ["topics"] })
      setCreating(false)
      navigate({ to: "/topics/$topicId", params: { topicId: topic.id } })
    },
    onError: (e) => toast.error(errorMessage(e)),
  })
  const list = (topics.data ?? []).filter(
    (t) =>
      `${t.name} ${t.description} ${t.source_name ?? ""}`
        .toLowerCase()
        .includes(search.trim().toLowerCase()) &&
      (status === "all" ||
        (status === "ready"
          ? t.availability === "ready"
          : t.availability !== "ready")),
  )
  return (
    <div className="space-y-7">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="mb-2 text-[11px] tracking-[0.16em] text-muted-foreground">
            业务数据空间
          </p>
          <h1 className="text-2xl font-semibold tracking-tight">业务主题</h1>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            {user?.is_superuser
              ? "把相关数据表整理为一个分析范围，例如「销售经营」。发布后，大家就能围绕它提问。"
              : "选择你要分析的业务范围，开始提问，或查看指标的计算口径。"}
          </p>
        </div>
        {user?.is_superuser && (
          <Button
            onClick={() => {
              const enabled =
                sources.data?.data.filter((source) => source.enabled) ?? []
              setForm({
                name: "",
                description: "",
                owner: user?.full_name || "",
                source_id:
                  enabled.find((source) => source.id === intent.source)?.id ??
                  (enabled.length === 1 ? enabled[0].id : ""),
              })
              setCreating(true)
            }}
          >
            <Plus className="size-4" />
            新建主题
          </Button>
        )}
      </div>
      {user?.is_superuser && <DataJourney current="/topics" />}
      {user?.is_superuser &&
        sources.data?.data.some(
          (source) => source.id === intent.source && source.enabled,
        ) && (
          <p className="rounded-lg border border-primary/20 bg-primary/5 px-4 py-3 text-sm">
            已从「
            {
              sources.data.data.find((source) => source.id === intent.source)
                ?.name
            }
            」进入。点击“新建主题”时会自动选择这个数据库。
          </p>
        )}
      <div className="grid grid-cols-3 divide-x rounded-xl border bg-card py-5">
        {[
          ["业务主题", topics.data?.length ?? 0],
          [
            "已发布可用",
            topics.data?.filter((t) => t.availability === "ready").length ?? 0,
          ],
          [
            "指标定义",
            topics.data?.reduce((n, t) => n + t.metric_count, 0) ?? 0,
          ],
        ].map(([label, count]) => (
          <div key={label} className="px-4 sm:px-6">
            <p className="text-xs text-muted-foreground">{label}</p>
            <p className="mt-2 text-2xl font-semibold tabular-nums">{count}</p>
          </div>
        ))}
      </div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <fieldset
          className="flex gap-1 rounded-lg border bg-card p-1"
          aria-label="主题状态筛选"
        >
          {[
            ["all", "全部主题"],
            ["ready", "可开始问数"],
            ["pending", "待完善"],
          ].map(([value, label]) => (
            <Button
              key={value}
              size="sm"
              variant={status === value ? "secondary" : "ghost"}
              aria-pressed={status === value}
              onClick={() => setStatus(value)}
            >
              {label}
            </Button>
          ))}
        </fieldset>
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
          <input
            aria-label="搜索主题"
            className={`${control} pl-9`}
            placeholder="搜索主题名称或说明"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>
      {topics.isPending ? (
        <p className="text-sm text-muted-foreground">正在加载业务主题…</p>
      ) : topics.isError ? (
        <div role="alert" className="rounded-xl border p-6">
          <p>{errorMessage(topics.error)}</p>
          <Button
            variant="outline"
            className="mt-3"
            onClick={() => topics.refetch()}
          >
            重试
          </Button>
        </div>
      ) : !list.length ? (
        <div className="rounded-xl border border-dashed bg-card px-6 py-16 text-center">
          <Layers3 className="mx-auto mb-4 size-8 text-muted-foreground" />
          <h2 className="font-medium">
            {search || status !== "all"
              ? "没有匹配的主题"
              : user?.is_superuser
                ? "创建第一个业务主题"
                : "暂无已授权的业务主题"}
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            {search || status !== "all"
              ? "换个关键词或清除筛选，查看其他主题。"
              : user?.is_superuser
                ? "新建主题后，按步骤选择数据表、添加分析维度，再按需要定义指标。"
                : "请联系管理员分配已发布主题的访问权限。"}
          </p>
          {(search || status !== "all") && (
            <Button
              className="mt-4"
              variant="outline"
              onClick={() => {
                setSearch("")
                setStatus("all")
              }}
            >
              清除筛选
            </Button>
          )}
        </div>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {list.map((topic) => (
            <article
              key={topic.id}
              className="group flex min-w-0 flex-col gap-4 rounded-xl border bg-card p-5 shadow-xs transition-shadow hover:shadow-md sm:p-6"
            >
              <div className="flex items-start justify-between gap-3">
                <span className="rounded-lg bg-primary/8 p-2.5 text-primary">
                  <Layers3 className="size-5" />
                </span>
                <Status value={topic.availability} />
              </div>
              <div>
                <h2 className="text-lg font-semibold">
                  <Link
                    to="/topics/$topicId"
                    params={{ topicId: topic.id }}
                    className="hover:text-primary"
                  >
                    {topic.name}
                  </Link>
                </h2>
                <p className="mt-2 line-clamp-2 text-sm leading-6 text-muted-foreground">
                  {topic.description || "尚未填写主题说明"}
                </p>
              </div>
              <div className="mt-auto flex flex-wrap items-center gap-x-4 gap-y-2 border-t pt-4 text-xs text-muted-foreground">
                <span>{topic.metric_count} 个指标</span>
                <span>{topic.dimension_count} 个维度</span>
                <span>
                  {topic.current_version
                    ? `版本 v${topic.current_version}`
                    : "待发布"}
                </span>
              </div>
              {topic.source_name && (
                <p className="truncate text-xs text-muted-foreground">
                  数据源 · {topic.source_name}
                </p>
              )}
              <div className="flex flex-wrap items-center justify-between gap-2">
                <Button variant="outline" size="sm" asChild>
                  <Link to="/topics/$topicId" params={{ topicId: topic.id }}>
                    {user?.is_superuser ? "配置主题" : "查看业务口径"}
                    <ArrowRight className="size-3.5" />
                  </Link>
                </Button>
                {topic.availability === "ready" ? (
                  <Button size="sm" asChild>
                    <Link to="/ask" search={{ topic: topic.id }}>
                      <MessageSquare className="size-3.5" />
                      开始问数
                    </Link>
                  </Button>
                ) : (
                  <span className="text-xs text-muted-foreground">
                    {topic.availability === "disabled"
                      ? "启用后可继续配置"
                      : topic.availability === "needs_review"
                        ? "检查数据变化并重新发布"
                        : "完成配置后发布"}
                  </span>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
      <Dialog
        open={creating}
        onOpenChange={(open) => !create.isPending && setCreating(open)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>新建业务主题</DialogTitle>
            <DialogDescription>
              例如「销售经营」包含订单和客户数据。先填写基本信息，下一步选择要分析的数据表。
            </DialogDescription>
          </DialogHeader>
          <form
            className="space-y-4"
            onSubmit={(e) => {
              e.preventDefault()
              create.mutate()
            }}
          >
            {(
              [
                ["name", "主题名称"],
                ["owner", "业务责任人"],
              ] as const
            ).map(([key, label]) => (
              <Field key={key} label={label}>
                <input
                  aria-label={label}
                  className={control}
                  required
                  maxLength={key === "name" ? 80 : 120}
                  value={form[key]}
                  placeholder={
                    key === "name"
                      ? "例如：销售经营、库存分析"
                      : "负责确认业务含义的人"
                  }
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                />
              </Field>
            ))}
            <Field
              label="绑定数据源"
              hint="一个主题使用一个数据库，创建后不可更换。"
            >
              <select
                aria-label="绑定数据源"
                className={control}
                required
                value={form.source_id}
                onChange={(e) =>
                  setForm({ ...form, source_id: e.target.value })
                }
              >
                <option value="">请选择已启用的数据源</option>
                {sources.data?.data
                  .filter((s) => s.enabled)
                  .map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name}
                    </option>
                  ))}
              </select>
            </Field>
            {sources.isError && (
              <p role="alert" className="text-sm text-destructive">
                数据源加载失败，请关闭后重试。
              </p>
            )}
            {!sources.isPending &&
              !sources.isError &&
              !sources.data?.data.some((source) => source.enabled) && (
                <p className="text-sm text-muted-foreground">
                  暂无可用数据库。
                  <Link to="/datasources" className="text-primary underline">
                    先添加数据库连接
                  </Link>
                </p>
              )}
            <Field label="主题说明">
              <textarea
                aria-label="主题说明"
                className={control}
                maxLength={500}
                rows={3}
                placeholder="例如：分析订单金额、客户分布和销售趋势"
                value={form.description}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
              />
            </Field>
            <DialogFooter>
              <Button
                variant="outline"
                type="button"
                onClick={() => setCreating(false)}
                disabled={create.isPending}
              >
                取消
              </Button>
              <Button
                type="submit"
                disabled={create.isPending || !form.source_id}
              >
                {create.isPending ? "创建中…" : "创建并选择数据表"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
