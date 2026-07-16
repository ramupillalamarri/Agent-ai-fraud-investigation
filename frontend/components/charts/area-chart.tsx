"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface DataPoint {
  label: string;
  value: number;
  secondary?: number;
}

interface AreaChartProps {
  data?: DataPoint[];
  className?: string;
  showSecondary?: boolean;
  primaryLabel?: string;
  secondaryLabel?: string;
  primaryColor?: string;
  secondaryColor?: string;
}

const defaultData: DataPoint[] = [
  { label: "Jan", value: 45, secondary: 12 },
  { label: "Feb", value: 52, secondary: 15 },
  { label: "Mar", value: 61, secondary: 18 },
  { label: "Apr", value: 58, secondary: 16 },
  { label: "May", value: 73, secondary: 22 },
  { label: "Jun", value: 89, secondary: 28 },
  { label: "Jul", value: 102, secondary: 31 },
  { label: "Aug", value: 95, secondary: 29 },
  { label: "Sep", value: 118, secondary: 38 },
  { label: "Oct", value: 134, secondary: 42 },
  { label: "Nov", value: 127, secondary: 39 },
  { label: "Dec", value: 142, secondary: 45 },
];

export function AreaChart({
  data = defaultData,
  className,
  showSecondary = true,
  primaryLabel = "Fraud Cases",
  secondaryLabel = "Flagged",
}: AreaChartProps) {
  const W = 860;
  const H = 220;
  const padL = 52;
  const padR = 20;
  const padT = 20;
  const padB = 40;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;

  const maxVal = Math.max(...data.map((d) => d.value)) * 1.15;
  const n = data.length;

  function px(i: number) {
    return padL + (i / (n - 1)) * plotW;
  }
  function py(v: number) {
    return padT + plotH - (v / maxVal) * plotH;
  }

  // Build smooth path using cubic bezier
  function buildPath(values: number[], close = false): string {
    const pts = values.map((v, i) => ({ x: px(i), y: py(v) }));
    let d = `M ${pts[0].x} ${pts[0].y}`;
    for (let i = 1; i < pts.length; i++) {
      const prev = pts[i - 1];
      const curr = pts[i];
      const cx1 = prev.x + (curr.x - prev.x) * 0.4;
      const cy1 = prev.y;
      const cx2 = curr.x - (curr.x - prev.x) * 0.4;
      const cy2 = curr.y;
      d += ` C ${cx1} ${cy1}, ${cx2} ${cy2}, ${curr.x} ${curr.y}`;
    }
    if (close) {
      d += ` L ${pts[pts.length - 1].x} ${padT + plotH} L ${pts[0].x} ${padT + plotH} Z`;
    }
    return d;
  }

  const primaryValues = data.map((d) => d.value);
  const secondaryValues = data.map((d) => d.secondary ?? 0);
  const yGridLabels = [0, Math.round(maxVal * 0.25), Math.round(maxVal * 0.5), Math.round(maxVal * 0.75), Math.round(maxVal)];

  return (
    <div className={cn("w-full", className)}>
      {/* Legend */}
      <div className="mb-3 flex items-center gap-4 px-2">
        <div className="flex items-center gap-1.5">
          <div className="h-2.5 w-2.5 rounded-full bg-blue-500" />
          <span className="text-xs text-muted-foreground">{primaryLabel}</span>
        </div>
        {showSecondary && (
          <div className="flex items-center gap-1.5">
            <div className="h-2.5 w-2.5 rounded-full bg-red-400" />
            <span className="text-xs text-muted-foreground">{secondaryLabel}</span>
          </div>
        )}
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ height: "100%", minHeight: 160 }}>
        <defs>
          <linearGradient id="primaryGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="hsl(217 91% 60%)" stopOpacity="0.25" />
            <stop offset="100%" stopColor="hsl(217 91% 60%)" stopOpacity="0.01" />
          </linearGradient>
          <linearGradient id="secondaryGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="hsl(0 72% 51%)" stopOpacity="0.15" />
            <stop offset="100%" stopColor="hsl(0 72% 51%)" stopOpacity="0.01" />
          </linearGradient>
        </defs>

        {/* Y-axis grid lines + labels */}
        {yGridLabels.map((val) => {
          const y = py(val);
          return (
            <g key={val}>
              <line
                x1={padL}
                y1={y}
                x2={W - padR}
                y2={y}
                stroke="hsl(217 32% 14%)"
                strokeWidth="1"
                strokeDasharray="4 4"
              />
              <text x={padL - 6} y={y + 4} textAnchor="end" fontSize="10" fill="hsl(215 20% 40%)">
                {val >= 1000 ? `${(val / 1000).toFixed(1)}k` : val}
              </text>
            </g>
          );
        })}

        {/* X-axis labels */}
        {data.map((d, i) => (
          <text
            key={d.label}
            x={px(i)}
            y={H - 8}
            textAnchor="middle"
            fontSize="10"
            fill="hsl(215 20% 40%)"
          >
            {d.label}
          </text>
        ))}

        {/* Fill areas */}
        <path d={buildPath(primaryValues, true)} fill="url(#primaryGrad)" />
        {showSecondary && <path d={buildPath(secondaryValues, true)} fill="url(#secondaryGrad)" />}

        {/* Lines */}
        <path d={buildPath(primaryValues)} fill="none" stroke="hsl(217 91% 60%)" strokeWidth="2" strokeLinecap="round" />
        {showSecondary && (
          <path
            d={buildPath(secondaryValues)}
            fill="none"
            stroke="hsl(0 72% 60%)"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeDasharray="5 3"
          />
        )}

        {/* Data points on primary line */}
        {primaryValues.map((v, i) => (
          <circle key={i} cx={px(i)} cy={py(v)} r="3" fill="hsl(217 91% 60%)" stroke="hsl(222 84% 5%)" strokeWidth="1.5" />
        ))}
      </svg>
    </div>
  );
}
