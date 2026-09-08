import { createFileRoute } from "@tanstack/react-router"
import { IntegrationAdmin } from "@/components/Integration/IntegrationAdmin"

export const Route = createFileRoute("/_layout/integrations")({
  component: IntegrationAdmin,
  head: () => ({ meta: [{ title: "外部系统接入 · LightSQL" }] }),
})
