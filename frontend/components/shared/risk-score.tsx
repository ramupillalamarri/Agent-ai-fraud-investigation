import { cn } from "@/lib/utils";

interface RiskScoreProps {
  score: number;
  showBar?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
}

function getRiskColor(score: number): { text: string; bar: string; bg: string } {
  if (score >= 80) return { text: "text-red-400", bar: "bg-red-500", bg: "bg-red-500/10" };
  if (score >= 60) return { text: "text-orange-400", bar: "bg-orange-500", bg: "bg-orange-500/10" };
  if (score >= 40) return { text: "text-amber-400", bar: "bg-amber-500", bg: "bg-amber-500/10" };
  return { text: "text-emerald-400", bar: "bg-emerald-500", bg: "bg-emerald-500/10" };
}

function getRiskLabel(score: number): string {
  if (score >= 80) return "Critical";
  if (score >= 60) return "High";
  if (score >= 40) return "Medium";
  return "Low";
}

export function RiskScore({ score, showBar = true, size = "md", className }: RiskScoreProps) {
  const { text, bar, bg } = getRiskColor(score);
  const pct = score;

  const sizeClasses = {
    sm: "text-xs",
    md: "text-sm",
    lg: "text-base font-semibold",
  };

  return (
    <div className={cn("flex flex-col gap-1", className)}>
      <div className="flex items-center gap-2">
        <span className={cn("tabular-nums font-semibold", text, sizeClasses[size])}>{score}</span>
        <span
          className={cn("rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide", bg, text)}
        >
          {getRiskLabel(score)}
        </span>
      </div>
      {showBar && (
        <div className="h-1 w-full overflow-hidden rounded-full bg-muted">
          <div
            className={cn("h-full rounded-full transition-all duration-500", bar)}
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
    </div>
  );
}

export function RiskScoreBadge({ score, className }: { score: number; className?: string }) {
  const { text, bg } = getRiskColor(score);
  return (
    <span className={cn("rounded-md px-2 py-0.5 text-xs font-bold tabular-nums", bg, text, className)}>
      {score}
    </span>
  );
}
