"use client";

import { useState } from "react";
import {
  TrendingUp,
  TrendingDown,
  Clock,
  Target,
  Activity,
  BarChart3,
  Download,
  RefreshCw,
  Cpu,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { AreaChart } from "@/components/charts/area-chart";
import { BarChart } from "@/components/charts/bar-chart";
import { DonutChart } from "@/components/charts/donut-chart";
import { useAnalytics } from "@/hooks/useAnalytics";
import { LoadingSpinner, ErrorCard } from "@/components/shared/feedback";
import { cn } from "@/lib/utils";

const DATE_RANGES = ["7d", "30d", "90d", "12m"] as const;
type DateRange = (typeof DATE_RANGES)[number];

const ICON_MAP: Record<string, any> = {
  "Detection Rate": Target,
  "Avg. Response Time": Clock,
  "Cases Closed": Activity,
  "False Positive Rate": BarChart3,
};

const COLOR_MAP: Record<string, { color: string; bg: string }> = {
  "Detection Rate": { color: "text-emerald-400", bg: "bg-emerald-400/10" },
  "Avg. Response Time": { color: "text-blue-400", bg: "bg-blue-400/10" },
  "Cases Closed": { color: "text-violet-400", bg: "bg-violet-400/10" },
  "False Positive Rate": { color: "text-amber-400", bg: "bg-amber-400/10" },
};

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState<DateRange>("30d");
  const { data, loading, error, refetch } = useAnalytics();

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <LoadingSpinner message="Querying live AI analytics database registry..." />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex h-[80vh] items-center justify-center p-6">
        <ErrorCard 
          message={error || "Analytics could not be loaded."} 
          onRetry={refetch} 
        />
      </div>
    );
  }

  const {
    summaryStats = [],
    fraudTrend30d = [],
    topFraudCategories = [],
    topMerchantsLoss = [],
    txVolumeWeekly = [],
    agentMetrics = [],
    agentPerformance = []
  } = data;

  const trendData = dateRange === "7d" ? fraudTrend30d.slice(-7) : dateRange === "90d" ? [...fraudTrend30d, ...fraudTrend30d, ...fraudTrend30d].slice(0, 30) : fraudTrend30d;

  const handleExport = () => {
    const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
      JSON.stringify(data, null, 2)
    )}`;
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", jsonString);
    downloadAnchor.setAttribute("download", `analytics_report_${new Date().toISOString().split('T')[0]}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
          <p className="mt-1 text-sm text-muted-foreground">AI-powered fraud detection intelligence and trends</p>
        </div>
        <div className="flex items-center gap-2">
          {/* Date range selector */}
          <div className="flex items-center gap-0.5 rounded-lg border border-border bg-muted/40 p-1">
            {DATE_RANGES.map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => setDateRange(r)}
                className={cn(
                  "rounded-md px-3 py-1 text-xs font-medium transition-colors",
                  dateRange === r ? "bg-background text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground",
                )}
              >
                {r}
              </button>
            ))}
          </div>
          <Button variant="outline" size="sm" className="gap-1.5" onClick={() => refetch()}>
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5" onClick={handleExport}>
            <Download className="h-3.5 w-3.5" />
            Export
          </Button>
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {summaryStats.map((s: any) => {
          const Icon = ICON_MAP[s.label] || Target;
          const styles = COLOR_MAP[s.label] || { color: "text-indigo-400", bg: "bg-indigo-400/10" };
          return (
            <Card key={s.label} className="gradient-border bg-white border border-slate-100 shadow-sm rounded-xl">
              <CardContent className="pt-4">
                <div className="flex items-start justify-between">
                  <div className={cn("flex h-9 w-9 items-center justify-center rounded-lg", styles.bg)}>
                    <Icon className={cn("h-4 w-4", styles.color)} />
                  </div>
                  <div className={cn("flex items-center gap-0.5 text-xs font-medium", s.up ? "text-emerald-500" : "text-rose-500")}>
                    {s.up ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                    {s.delta}
                  </div>
                </div>
                <div className="mt-3">
                  <p className="text-2xl font-bold tabular-nums text-slate-800">{s.value}</p>
                  <p className="mt-0.5 text-xs font-semibold text-slate-700">{s.label}</p>
                  <p className="text-[11px] text-slate-400">{s.description}</p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Main trend chart */}
      <Card className="bg-white border border-slate-100 shadow-sm rounded-xl overflow-hidden">
        <CardHeader className="pb-2 bg-slate-50/50">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base font-bold text-slate-800">Fraud Detection Timeline</CardTitle>
              <CardDescription className="text-xs text-slate-500">Cases detected vs. escalated — {dateRange} window</CardDescription>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-500 font-medium">
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-blue-500" />
                Detected
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-red-400" />
                Escalated
              </span>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-4">
          <AreaChart data={trendData} primaryLabel="Detected" secondaryLabel="Escalated" />
        </CardContent>
      </Card>

      {/* Row 2: Donut + Horizontal bar + Bar */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Fraud by type donut */}
        <Card className="bg-white border border-slate-100 shadow-sm rounded-xl overflow-hidden">
          <CardHeader className="pb-2 bg-slate-50/50">
            <CardTitle className="text-base font-bold text-slate-800">Fraud by Category</CardTitle>
            <CardDescription className="text-xs text-slate-500">Distribution across all cases</CardDescription>
          </CardHeader>
          <CardContent className="pt-4 flex justify-center">
            <DonutChart
              data={topFraudCategories}
              centerLabel={data.summaryStats[2]?.value || "0"}
              centerSublabel="total cases"
              size={200}
            />
          </CardContent>
        </Card>

        {/* Loss by merchant category */}
        <Card className="bg-white border border-slate-100 shadow-sm rounded-xl overflow-hidden">
          <CardHeader className="pb-2 bg-slate-50/50">
            <CardTitle className="text-base font-bold text-slate-800">Loss by Merchant Category</CardTitle>
            <CardDescription className="text-xs text-slate-500">Estimated financial exposure ($)</CardDescription>
          </CardHeader>
          <CardContent className="pt-4">
            <BarChart
              data={topMerchantsLoss.map((m: any) => ({
                ...m,
                label: m.label.split(" ")[0],
                value: Math.round(m.value / 1000),
              }))}
              horizontal
            />
          </CardContent>
        </Card>

        {/* Weekly flagged volume */}
        <Card className="bg-white border border-slate-100 shadow-sm rounded-xl overflow-hidden">
          <CardHeader className="pb-2 bg-slate-50/50">
            <CardTitle className="text-base font-bold text-slate-800">Flagged Volume by Day</CardTitle>
            <CardDescription className="text-xs text-slate-500">Transactions flagged this week</CardDescription>
          </CardHeader>
          <CardContent className="pt-4">
            <BarChart data={txVolumeWeekly} />
          </CardContent>
        </Card>
      </div>

      {/* Row 3: Agent performance */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Agent performance chart */}
        <Card className="bg-white border border-slate-100 shadow-sm rounded-xl overflow-hidden">
          <CardHeader className="pb-2 bg-slate-50/50">
            <CardTitle className="text-base font-bold text-slate-800">AI Model Accuracy (7 Days)</CardTitle>
            <CardDescription className="text-xs text-slate-500">FraudDetect v2.1 detection confidence</CardDescription>
          </CardHeader>
          <CardContent className="pt-4">
            <AreaChart
              data={agentPerformance}
              showSecondary={false}
              primaryLabel="Accuracy %"
            />
          </CardContent>
        </Card>

        {/* Agent table */}
        <Card className="bg-white border border-slate-100 shadow-sm rounded-xl overflow-hidden">
          <CardHeader className="pb-2 bg-slate-50/50">
            <CardTitle className="text-base font-bold text-slate-800">Agent Performance Summary</CardTitle>
            <CardDescription className="text-xs text-slate-500">All active detection agents</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 pt-4">
            {agentMetrics.map((agent: any) => (
              <div key={agent.name} className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="flex h-6 w-6 items-center justify-center rounded-md bg-indigo-50 text-indigo-700">
                      <Cpu className="h-3 w-3" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold leading-none text-slate-800">{agent.name}</p>
                      <p className="text-[10px] text-slate-400 mt-0.5">{agent.type}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-slate-400">{agent.cases.toLocaleString()} cases</span>
                    <span
                      className={cn(
                        "rounded-full px-1.5 py-0.5 text-[10px] font-semibold border",
                        agent.status === "active"
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : "bg-amber-50 text-amber-700 border-amber-200",
                      )}
                    >
                      {agent.status}
                    </span>
                    <span className="w-10 text-right text-xs font-bold tabular-nums text-slate-800">{agent.accuracy}%</span>
                  </div>
                </div>
                <Progress
                  value={agent.accuracy}
                  max={100}
                  className="h-1.5 bg-slate-100"
                  indicatorClassName={
                    agent.accuracy >= 97
                      ? "bg-emerald-500"
                      : agent.accuracy >= 94
                        ? "bg-indigo-600"
                        : "bg-amber-500"
                  }
                />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Resolution metrics */}
      <div className="grid gap-4 sm:grid-cols-3">
        {[
          { label: "Mean Time to Detect", value: "4.2 min", sub: "from transaction to flag", color: "text-indigo-600" },
          { label: "Mean Time to Investigate", value: "6.8 hrs", sub: "from flag to case open", color: "text-amber-600" },
          { label: "Mean Time to Resolve", value: "2.1 days", sub: "from open to closed", color: "text-emerald-600" },
        ].map((m) => (
          <Card key={m.label} className="text-center bg-white border border-slate-100 shadow-sm rounded-xl">
            <CardContent className="py-6">
              <p className={cn("text-3xl font-extrabold tabular-nums", m.color)}>{m.value}</p>
              <p className="mt-1 text-sm font-bold text-slate-800">{m.label}</p>
              <p className="text-xs text-slate-400 mt-0.5">{m.sub}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
