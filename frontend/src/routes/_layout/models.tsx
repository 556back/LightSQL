import { createFileRoute, redirect } from "@tanstack/react-router"
import { UsersService } from "@/client"
import { ModelSettings } from "@/components/Assistant/ModelSettings"

export const Route = createFileRoute("/_layout/models")({
  component: ModelSettings,
  beforeLoad: async () => {
    if (!(await UsersService.readUserMe()).data.is_superuser)
      throw redirect({ to: "/" })
  },
  head: () => ({ meta: [{ title: "模型设置 · LightSQL" }] }),
})
