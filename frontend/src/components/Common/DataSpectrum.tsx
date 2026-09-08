import { cn } from "@/lib/utils"

/** A decorative projection of data paths; never a chart or live measurement. */
export function DataSpectrum({ className }: { className?: string }) {
  return (
    <svg
      className={cn("data-spectrum", className)}
      viewBox="0 0 560 320"
      fill="none"
      aria-hidden="true"
    >
      <g className="spectrum-grid" stroke="currentColor" strokeWidth="0.6">
        {[80, 140, 200, 260].map((y) => (
          <path key={y} d={`M20 ${y}H540`} />
        ))}
        {[80, 160, 240, 320, 400, 480].map((x) => (
          <path key={x} d={`M${x} 30V290`} />
        ))}
      </g>
      <g stroke="currentColor" strokeWidth="1.3">
        {Array.from({ length: 18 }, (_, i) => (
          <path
            key={i}
            opacity={0.25 + i * 0.035}
            d={`M-20 ${245 - i * 5} C100 ${300 - i * 8}, 170 ${35 + i * 6}, 280 ${110 + i * 5} S420 ${290 - i * 9}, 580 ${40 + i * 7}`}
          />
        ))}
      </g>
      <g fill="currentColor">
        <circle cx="160" cy="170" r="4" />
        <circle cx="320" cy="160" r="4" />
        <circle cx="480" cy="120" r="4" />
      </g>
      <g stroke="currentColor" opacity="0.4">
        <circle cx="160" cy="170" r="12" />
        <circle cx="320" cy="160" r="12" />
        <circle cx="480" cy="120" r="12" />
      </g>
    </svg>
  )
}
