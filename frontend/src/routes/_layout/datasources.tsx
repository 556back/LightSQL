import { createFileRoute } from "@tanstack/react-router"
import { DataSourcesPage } from "@/components/DataSources/DataSourcesPage"

export const Route = createFileRoute("/_layout/datasources")({
  component: DataSourcesPage,
  head: () => ({ meta: [{ title: "数据库连接 · LightSQL" }] }),
})
