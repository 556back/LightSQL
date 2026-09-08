import { createFileRoute } from "@tanstack/react-router"
import { AskPage } from "@/components/Assistant/AskPage"

export const Route = createFileRoute("/_layout/ask")({
  validateSearch: (
    search: Record<string, unknown>,
  ): { topic?: string; conversation?: string } => ({
    topic: typeof search.topic === "string" ? search.topic : undefined,
    conversation:
      typeof search.conversation === "string" ? search.conversation : undefined,
  }),
  component: AskPage,
  head: () => ({ meta: [{ title: "智能问数 · LightSQL" }] }),
})
