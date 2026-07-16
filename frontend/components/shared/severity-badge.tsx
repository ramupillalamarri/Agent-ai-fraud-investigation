import { cn } from "@/lib/utils";
import type { Severity } from "@/types";

const config: Record<Severity, { label: string; className: string; dot: string }> = {
  critical: {
    label: "Critical",
    className: "bg-red-500/15 text-red-400 border-red-500/25 ring-red-500/10",
    dot: "bg-red-400",
  },
  high: {
    label: "High",
    className: "bg-orange-500/15 text-orange-400 border-orange-500/25 ring-orange-500/10",
    dot: "bg-orange-400",
  },
  medium: {
    label: "Medium",
    className: "bg-amber-500/15 text-amber-400 border-amber-500/25 ring-amber-500/10",
    dot: "bg-amber-400",
  },
  low: {
    label: "Low",
    className: "bg-emerald-500/15 text-emerald-400 border-emerald-500/25 ring-emerald-500/10",
    dot: "bg-emerald-400",
  },
  info: {
    label: "Info",
    className: "bg-blue-500/15 text-blue-400 border-blue-500/25 ring-blue-500/10",
    dot: "bg-blue-400",
  },
};

interface SeverityBadgeProps {
  severity: Severity;
  showDot?: boolean;
  className?: string;
}

export function SeverityBadge({ severity, showDot = true, className }: SeverityBadgeProps) {
  const { label, className: baseClass, dot } = config[severity];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide",
        baseClass,
        className,
      )}
    >
      {showDot && <span className={cn("h-1.5 w-1.5 rounded-full", dot)} />}
      {label}
    </span>
  );
}
