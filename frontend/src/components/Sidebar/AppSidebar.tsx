import {
  Activity,
  BookOpen,
  Cpu,
  Database,
  Layers3,
  MessageSquare,
  Play,
  Plug,
  Users,
} from "lucide-react"

import { SidebarAppearance } from "@/components/Common/Appearance"
import { Logo } from "@/components/Common/Logo"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
import { type Item, Main } from "./Main"
import { User } from "./User"

const baseItems: Item[] = [
  { icon: MessageSquare, title: "智能问数", path: "/ask" },
  { icon: Layers3, title: "业务主题", path: "/topics" },
  { icon: Play, title: "查询验证", path: "/queries" },
]

export function AppSidebar() {
  const { user: currentUser } = useAuth()

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-6 py-6 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:items-center">
        <Logo variant="responsive" />
      </SidebarHeader>
      <SidebarContent>
        <Main label="探索与分析" items={baseItems} />
        {currentUser?.is_superuser && (
          <>
            <Main
              label="数据准备"
              items={[
                { icon: Database, title: "数据库连接", path: "/datasources" },
                { icon: BookOpen, title: "数据表目录", path: "/catalog" },
              ]}
            />
            <Main
              label="系统管理"
              items={[
                { icon: Cpu, title: "模型设置", path: "/models" },
                { icon: Plug, title: "外部系统接入", path: "/integrations" },
                { icon: Activity, title: "质量与运维", path: "/quality" },
                { icon: Users, title: "用户管理", path: "/admin" },
              ]}
            />
          </>
        )}
        <div className="mx-4 mt-auto mb-6 rounded-lg border bg-background p-3 group-data-[collapsible=icon]:hidden">
          <p className="text-xs font-medium">从数据到答案</p>
          <p className="mt-1 text-[11px] leading-5 text-muted-foreground">
            选好业务主题，用一句话开始分析。
          </p>
        </div>
      </SidebarContent>
      <SidebarFooter>
        <SidebarAppearance />
        <User user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
