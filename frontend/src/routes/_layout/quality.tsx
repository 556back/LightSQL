import { createFileRoute, redirect } from "@tanstack/react-router"
import { UsersService } from "@/client"
import { QualityPage } from "@/components/Quality/QualityPage"

export const Route = createFileRoute("/_layout/quality")({
  component: QualityPage,
  beforeLoad: async () => {
    if (!(await UsersService.readUserMe()).data.is_superuser)
      throw redirect({ to: "/" })
  },
  head: () => ({ meta: [{ title: "质量与运维 · LightSQL" }] }),
})
