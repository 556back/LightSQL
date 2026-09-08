import { useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import type { ConversationPublic, QueryJobPublic } from "@/client"

type Snapshot = { conversation: ConversationPublic; jobs: QueryJobPublic[] }

export function useConversationStream(id: string) {
  const qc = useQueryClient()
  const [state, setState] = useState("正在连接进度流…")
  const [error, setError] = useState("")
  const [jobs, setJobs] = useState<QueryJobPublic[]>([])
  useEffect(() => {
    const controller = new AbortController()
    let timer: ReturnType<typeof setTimeout> | undefined
    let stopped = false
    const fail = (message: string) => {
      stopped = true
      setError(message)
      qc.removeQueries({ queryKey: ["conversation", id] })
      qc.removeQueries({ queryKey: ["query-result"] })
      qc.removeQueries({ queryKey: ["answer-evidence", id] })
      qc.invalidateQueries({ queryKey: ["conversations"] })
    }
    const connect = async () => {
      try {
        const base = (import.meta.env.VITE_API_URL ?? "").replace(/\/+$/, "")
        const response = await fetch(
          `${base}/api/v1/assistant/conversations/${id}/events`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
            },
            signal: controller.signal,
            cache: "no-store",
          },
        )
        if ([401, 403, 404, 409, 410, 422].includes(response.status)) {
          const body = await response.json()
          fail(
            typeof body.detail === "string"
              ? body.detail
              : "会话已不可访问，请重新登录或新建会话",
          )
          return
        }
        if (!response.ok || !response.body)
          throw new Error("stream unavailable")
        setState("进度实时同步")
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ""
        try {
          while (!stopped) {
            const part = await reader.read()
            if (part.done) break
            buffer += decoder
              .decode(part.value, { stream: true })
              .replace(/\r\n/g, "\n")
            let end = buffer.indexOf("\n\n")
            while (end >= 0) {
              const frame = buffer.slice(0, end)
              buffer = buffer.slice(end + 2)
              const event = frame
                .split("\n")
                .find((line) => line.startsWith("event: "))
                ?.slice(7)
              const text = frame
                .split("\n")
                .filter((line) => line.startsWith("data: "))
                .map((line) => line.slice(6))
                .join("\n")
              if (event === "access_error") {
                fail(JSON.parse(text).detail)
                break
              }
              if (event === "snapshot") {
                const data = JSON.parse(text) as Snapshot
                qc.setQueryData(["conversation", id], data.conversation)
                for (const job of data.jobs)
                  qc.setQueryData(["query-job", job.id], job)
                setJobs(data.jobs)
                qc.invalidateQueries({ queryKey: ["conversations"] })
              }
              end = buffer.indexOf("\n\n")
            }
          }
        } finally {
          await reader.cancel()
        }
      } catch {
        if (!controller.signal.aborted) setState("连接中断，正在恢复最新进度…")
      }
      if (!stopped && !controller.signal.aborted)
        timer = setTimeout(connect, 1500)
    }
    void connect()
    return () => {
      stopped = true
      controller.abort()
      clearTimeout(timer)
    }
  }, [id, qc])
  return { state, error, jobs }
}
