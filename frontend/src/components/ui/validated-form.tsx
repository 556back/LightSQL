import { type ComponentProps, useEffect, useId, useState } from "react"

type FieldElement = HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
type FieldError = { field: FieldElement; message: string }

function fieldError(field: FieldElement): string {
  const label =
    field.labels?.[0]?.textContent?.trim() ||
    field.getAttribute("aria-label") ||
    field.name ||
    "此项"
  if (field.validity.valueMissing) return `请填写${label}`
  if (field.validity.typeMismatch) return `${label}格式不正确，请检查后重试`
  if (field.validity.rangeUnderflow)
    return `${label}不能小于 ${field.getAttribute("min")}`
  if (field.validity.rangeOverflow)
    return `${label}不能大于 ${field.getAttribute("max")}`
  return `请检查${label}的格式或取值`
}

/** Adapts existing domain constraints into localized, inline validation. */
export function ValidatedForm({
  children,
  onSubmit,
  onInput,
  ...props
}: ComponentProps<"form">) {
  const errorId = useId()
  const [errors, setErrors] = useState<FieldError[]>([])

  useEffect(() => {
    const previous = errors.map(({ field }, index) => {
      const invalid = field.getAttribute("aria-invalid")
      const description = field.getAttribute("aria-describedby")
      field.setAttribute("aria-invalid", "true")
      field.setAttribute(
        "aria-describedby",
        [description, `${errorId}-${index}`].filter(Boolean).join(" "),
      )
      return () => {
        if (invalid === null) field.removeAttribute("aria-invalid")
        else field.setAttribute("aria-invalid", invalid)
        if (description === null) field.removeAttribute("aria-describedby")
        else field.setAttribute("aria-describedby", description)
      }
    })
    return () => {
      for (const restore of previous) restore()
    }
  }, [errors, errorId])

  return (
    <form
      {...props}
      noValidate
      onInput={(event) => {
        setErrors((current) =>
          current.filter(({ field }) => !field.validity.valid),
        )
        onInput?.(event)
      }}
      onSubmit={(event) => {
        const invalid = Array.from(event.currentTarget.elements)
          .filter(
            (field): field is FieldElement =>
              field instanceof HTMLInputElement ||
              field instanceof HTMLSelectElement ||
              field instanceof HTMLTextAreaElement,
          )
          .filter((field) => field.willValidate && !field.validity.valid)
          .map((field) => ({ field, message: fieldError(field) }))
        setErrors(invalid)
        if (invalid.length) {
          event.preventDefault()
          invalid[0].field.focus()
          return
        }
        onSubmit?.(event)
      }}
    >
      {children}
      {errors.length > 0 && (
        <div
          role="alert"
          className="rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive"
        >
          {errors.map(({ field, message }, index) => (
            <p id={`${errorId}-${index}`} key={field.id || field.name || index}>
              {message}
            </p>
          ))}
        </div>
      )}
    </form>
  )
}
