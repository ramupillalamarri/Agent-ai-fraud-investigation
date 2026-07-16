"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface DonutSegment {
  label: string;
  value: number;
  color: string;
}

interface DonutChartProps {
  data?: DonutSegment[];
  className?: string;
  centerLabel?: string;
  centerSublabel?: string;
  size?: number;
}

const defaultData: DonutSegment[] = [
  { label: "Card Fraud", value: 38, color: "hsl(0 72% 60%)" },
  { label: "Account Takeover", value: 24, color: "hsl(25 95% 58%)" },
  { label: "Identity Theft", value: 18, color: "hsl(43 96% 56%)" },
  { label: "Return Fraud", value: 12, color: "hsl(270 67% 64%)" },
  { label: "Other", value: 8, color: "hsl(215 20% 45%)" },
];

export function DonutChart({
  data = defaultData,
  className,
  centerLabel,
  centerSublabel,
  size = 200,
}: DonutChartProps) {
  const total = data.reduce((sum, d) => sum + d.value, 0);
  const r = 70;
  const circumference = 2 * Math.PI * r;
  const cx = size / 2;
  const cy = size / 2;

  let cumulative = 0;
  const segments = data.map((d) => {
    const fraction = d.value / total;
    const dashLen = fraction * circumference;
    // dashOffset: start from top (circumference/4 offset), minus cumulative
    const dashOffset = circumference / 4 - cumulative * circumference;
    cumulative += fraction;
    return { ...d, dashLen, dashOffset, fraction };
  });

  return (
    <div className={cn("flex flex-col items-center gap-4", className)}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg viewBox={`0 0 ${size} ${size}`} width={size} height={size}>
          {/* Track */}
          <circle cx={cx} cy={cy} r={r} fill="none" stroke="hsl(217 32% 12%)" strokeWidth="28" />
          {/* Segments */}
          {segments.map((seg) => (
            <circle
              key={seg.label}
              cx={cx}
              cy={cy}
              r={r}
              fill="none"
              stroke={seg.color}
              strokeWidth="28"
              strokeDasharray={`${seg.dashLen} ${circumference}`}
              strokeDashoffset={seg.dashOffset}
              strokeLinecap="butt"
            />
          ))}
        </svg>
        {/* Center text */}
        {centerLabel && (
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-xl font-bold leading-none">{centerLabel}</span>
            {centerSublabel && (
              <span className="mt-1 text-[11px] text-muted-foreground">{centerSublabel}</span>
            )}
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="w-full space-y-2">
        {data.map((d) => {
          const pct = Math.round((d.value / total) * 100);
          return (
            <div key={d.label} className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: d.color }} />
                <span className="text-muted-foreground">{d.label}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-medium tabular-nums">{pct}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
