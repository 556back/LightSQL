import type { ReactNode } from "react"

export function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string
  title: string
  description: string
  action?: ReactNode
}) {
  return (
    <div className="page-heading flex flex-wrap items-end justify-between gap-4">
      <div className="max-w-2xl">
        <p className="page-eyebrow">{eyebrow}</p>
        <h1 className="page-title">{title}</h1>
        <p className="mt-3 text-sm leading-7 text-muted-foreground">
          {description}
        </p>
      </div>
      {action}
    </div>
  )
}
