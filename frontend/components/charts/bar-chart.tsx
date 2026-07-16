"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface BarDataPoint {
  label: string;
  value: number;
  color?: string;
}

interface BarChartProps {
  data?: BarDataPoint[];
  className?: string;
  title?: string;
  horizontal?: boolean;
  maxValue?: number;
}

const defaultData: BarDataPoint[] = [
  { label: "Mon", value: 42 },
  { label: "Tue", value: 58 },
  { label: "Wed", value: 61 },
  { label: "Thu", value: 73 },
  { label: "Fri", value: 95 },
  { label: "Sat", value: 38 },
  { label: "Sun", value: 21 },
];

export function BarChart({ data = defaultData, className, maxValue, horizontal = false }: BarChartProps) {
  if (horizontal) {
    return <HorizontalBarChart data={data} className={className} maxValue={maxValue} />;
  }

  const W = 700;
  const H = 220;
  const padL = 44;
  const padR = 16;
  const padT = 16;
  const padB = 36;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;

  const max = maxValue ?? Math.max(...data.map((d) => d.value)) * 1.2;
  const n = data.length;
  const groupW = plotW / n;
  const barW = Math.min(groupW * 0.55, 52);

  const yLabels = [0, Math.round(max * 0.25), Math.round(max * 0.5), Math.round(max * 0.75), Math.round(max)];

  function barX(i: number) {
    return padL + i * groupW + (groupW - barW) / 2;
  }
  function barY(v: number) {
    return padT + plotH - (v / max) * plotH;
  }
  function barH(v: number) {
    return (v / max) * plotH;
  }

  return (
    <div className={cn("w-full", className)}>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ minHeight: 140 }}>
        <defs>
          <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="hsl(217 91% 60%)" stopOpacity="0.9" />
            <stop offset="100%" stopColor="hsl(217 91% 60%)" stopOpacity="0.4" />
          </linearGradient>
        </defs>

        {/* Y grid */}
        {yLabels.map((val) => {
          const y = barY(val);
          return (
            <g key={val}>
              <line
                x1={padL}
                y1={y}
                x2={W - padR}
                y2={y}
                stroke="hsl(217 32% 14%)"
                strokeWidth="1"
                strokeDasharray={val === 0 ? "none" : "4 4"}
              />
              <text x={padL - 6} y={y + 4} textAnchor="end" fontSize="10" fill="hsl(215 20% 40%)">
                {val}
              </text>
            </g>
          );
        })}

        {/* Bars */}
        {data.map((d, i) => {
          const h = barH(d.value);
          const y = barY(d.value);
          const x = barX(i);
          return (
            <g key={d.label}>
              <rect x={x} y={y} width={barW} height={h} rx="4" fill="url(#barGrad)" />
              {/* Value label on top */}
              <text x={x + barW / 2} y={y - 4} textAnchor="middle" fontSize="10" fill="hsl(215 20% 55%)" fontWeight="500">
                {d.value}
              </text>
              {/* X label */}
              <text
                x={padL + i * groupW + groupW / 2}
                y={H - 8}
                textAnchor="middle"
                fontSize="11"
                fill="hsl(215 20% 45%)"
              >
                {d.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

function HorizontalBarChart({
  data,
  className,
  maxValue,
}: {
  data: BarDataPoint[];
  className?: string;
  maxValue?: number;
}) {
  const max = maxValue ?? Math.max(...data.map((d) => d.value));
  const colors = [
    "hsl(217 91% 60%)",
    "hsl(0 72% 60%)",
    "hsl(38 92% 55%)",
    "hsl(160 84% 39%)",
    "hsl(270 67% 64%)",
    "hsl(199 89% 52%)",
  ];

  return (
    <div className={cn("space-y-3", className)}>
      {data.map((d, i) => {
        const pct = (d.value / max) * 100;
        return (
          <div key={d.label} className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">{d.label}</span>
              <span className="font-medium tabular-nums">{d.value.toLocaleString()}</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-muted/50">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{ width: `${pct}%`, backgroundColor: d.color ?? colors[i % colors.length] }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
