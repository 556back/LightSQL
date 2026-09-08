import { Link } from "@tanstack/react-router"
import { Layers2 } from "lucide-react"
import { cn } from "@/lib/utils"

export function Logo({
  variant = "full",
  className,
  asLink = true,
}: {
  variant?: "full" | "icon" | "responsive"
  className?: string
  asLink?: boolean
}) {
  const content = (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <span className="flex size-8 shrink-0 items-center justify-center rounded-[10px] bg-primary text-primary-foreground">
        <Layers2 className="size-5" />
      </span>
      {variant !== "icon" && (
        <span
          className={cn(
            "text-xl font-semibold tracking-tight",
            variant === "responsive" && "group-data-[collapsible=icon]:hidden",
          )}
        >
          Light<span className="font-normal text-primary">SQL</span>
        </span>
      )}
    </span>
  )
  return asLink ? (
    <Link to="/" aria-label="LightSQL 首页">
      {content}
    </Link>
  ) : (
    content
  )
}
