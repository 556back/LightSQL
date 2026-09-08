import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useBlocker } from "@tanstack/react-router"
import { Plus, Save, Trash2 } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"
import {
  type PolicyPublic,
  type PublishedTopic,
  QueriesService,
  type QueryGrant,
  TopicsService,
  type UserPublic,
  UsersService,
} from "@/client"
import { control, errorMessage, Field } from "@/components/Semantic/shared"
import { Button } from "@/components/ui/button"

type ScopeModel = {
  id: string
  label: string
  columns: { name: string; data_type: string }[]
}

export function PolicyEditor({ topicId }: { topicId: string }) {
  const data = useQuery({
    queryKey: ["query-policy", topicId],
    queryFn: async () => {
      const [policy, topic, members, users] = await Promise.all([
        QueriesService.getPolicy({ path: { topic_id: topicId } }),
        TopicsService.getPublishedTopic({ path: { topic_id: topicId } }),
        TopicsService.getTopic({ path: { topic_id: topicId } }),
        UsersService.readUsers({ query: { limit: 1000 } }),
      ])
      return {
        policy: policy.data,
        topic: topic.data,
        users:
          users.data?.data.filter((u) =>
            members.data?.member_ids.includes(u.id),
          ) || [],
      }
    },
  })
  if (data.isError)
    return (
      <p
        role="alert"
        className="rounded-xl border p-4 text-sm text-destructive"
      >
        {errorMessage(data.error)}
      </p>
    )
  if (!data.data?.policy || !data.data.topic) return <p>正在加载查询授权…</p>
  return (
    <PolicyForm
      key={`${topicId}-${data.data.policy.revision}`}
      topic={data.data.topic}
      initial={data.data.policy}
      users={data.data.users}
    />
  )
}

