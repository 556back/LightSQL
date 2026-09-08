import { createFileRoute } from "@tanstack/react-router"
import { QueryPage } from "@/components/Queries/QueryPage"

export const Route = createFileRoute("/_layout/queries")({
  component: QueryPage,
  head: () => ({ meta: [{ title: "查询验证 · LightSQL" }] }),
})
