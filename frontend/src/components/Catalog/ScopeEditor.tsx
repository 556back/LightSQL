import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Loader2, Search } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"
import { type CatalogPublic, CatalogService, type ObjectRef } from "@/client"
import { errorMessage } from "@/components/DataSources/shared"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"

export const objectKey = (ref: ObjectRef) =>
  JSON.stringify([ref.schema_name, ref.name, ref.kind])

export function ScopeEditor({
  catalog,
  onClose,
}: {
  catalog: CatalogPublic
  onClose: () => void
}) {
  const qc = useQueryClient()
  const [selected, setSelected] = useState(catalog.scope)
  const [schema, setSchema] = useState("")
  const [search, setSearch] = useState("")
  const [syncAfterSave, setSyncAfterSave] = useState(true)
  const path = { source_id: catalog.source_id }
  const schemas = useQuery({
    queryKey: ["catalog-schemas", catalog.source_id, catalog.source_revision],
    queryFn: async () => (await CatalogService.listSchemas({ path })).data,
  })
  const activeSchema = schema || schemas.data?.[0] || ""
  const discovery = useQuery({
    queryKey: [
      "catalog-discover",
      catalog.source_id,
      catalog.source_revision,
      activeSchema,
    ],
    queryFn: async () =>
      (
        await CatalogService.discoverObjects({
          path,
          query: { schema_name: activeSchema },
        })
      ).data,
    enabled: !!activeSchema,
  })
  const shown = (discovery.data ?? []).filter((r) =>
    r.name.toLowerCase().includes(search.toLowerCase()),
  )
  const selectedKeys = new Set(selected.map(objectKey))
  const save = useMutation({
    mutationFn: () =>
      CatalogService.saveScope({
        path,
        body: {
          expected_revision: catalog.revision,
          expected_source_revision: catalog.source_revision,
          objects: selected,
        },
      }),
    onSuccess: async () => {
      qc.invalidateQueries({ queryKey: ["catalog", catalog.source_id] })
      qc.invalidateQueries({ queryKey: ["topic-catalog", catalog.source_id] })
      if (syncAfterSave && selected.length > 0) {
        try {
          await CatalogService.syncCatalog({ path })
          qc.invalidateQueries({
            queryKey: ["catalog-jobs", catalog.source_id],
          })
          toast.success("数据表已保存，正在同步字段和关联")
        } catch (error) {
          toast.error(
            `选表已保存，但同步未启动：${errorMessage(error)}。请点击“更新表结构”重试。`,
          )
        }
      } else {
        toast.success(
          selected.length
            ? "数据表已保存，可稍后更新表结构"
            : "已清空选表范围，现有目录已隐藏",
        )
      }
      onClose()
    },
    onError: (e) => toast.error(errorMessage(e)),
  })
  function toggle(ref: ObjectRef) {
    setSelected((prev) =>
      selectedKeys.has(objectKey(ref))
        ? prev.filter((r) => objectKey(r) !== objectKey(ref))
        : [...prev, ref],
    )
  }
  return (
    <Dialog
      open
      onOpenChange={(open) => {
        if (!open && !save.isPending) onClose()
      }}
    >
      <DialogContent className="sm:max-w-[780px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>选择数据表</DialogTitle>
          <DialogDescription>
            勾选要用于分析的表和视图，保存后自动读取字段和关联。这里只读取结构，不复制业务数据。
          </DialogDescription>
        </DialogHeader>
        {catalog.needs_confirmation && (
          <p className="rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
            连接配置已变化，请检查当前数据库的对象并重新保存范围。
          </p>
        )}
        <fieldset
          disabled={save.isPending}
          className="grid min-w-0 gap-4 sm:grid-cols-[minmax(0,1fr)_240px]"
        >
          <legend className="sr-only">可用数据表与已选范围</legend>
          <div className="space-y-3">
            <label
              className="block text-sm font-medium"
              htmlFor="schema-select"
            >
              数据表所在分组（Schema）
            </label>
            <select
              id="schema-select"
              className="h-10 w-full rounded-md border bg-background px-3 text-sm"
              value={activeSchema}
              onChange={(e) => setSchema(e.target.value)}
              disabled={schemas.isPending}
            >
              {!schemas.data?.length && (
                <option value="">
                  {schemas.isPending ? "正在读取模式…" : "没有可见模式"}
                </option>
              )}
              {schemas.data?.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
            <div className="relative">
              <Search className="absolute left-3 top-3 size-4 text-muted-foreground" />
              <Input
                className="pl-9"
                aria-label="搜索可选对象"
                placeholder="搜索表或视图名称"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            {schemas.isError || discovery.isError ? (
              <div
                role="alert"
                className="rounded-lg border p-4 text-sm text-destructive"
              >
                {errorMessage(schemas.error ?? discovery.error)}
                <Button
                  variant="link"
                  onClick={() => {
                    schemas.refetch()
                    discovery.refetch()
                  }}
                >
                  重新读取
                </Button>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{shown.length} 个可选对象</span>
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={!shown.length}
                    onClick={() =>
                      setSelected((prev) => [
                        ...prev,
                        ...shown.filter((r) => !selectedKeys.has(objectKey(r))),
                      ])
                    }
                  >
                    选择当前列表
                  </Button>
                </div>
                <div className="h-64 overflow-y-auto rounded-lg border divide-y">
                  {discovery.isFetching ? (
                    <p className="flex gap-2 p-5 text-sm text-muted-foreground">
                      <Loader2 className="size-4 animate-spin" />
                      读取结构中…
                    </p>
                  ) : shown.length ? (
                    shown.map((ref) => (
                      <label
                        key={objectKey(ref)}
                        className="flex cursor-pointer items-center gap-3 px-4 py-3 hover:bg-muted/40"
                      >
                        <input
                          type="checkbox"
                          className="size-4 accent-primary"
                          checked={selectedKeys.has(objectKey(ref))}
                          onChange={() => toggle(ref)}
                        />
                        <span className="min-w-0 flex-1 break-all font-mono text-sm">
                          {ref.name}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {ref.kind === "view" ? "视图" : "表"}
                        </span>
                      </label>
                    ))
                  ) : (
                    <p className="p-5 text-sm text-muted-foreground">
                      没有匹配的对象，请检查模式、搜索条件和数据库授权。
                    </p>
                  )}
                </div>
              </>
            )}
          </div>
          <div className="rounded-lg border bg-muted/20 p-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium">
                已选择 {selected.length} / 200
              </h3>
              <Button size="sm" variant="ghost" onClick={() => setSelected([])}>
                清空
              </Button>
            </div>
            <div className="mt-3 max-h-80 space-y-2 overflow-y-auto">
              {selected.map((ref) => (
                <div
                  key={objectKey(ref)}
                  className="flex items-start gap-2 rounded-md border bg-background p-2 text-xs"
                >
                  <span className="flex-1 break-all">
                    <span className="text-muted-foreground">
                      {ref.schema_name}.
                    </span>
                    {ref.name}
                  </span>
                  <button
                    type="button"
                    className="text-muted-foreground hover:text-destructive"
                    aria-label={`移除 ${ref.schema_name}.${ref.name}`}
                    onClick={() => toggle(ref)}
                  >
                    ×
                  </button>
                </div>
              ))}
              {!selected.length && (
                <p className="py-6 text-xs leading-6 text-muted-foreground">
                  从左侧选择需要理解的业务表。
                  <br />
                  保存空范围会立即隐藏现有目录。
                </p>
              )}
            </div>
          </div>
        </fieldset>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={syncAfterSave}
            disabled={save.isPending || !selected.length}
            onChange={(e) => setSyncAfterSave(e.target.checked)}
          />
          保存后立即同步表结构
        </label>
        {!selected.length && catalog.scope.length > 0 && (
          <p role="alert" className="rounded-lg bg-amber-500/10 p-3 text-sm">
            保存空范围会隐藏现有目录，引用这些表的主题需要重新检查。
          </p>
        )}
        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={save.isPending}>
            取消
          </Button>
          <Button
            onClick={() => save.mutate()}
            disabled={save.isPending || selected.length > 200}
          >
            {save.isPending && <Loader2 className="size-4 animate-spin" />}
            {save.isPending
              ? "正在保存…"
              : syncAfterSave && selected.length
                ? "保存并同步"
                : "保存选表范围"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
