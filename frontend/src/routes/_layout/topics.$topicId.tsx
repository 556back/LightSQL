import { createFileRoute } from "@tanstack/react-router"
import { TopicWorkspace } from "@/components/Semantic/TopicWorkspace"
export const Route = createFileRoute("/_layout/topics/$topicId")({
  component: Page,
  head: () => ({ meta: [{ title: "主题工作台 · LightSQL" }] }),
})
function Page() {
  const { topicId } = Route.useParams()
  return <TopicWorkspace topicId={topicId} />
}
