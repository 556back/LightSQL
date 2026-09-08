import { createFileRoute } from "@tanstack/react-router"
import { TopicsPage } from "@/components/Semantic/TopicsPage"
export const Route = createFileRoute("/_layout/topics/")({
  validateSearch: (search: Record<string, unknown>): { source?: string } => ({
    source: typeof search.source === "string" ? search.source : undefined,
  }),
  component: TopicsPage,
  head: () => ({ meta: [{ title: "业务主题 · LightSQL" }] }),
})
