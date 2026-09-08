import { createFileRoute } from "@tanstack/react-router"
import { CatalogPage } from "@/components/Catalog/CatalogPage"

export const Route = createFileRoute("/_layout/catalog")({
  validateSearch: (search: Record<string, unknown>): { source?: string } => ({
    source: typeof search.source === "string" ? search.source : undefined,
  }),
  component: CatalogPage,
  head: () => ({ meta: [{ title: "数据表目录 · LightSQL" }] }),
})
