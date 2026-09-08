import { useState } from "react"
import type { QueryResult } from "@/client"
import { control } from "@/components/Semantic/shared"

export function ResultChart({
  result,
  preferred = "auto",
}: {
  result: QueryResult
  preferred?: string
}) {
  const numeric = result.columns
    .map((c, i) => ({ ...c, i }))
    .filter((c) => c.value_type === "number")
  const [kind, setKind] = useState(preferred === "auto" ? "bar" : preferred)
  const [x, setX] = useState(
    Math.max(
      0,
      result.columns.findIndex((c) => c.value_type !== "number"),
    ),
  )
  const [chosenY, setY] = useState(-1)
  const y = chosenY >= 0 ? chosenY : (numeric[0]?.i ?? -1)
  if (!numeric.length || !result.rows.length) return null
  const points = result.rows
    .slice(0, 40)
    .map((r, i) => ({
      label: String(r[x] ?? "NULL"),
      raw: r[y],
      value: r[y] === null ? null : Number(r[y]),
      i,
    }))
  const valid = points.filter(
    (p) => p.value !== null && Number.isFinite(p.value),
  )
  const min = Math.min(0, ...valid.map((p) => p.value as number))
  const max = Math.max(0, ...valid.map((p) => p.value as number))
  const scale = (v: number) => 215 - ((v - min) / (max - min || 1)) * 185
  const atX = (i: number) => 65 + ((i + 0.5) * 620) / points.length
  return (
    <div className="mb-5 space-y-3 rounded-lg border p-4">
      <div className="flex flex-wrap gap-3">
        <label className="text-xs">
          展示方式
          <select
            aria-label="图表类型"
            className={control}
            value={kind}
            onChange={(e) => setKind(e.target.value)}
          >
            <option value="bar">柱状图</option>
            <option value="line">折线图</option>
            <option value="table">仅表格</option>
          </select>
        </label>
        <label className="text-xs">
          分类 / 时间
          <select
            aria-label="图表横轴"
            className={control}
            value={x}
            onChange={(e) => setX(Number(e.target.value))}
          >
            {result.columns.map((c, i) => (
              <option key={c.id} value={i}>
                {c.label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs">
          数值
          <select
            aria-label="图表数值"
            className={control}
            value={y}
            onChange={(e) => setY(Number(e.target.value))}
          >
            {numeric.map((c) => (
              <option key={c.id} value={c.i}>
                {c.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      {kind !== "table" && (
        <>
          <svg
            viewBox="0 0 740 290"
            role="img"
            aria-label={`${result.columns[y]?.label} ${kind === "line" ? "折线图" : "柱状图"}`}
            className="w-full min-w-0"
          >
            <line
              x1="65"
              x2="690"
              y1={scale(0)}
              y2={scale(0)}
              stroke="currentColor"
              opacity="0.3"
            />
            <text
              x="60"
              y="25"
              textAnchor="end"
              fontSize="11"
              fill="currentColor"
            >
              {max.toLocaleString(undefined, { maximumSignificantDigits: 5 })}
            </text>
            <text
              x="60"
              y="220"
              textAnchor="end"
              fontSize="11"
              fill="currentColor"
            >
              {min.toLocaleString(undefined, { maximumSignificantDigits: 5 })}
            </text>
            {points.map((p) => {
              const previous = points[p.i - 1]
              return (
                <g key={p.i}>
                  {p.value !== null && Number.isFinite(p.value) && (
                    <>
                      {kind === "line" ? (
                        <>
                          {previous?.value !== null &&
                            previous?.value !== undefined &&
                            Number.isFinite(previous.value) && (
                              <line
                                x1={atX(p.i - 1)}
                                y1={scale(previous.value)}
                                x2={atX(p.i)}
                                y2={scale(p.value)}
                                stroke="#2563eb"
                                strokeWidth="2"
                              />
                            )}
                          <circle
                            cx={atX(p.i)}
                            cy={scale(p.value)}
                            r="4"
                            fill="#2563eb"
                          >
                            <title>
                              {p.label}: {String(p.raw)}
                            </title>
                          </circle>
                        </>
                      ) : (
                        <rect
                          x={atX(p.i) - 220 / points.length}
                          y={Math.min(scale(0), scale(p.value))}
                          width={440 / points.length}
                          height={Math.max(
                            1,
                            Math.abs(scale(0) - scale(p.value)),
                          )}
                          rx="2"
                          fill={p.value < 0 ? "#e11d48" : "#2563eb"}
                        >
                          <title>
                            {p.label}: {String(p.raw)}
                          </title>
                        </rect>
                      )}
                    </>
                  )}
                  {p.i % Math.max(1, Math.ceil(points.length / 8)) === 0 && (
                    <text
                      x={atX(p.i)}
                      y="245"
                      textAnchor="middle"
                      fontSize="11"
                      fill="currentColor"
                    >
                      {p.label.length > 12
                        ? `${p.label.slice(0, 12)}…`
                        : p.label}
                    </text>
                  )}
                </g>
              )
            })}
            <text
              x="370"
              y="277"
              textAnchor="middle"
              fontSize="12"
              fill="currentColor"
            >
              {result.columns[x]?.label} / {result.columns[y]?.label}
            </text>
          </svg>
          <p className="text-xs text-muted-foreground">
            图表按查询返回顺序展示前 {points.length}{" "}
            行，未再次合并同名分类；悬停查看原值。NULL
            留空，精确数值以表格为准。{result.truncated && "查询结果已截断。"}
          </p>
        </>
      )}
    </div>
  )
}
