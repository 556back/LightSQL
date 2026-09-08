import {
  createFileRoute,
  Outlet,
  redirect,
  useRouterState,
} from "@tanstack/react-router"

import { Footer } from "@/components/Common/Footer"
import AppSidebar from "@/components/Sidebar/AppSidebar"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
      })
    }
  },
})

function Layout() {
  const pathname = useRouterState({
    select: (state) => state.location.pathname,
  })
  const pageTitle =
    (
      {
        ask: "智能问数",
        topics: "业务主题",
        catalog: "数据表目录",
        datasources: "数据库连接",
        queries: "查询验证",
        models: "模型设置",
        integrations: "外部系统接入",
        quality: "质量与运维",
        admin: "用户管理",
        settings: "个人设置",
      } as Record<string, string>
    )[pathname.split("/")[1]] ?? "工作空间"
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="min-w-0">
        <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-3 border-b bg-card/95 px-4 backdrop-blur sm:px-8">
          <SidebarTrigger className="-ml-1 text-muted-foreground" />
          <span className="h-4 border-l" />
          <span className="hidden text-sm text-muted-foreground sm:inline">
            工作空间
          </span>
          <span className="hidden text-muted-foreground/40 sm:inline">/</span>
          <span className="text-sm font-medium">{pageTitle}</span>
          <span className="ml-auto rounded-md border px-2 py-1 text-[10px] text-muted-foreground">
            内部系统
          </span>
        </header>
        <div className="app-content min-w-0 flex-1 p-4 sm:p-6 lg:p-8">
          <div className="mx-auto w-full max-w-[1440px]">
            <Outlet />
          </div>
        </div>
        <Footer />
      </SidebarInset>
    </SidebarProvider>
  )
}
