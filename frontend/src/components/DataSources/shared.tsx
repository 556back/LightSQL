import { AxiosError } from "axios"
import type { DataSourceCreate, DataSourcePublic } from "@/client"

export type Kind = DataSourceCreate["database_type"]
export const kinds: Record<
  Kind,
  { label: string; initial: string; port: number; color: string }
> = {
  postgresql: {
    label: "PostgreSQL",
    initial: "P",
    port: 5432,
    color: "bg-sky-50 text-sky-700 dark:bg-sky-950 dark:text-sky-300",
  },
  mysql: {
    label: "MySQL",
    initial: "M",
    port: 3306,
    color: "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
  },
  oracle: {
    label: "Oracle",
    initial: "O",
    port: 1521,
    color: "bg-rose-50 text-rose-600 dark:bg-rose-950 dark:text-rose-300",
  },
  dameng: {
    label: "达梦 DM8",
    initial: "D",
    port: 5236,
    color:
      "bg-violet-50 text-violet-700 dark:bg-violet-950 dark:text-violet-300",
  },
  kingbase: {
    label: "人大金仓",
    initial: "K",
    port: 54321,
    color: "bg-teal-50 text-teal-700 dark:bg-teal-950 dark:text-teal-300",
  },
}
export function databaseLabel(kind: Kind) {
  return kind === "oracle"
    ? "Service Name"
    : kind === "dameng"
      ? "默认模式（Schema）"
      : "数据库名称"
}
export function errorMessage(error: unknown) {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail
    if (typeof detail === "string") return detail
    if (Array.isArray(detail)) return detail.map((item) => item.msg).join("；")
  }
  return "请求未完成，请检查网络后重试"
}
export function dateLabel(value: string | null) {
  return value
    ? new Date(value).toLocaleString("zh-CN", {
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
      })
    : "尚未测试"
}
export function Status({ source }: { source: DataSourcePublic }) {
  const status = !source.enabled ? "disabled" : source.status
  const style =
    status === "connected"
      ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
      : status === "error"
        ? "bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-300"
        : "bg-muted text-muted-foreground"
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium ${style}`}
    >
      <span className="size-1.5 rounded-full bg-current" />
      {status === "connected"
        ? "连接正常"
        : status === "error"
          ? "连接异常"
          : status === "disabled"
            ? "已停用"
            : "待测试"}
    </span>
  )
}
export function DatabaseIcon({
  kind,
  small = false,
}: {
  kind: Kind
  small?: boolean
}) {
  return (
    <span
      className={`inline-flex shrink-0 items-center justify-center rounded-xl border border-current/5 font-mono font-semibold ${small ? "size-9 text-lg" : "size-11 text-xl"} ${kinds[kind].color}`}
    >
      {kinds[kind].initial}
    </span>
  )
}
