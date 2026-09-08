import { Link } from "@tanstack/react-router"
import {
  ArrowRight,
  Database,
  Layers3,
  MessageSquare,
  Table2,
} from "lucide-react"

const steps = [
  {
    path: "/datasources",
    icon: Database,
    title: "连接数据库",
    hint: "数据从哪里来",
  },
  {
    path: "/catalog",
    icon: Table2,
    title: "选择数据表",
    hint: "有哪些表和字段",
  },
  {
    path: "/topics",
    icon: Layers3,
    title: "整理业务主题",
    hint: "选表、定义业务含义",
  },
  {
    path: "/ask",
    icon: MessageSquare,
    title: "开始问数",
    hint: "用自然语言提问",
  },
] as const

export function DataJourney({ current }: { current: string }) {
  return (
    <nav
      aria-label="数据准备流程"
      className="grid grid-cols-2 gap-2 rounded-xl border bg-card p-2 lg:grid-cols-4"
    >
      {steps.map((step, index) => (
        <Link
          key={step.path}
          to={step.path}
          aria-current={current === step.path ? "step" : undefined}
          className={`flex min-w-0 items-center gap-3 rounded-lg p-3 transition-colors ${current === step.path ? "bg-primary/8 text-primary" : "text-muted-foreground hover:bg-muted"}`}
        >
          <step.icon className="size-5 shrink-0" />
          <span className="min-w-0 flex-1">
            <span className="block text-sm font-medium">
              {index + 1}. {step.title}
            </span>
            <span className="mt-1 block text-xs text-muted-foreground">
              {step.hint}
            </span>
          </span>
          {index < 3 && (
            <ArrowRight className="hidden size-3 shrink-0 xl:block" />
          )}
        </Link>
      ))}
    </nav>
  )
}
