import type { AnalysisPublic, QueryResult } from "@/client"

export type Task = {
  task_id: string
  topic_id: string
  conversation_id: string | null
  revision: number
  status: string
  message: string
  question: string
  expires_at: string
  clarification?: {
    message: string
    ambiguities: { mention: string; options: { id: string; label: string }[] }[]
  }
}
export type Result = QueryResult & {
  chart: string
  semantic_version: number
  analysis: AnalysisPublic | null
  analysis_status: string
  evidence: Record<string, unknown> | null
  expires_at: string
}
export class IntegrationError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message)
  }
}
export function createIntegrationApi(token: () => string) {
  return async function api<T>(
    path: string,
    body?: unknown,
    method = body === undefined ? "GET" : "POST",
    key?: string,
  ): Promise<T> {
    const response = await fetch(`/api/integration/v1${path}`, {
      method,
      cache: "no-store",
      credentials: "omit",
      headers: {
        Authorization: `Bearer ${token()}`,
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...(key ? { "Idempotency-Key": key } : {}),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    })
    const data = await response.json()
    if (!response.ok)
      throw new IntegrationError(response.status, data.message || "请求失败")
    return data as T
  }
}
