import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Check, Loader2 } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"
import {
  type DataSourceCreateWritable,
  type DataSourcePublic,
  DatasourcesService,
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
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  DatabaseIcon,
  databaseLabel,
  errorMessage,
  type Kind,
  kinds,
} from "./shared"

export function SourceEditor({
  source,
  onClose,
}: {
  source: DataSourcePublic | null
  onClose: () => void
}) {
  const queryClient = useQueryClient()
  const [form, setForm] = useState<DataSourceCreateWritable>({
    name: source?.name ?? "",
    database_type: source?.database_type ?? "postgresql",
    host: source?.host ?? "",
    port: source?.port ?? 5432,
    database: source?.database ?? "",
    username: source?.username ?? "",
    password: "",
    description: source?.description ?? "",
    tls_mode: source?.tls_mode ?? "verify-full",
    enabled: source?.enabled ?? true,
  })
  const [error, setError] = useState("")
  const set = <K extends keyof DataSourceCreateWritable>(
    key: K,
    value: DataSourceCreateWritable[K],
  ) => setForm((prev) => ({ ...prev, [key]: value }))
  const save = useMutation({
    mutationFn: async () =>
      source
        ? DatasourcesService.updateDatasource({
            path: { source_id: source.id },
            body: {
              ...form,
              password: form.password || undefined,
              expected_revision: source.revision,
            },
          })
        : DatasourcesService.createDatasource({ body: form }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["datasources"] })
      toast.success(
        source ? "连接配置已更新" : "数据源已添加，可以开始测试连接",
      )
      onClose()
    },
    onError: (err) => setError(errorMessage(err)),
  })
  return (
    <Dialog
      open
      onOpenChange={(open) => {
        if (!open && !save.isPending) onClose()
      }}
    >
      <DialogContent className="max-h-[92vh] overflow-y-auto sm:max-w-[620px]">
        <DialogHeader>
          <DialogTitle className="text-xl">
            {source ? "编辑数据源" : "连接新的数据源"}
          </DialogTitle>
          <DialogDescription>
            配置数据库连接，建立数据分析的第一步。
          </DialogDescription>
        </DialogHeader>
        <form
          className="space-y-5 pt-2"
          onSubmit={(event) => {
            event.preventDefault()
            setError("")
            save.mutate()
          }}
        >
          <fieldset disabled={save.isPending}>
            <legend className="mb-3 text-sm font-medium">数据库类型</legend>
            <div className="grid grid-cols-3 gap-3">
              {(Object.keys(kinds) as Kind[]).map((kind) => (
                <button
                  key={kind}
                  type="button"
                  aria-pressed={form.database_type === kind}
                  className={`relative flex flex-col items-center gap-2 rounded-xl border p-3 transition-colors ${form.database_type === kind ? "border-primary bg-primary/5 ring-1 ring-primary" : "hover:bg-muted"}`}
                  onClick={() =>
                    setForm((prev) => ({
                      ...prev,
                      database_type: kind,
                      port: kinds[kind].port,
                    }))
                  }
                >
                  <DatabaseIcon kind={kind} small />
                  <span className="text-sm font-medium">
                    {kinds[kind].label}
                  </span>
                  {form.database_type === kind && (
                    <Check className="absolute right-2 top-2 size-3.5 text-primary" />
                  )}
                </button>
              ))}
            </div>
          </fieldset>
          {form.database_type === "kingbase" && (
            <p className="text-xs leading-5 text-muted-foreground">
              当前支持金仓 PostgreSQL 兼容模式，其他兼容模式暂未验证。
            </p>
          )}
          <div className="space-y-2">
            <Label htmlFor="source-name">显示名称</Label>
            <Input
              id="source-name"
              placeholder="例如 经营分析数据库"
              value={form.name}
              onChange={(e) => set("name", e.target.value)}
              maxLength={80}
              required
              disabled={save.isPending}
            />
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="source-host">主机地址</Label>
              <Input
                id="source-host"
                value={form.host}
                onChange={(e) => set("host", e.target.value)}
                placeholder="例如 db.internal 或 10.0.1.20"
                required
                disabled={save.isPending}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="source-port">端口</Label>
              <Input
                id="source-port"
                type="number"
                min={1}
                max={65535}
                value={form.port || ""}
                onChange={(e) => set("port", Number(e.target.value))}
                required
                disabled={save.isPending}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="source-database">
                {databaseLabel(form.database_type)}
              </Label>
              <Input
                id="source-database"
                value={form.database}
                onChange={(e) => set("database", e.target.value)}
                placeholder={
                  form.database_type === "oracle"
                    ? "例如 FREEPDB1"
                    : form.database_type === "dameng"
                      ? "例如 LIGHT_DEMO"
                      : "例如 analytics"
                }
                required
                disabled={save.isPending}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="source-username">数据库账号</Label>
              <Input
                id="source-username"
                value={form.username}
                onChange={(e) => set("username", e.target.value)}
                placeholder="建议使用专用只读账号"
                required
                disabled={save.isPending}
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="source-password">
              连接密码{" "}
              {source && (
                <span className="font-normal text-muted-foreground">
                  （留空保留原密码）
                </span>
              )}
            </Label>
            <Input
              id="source-password"
              type="password"
              autoComplete="new-password"
              value={form.password}
              onChange={(e) => set("password", e.target.value)}
              required={!source}
              maxLength={1024}
              disabled={save.isPending}
              placeholder={
                source ? "已安全保存，不会显示原密码" : "请输入数据库密码"
              }
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="source-description">
              备注{" "}
              <span className="font-normal text-muted-foreground">
                （选填）
              </span>
            </Label>
            <Input
              id="source-description"
              value={form.description}
              onChange={(e) => set("description", e.target.value)}
              maxLength={500}
              placeholder="描述用途，方便后续识别"
              disabled={save.isPending}
            />
          </div>
          <label className="flex cursor-pointer items-start gap-3 rounded-lg border bg-muted/30 p-3">
            <input
              type="checkbox"
              className="mt-1 accent-[var(--primary)]"
              checked={form.tls_mode === "verify-full"}
              onChange={(e) =>
                set("tls_mode", e.target.checked ? "verify-full" : "disable")
              }
              disabled={save.isPending}
            />
            <span>
              <span className="text-sm font-medium">
                启用 TLS 并验证服务器证书
              </span>
              <span className="mt-1 block text-xs text-muted-foreground">
                {form.database_type === "dameng"
                  ? "达梦证书校验尚未适配，开启时会拒绝连接。仅在可信本地测试环境中关闭此项。"
                  : "本地无 TLS 的演示数据库可关闭此项。"}
              </span>
            </span>
          </label>
          {error && (
            <div
              role="alert"
              className="rounded-lg bg-destructive/10 px-4 py-3 text-sm text-destructive"
            >
              {error}
            </div>
          )}
          <DialogFooter className="border-t pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={save.isPending}
            >
              取消
            </Button>
            <Button type="submit" disabled={save.isPending}>
              {save.isPending && <Loader2 className="size-4 animate-spin" />}
              {source ? "保存修改" : "保存连接"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
