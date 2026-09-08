import { Link as RouterLink, useRouterState } from "@tanstack/react-router"
import type { LucideIcon } from "lucide-react"

import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"

export type Item = {
  icon: LucideIcon
  title: string
  path: string
}

interface MainProps {
  items: Item[]
  label?: string
}

export function Main({ items, label }: MainProps) {
  const { isMobile, setOpenMobile } = useSidebar()
  const router = useRouterState()
  const currentPath = router.location.pathname

  const handleMenuClick = () => {
    if (isMobile) {
      setOpenMobile(false)
    }
  }

  return (
    <SidebarGroup className="px-3 py-2">
      {label && (
        <p className="px-3 pb-2 pt-3 text-xs font-medium text-muted-foreground group-data-[collapsible=icon]:hidden">
          {label}
        </p>
      )}
      <SidebarGroupContent>
        <SidebarMenu>
          {items.map((item) => {
            const isActive =
              currentPath === item.path ||
              currentPath.startsWith(`${item.path}/`)

            return (
              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton
                  tooltip={item.title}
                  isActive={isActive}
                  className="h-10 rounded-lg px-3 text-sm data-[active=true]:bg-primary/10 data-[active=true]:text-primary data-[active=true]:font-semibold"
                  asChild
                >
                  <RouterLink to={item.path} onClick={handleMenuClick}>
                    <item.icon />
                    <span>{item.title}</span>
                  </RouterLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
            )
          })}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  )
}
