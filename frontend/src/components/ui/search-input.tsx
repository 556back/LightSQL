import { Search, X } from "lucide-react"
import { useRef } from "react"
import { cn } from "@/lib/utils"
import { Input } from "./input"

export function SearchInput({
  value,
  onValueChange,
  label,
  placeholder,
  className,
}: {
  value: string
  onValueChange: (value: string) => void
  label: string
  placeholder: string
  className?: string
}) {
  const ref = useRef<HTMLInputElement>(null)
  return (
    <div className={cn("relative min-w-0", className)}>
      <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        ref={ref}
        aria-label={label}
        value={value}
        onChange={(event) => onValueChange(event.target.value)}
        placeholder={placeholder}
        className="h-10 bg-card pl-9 pr-10"
      />
      {value && (
        <button
          type="button"
          aria-label={`清除${label}`}
          title={`清除${label}`}
          className="absolute right-1 top-1/2 flex size-8 -translate-y-1/2 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground"
          onClick={() => {
            onValueChange("")
            ref.current?.focus()
          }}
        >
          <X className="size-4" />
        </button>
      )}
    </div>
  )
}
