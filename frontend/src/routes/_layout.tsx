import {
  createFileRoute,
  Link,
  Outlet,
  redirect,
  useRouterState,
} from "@tanstack/react-router"
import { ArrowUpRight } from "lucide-react"

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
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded-lg focus:bg-card focus:p-3"
      >
        跳转到主要内容
      </a>
      <AppSidebar />
      <SidebarInset className="min-w-0">
        <header className="sticky top-0 z-10 flex h-[72px] shrink-0 items-center gap-3 border-b bg-card/95 px-4 backdrop-blur sm:px-8">
          <SidebarTrigger className="-ml-1 text-muted-foreground" />
          <span className="h-4 border-l" />
          <span className="hidden text-sm text-muted-foreground sm:inline">
            工作空间
          </span>
          <span className="hidden text-muted-foreground/40 sm:inline">/</span>
          <span className="text-sm font-medium">{pageTitle}</span>
          <Link
            to="/ask"
            className="ml-auto flex items-center gap-2 rounded-lg px-3 py-2 text-xs text-primary hover:bg-accent"
          >
            进入问数 <ArrowUpRight className="size-3.5" />
          </Link>
        </header>
        <div
          id="main-content"
          tabIndex={-1}
          className="app-content min-w-0 flex-1 p-4 sm:p-6 lg:p-8"
        >
          <div className="mx-auto w-full max-w-[1440px]">
            <Outlet />
          </div>
        </div>
        <Footer />
      </SidebarInset>
    </SidebarProvider>
  )
}