function PolicyForm({
  topic,
  initial,
  users,
}: {
  topic: PublishedTopic
  initial: PolicyPublic
  users: UserPublic[]
}) {
  const qc = useQueryClient()
  const [grants, setGrants] = useState<QueryGrant[]>(initial.grants)
  const [selected, setSelected] = useState(users[0]?.id || "")
  const [saved, setSaved] = useState(JSON.stringify(initial.grants))
  const models = initial.models as ScopeModel[]
  const current = grants.find((g) => g.user_id === selected)
  const dirty = JSON.stringify(grants) !== saved
  useBlocker({
    shouldBlockFn: () =>
      dirty && !window.confirm("查询授权尚未保存，确定离开？"),
    enableBeforeUnload: dirty,
  })
  const save = useMutation({
    mutationFn: () =>
      QueriesService.savePolicy({
        path: { topic_id: topic.id },
        body: { expected_revision: initial.revision, grants },
      }),
    onSuccess: () => {
      setSaved(JSON.stringify(grants))
      qc.invalidateQueries({ queryKey: ["query-policy", topic.id] })
      qc.invalidateQueries({ queryKey: ["query-catalog", topic.id] })
      toast.success("查询授权已保存")
    },
  })
  function update(patch: Partial<QueryGrant>) {
    setGrants((values) =>
      values.map((g) => (g.user_id === selected ? { ...g, ...patch } : g)),
    )
  }
  return (
    <section className="space-y-4 rounded-xl border border-primary/30 bg-card p-5">
      <div className="flex flex-wrap justify-between gap-3">
        <div>
          <h2 className="font-semibold">成员查询授权</h2>
          <p className="mt-1 text-xs leading-5 text-muted-foreground">
            绑定发布 v{topic.version}
            。成员资格用于查看主题；执行查询还需显式授权指标、维度与行范围。保存后立即生效。
          </p>
        </div>
        <Button
          size="sm"
          onClick={() => save.mutate()}
          disabled={save.isPending || (!dirty && !initial.stale)}
        >
          <Save className="size-4" />
          保存授权
        </Button>
      </div>
      {initial.stale && (
        <p role="alert" className="rounded-md bg-amber-500/10 p-3 text-sm">
          语义版本已更新，现有查询授权已失效。请检查并重新保存。
        </p>
      )}
      {save.isError && (
        <p
          role="alert"
          className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive"
        >
          {errorMessage(save.error)}
        </p>
      )}
      <Field label="选择主题成员">
        <select
          aria-label="查询授权成员"
          value={selected}
          className={`${control} max-w-lg`}
          onChange={(e) => setSelected(e.target.value)}
        >
          <option value="">选择成员</option>
          {users.map((u) => (
            <option key={u.id} value={u.id}>
              {u.full_name || u.email} ·{" "}
              {grants.some((g) => g.user_id === u.id) ? "已配置" : "未授权查询"}
            </option>
          ))}
        </select>
      </Field>
      {!users.length && (
        <p className="text-sm text-muted-foreground">
          请先在业务主题中添加成员。
        </p>
      )}
      {selected && !current && (
        <Button
          size="sm"
          variant="outline"
          onClick={() =>
            setGrants((values) => [
              ...values,
              {
                user_id: selected,
                metric_ids: topic.metrics.map((m) => m.id),
                dimension_ids: topic.dimensions.map((d) => d.id),
                unrestricted: false,
                rows: [],
              },
            ])
          }
        >
          <Plus className="size-4" />
          为此成员配置查询授权
        </Button>
      )}
      {current && (
        <>
          <div className="grid gap-4 lg:grid-cols-2">
            <Field label="允许指标">
              <div className="flex flex-wrap gap-3">
                {topic.metrics.map((m) => (
                  <label
                    key={m.id}
                    className="flex items-center gap-2 text-xs font-normal"
                  >
                    <input
                      type="checkbox"
                      checked={current.metric_ids?.includes(m.id) || false}
                      onChange={() =>
                        update({
                          metric_ids: current.metric_ids?.includes(m.id)
                            ? current.metric_ids.filter((id) => id !== m.id)
                            : [...(current.metric_ids || []), m.id],
                        })
                      }
                    />
                    {m.label}
                  </label>
                ))}
              </div>
            </Field>
            <Field label="允许分组与过滤维度">
              <div className="flex flex-wrap gap-3">
                {topic.dimensions.map((d) => (
                  <label
                    key={d.id}
                    className="flex items-center gap-2 text-xs font-normal"
                  >
                    <input
                      type="checkbox"
                      checked={current.dimension_ids?.includes(d.id)}
                      onChange={() =>
                        update({
                          dimension_ids: current.dimension_ids?.includes(d.id)
                            ? current.dimension_ids.filter((id) => id !== d.id)
                            : [...(current.dimension_ids || []), d.id],
                        })
                      }
                    />
                    {d.label}
                  </label>
                ))}
              </div>
            </Field>
          </div>
          <Field label="自由探索表字段（独立于指标授权，包含明细查询）">
            <div className="space-y-3">
              {models.map((model) => (
                <div key={model.id} className="rounded-md border p-3">
                  <p className="mb-2 text-sm">{model.label}</p>
                  <div className="flex flex-wrap gap-3">
                    {model.columns.map((column) => (
                      <label
                        key={column.name}
                        className="flex items-center gap-2 text-xs font-normal"
                      >
                        <input
                          type="checkbox"
                          checked={
                            !!current.exploration
                              ?.find((a) => a.model_id === model.id)
                              ?.columns.includes(column.name)
                          }
                          onChange={(e) => {
                            const access = current.exploration || []
                            const selectedColumns =
                              access.find((a) => a.model_id === model.id)
                                ?.columns || []
                            const columns = e.target.checked
                              ? [...selectedColumns, column.name]
                              : selectedColumns.filter((c) => c !== column.name)
                            update({
                              exploration: [
                                ...access.filter(
                                  (a) => a.model_id !== model.id,
                                ),
                                ...(columns.length
                                  ? [{ model_id: model.id, columns }]
                                  : []),
                              ],
                            })
                          }}
                        />
                        {column.name}
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </Field>
          <Field label="行级访问范围">
            <select
              aria-label="行级访问范围"
              className={`${control} max-w-lg`}
              value={current.unrestricted ? "all" : "restricted"}
              onChange={(e) =>
                update({ unrestricted: e.target.value === "all", rows: [] })
              }
            >
              <option value="restricted">仅限指定组织 / 租户行</option>
              <option value="all">显式允许全部已授权数据行</option>
            </select>
          </Field>
          {!current.unrestricted && (
            <div className="space-y-2">
              <p className="text-xs text-muted-foreground">
                每个指标的基础模型都要配置范围。多个规则取交集，同一规则中的多个值取并集。
              </p>
              {current.rows?.map((row, index) => (
                <div
                  key={`${selected}-${index}`}
                  className="flex flex-wrap gap-2"
                >
                  <select
                    aria-label="授权模型"
                    className={`${control} flex-1`}
                    value={row.model_id}
                    onChange={(e) =>
                      update({
                        rows: current.rows?.map((r, i) =>
                          i === index
                            ? {
                                ...r,
                                model_id: e.target.value,
                                column:
                                  models.find((m) => m.id === e.target.value)
                                    ?.columns[0].name || "",
                              }
                            : r,
                        ),
                      })
                    }
                  >
                    {models.map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.label}
                      </option>
                    ))}
                  </select>
                  <select
                    aria-label="授权字段"
                    className={`${control} flex-1`}
                    value={row.column}
                    onChange={(e) =>
                      update({
                        rows: current.rows?.map((r, i) =>
                          i === index ? { ...r, column: e.target.value } : r,
                        ),
                      })
                    }
                  >
                    {models
                      .find((m) => m.id === row.model_id)
                      ?.columns.map((c) => (
                        <option key={c.name} value={c.name}>
                          {c.name} ({c.data_type})
                        </option>
                      ))}
                  </select>
                  <input
                    aria-label="授权值"
                    className={`${control} flex-[2]`}
                    value={row.values.join(",")}
                    placeholder="允许的编码，英文逗号分隔"
                    onChange={(e) =>
                      update({
                        rows: current.rows?.map((r, i) =>
                          i === index
                            ? { ...r, values: e.target.value.split(",") }
                            : r,
                        ),
                      })
                    }
                  />
                  <Button
                    size="icon"
                    variant="ghost"
                    aria-label="删除行范围"
                    onClick={() =>
                      update({
                        rows: current.rows?.filter((_, i) => i !== index),
                      })
                    }
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </div>
              ))}
              <Button
                size="sm"
                variant="outline"
                onClick={() =>
                  update({
                    rows: [
                      ...(current.rows || []),
                      {
                        model_id: models[0].id,
                        column: models[0].columns[0].name,
                        values: [""],
                      },
                    ],
                  })
                }
              >
                <Plus className="size-4" />
                添加行范围
              </Button>
            </div>
          )}
          <Button
            size="sm"
            variant="ghost"
            className="text-destructive"
            onClick={() =>
              setGrants((values) =>
                values.filter((g) => g.user_id !== selected),
              )
            }
          >
            撤销此成员查询授权（保存后生效）
          </Button>
        </>
      )}
    </section>
  )
}
