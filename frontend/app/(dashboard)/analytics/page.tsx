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
import {
  FRAUD_TREND_30D,
  AGENT_PERFORMANCE,
  TX_VOLUME_WEEKLY,
  TOP_FRAUD_CATEGORIES,
  TOP_MERCHANTS_LOSS,
} from "@/lib/mock-data";
import { cn } from "@/lib/utils";

const DATE_RANGES = ["7d", "30d", "90d", "12m"] as const;
type DateRange = (typeof DATE_RANGES)[number];

const SUMMARY_STATS = [
  {
    label: "Detection Rate",
    value: "98.1%",
    delta: "+0.4%",
    up: true,
    icon: Target,
    color: "text-emerald-400",
    bg: "bg-emerald-400/10",
    description: "vs prior period",
  },
  {
    label: "Avg. Response Time",
    value: "1.8 hrs",
    delta: "-12 min",
    up: false,
    icon: Clock,
    color: "text-blue-400",
    bg: "bg-blue-400/10",
    description: "to first action",
  },
  {
    label: "Cases Closed",
    value: "847",
    delta: "+127",
    up: true,
    icon: Activity,
    color: "text-violet-400",
    bg: "bg-violet-400/10",
    description: "this period",
  },
  {
    label: "False Positive Rate",
    value: "1.9%",
    delta: "-0.3%",
    up: false,
    icon: BarChart3,
    color: "text-amber-400",
    bg: "bg-amber-400/10",
    description: "model accuracy",
  },
];

const AGENT_METRICS = [
  { name: "FraudDetect v2.1", type: "Card Fraud", accuracy: 98.1, cases: 1240, status: "active" },
  { name: "ATO Sentinel", type: "Account Takeover", accuracy: 96.4, cases: 384, status: "active" },
  { name: "Graph Analyzer", type: "Network Analysis", accuracy: 94.8, cases: 127, status: "active" },
  { name: "Wire Guardian", type: "Wire Fraud", accuracy: 97.2, cases: 89, status: "active" },
  { name: "Identity Shield", type: "Synthetic ID", accuracy: 93.1, cases: 203, status: "training" },
];

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState<DateRange>("30d");

  const trendData = dateRange === "7d" ? FRAUD_TREND_30D.slice(-7) : dateRange === "90d" ? [...FRAUD_TREND_30D, ...FRAUD_TREND_30D, ...FRAUD_TREND_30D].slice(0, 30) : FRAUD_TREND_30D;

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
          <Button variant="outline" size="sm" className="gap-1.5">
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5">
            <Download className="h-3.5 w-3.5" />
            Export
          </Button>
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {SUMMARY_STATS.map((s) => (
          <Card key={s.label} className="gradient-border">
            <CardContent className="pt-4">
              <div className="flex items-start justify-between">
                <div className={cn("flex h-9 w-9 items-center justify-center rounded-lg", s.bg)}>
                  <s.icon className={cn("h-4 w-4", s.color)} />
                </div>
                <div className={cn("flex items-center gap-0.5 text-xs font-medium", s.up ? "text-emerald-400" : "text-red-400")}>
                  {s.up ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                  {s.delta}
                </div>
              </div>
              <div className="mt-3">
                <p className="text-2xl font-bold tabular-nums">{s.value}</p>
                <p className="mt-0.5 text-xs text-muted-foreground">{s.label}</p>
                <p className="text-[11px] text-muted-foreground/60">{s.description}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main trend chart */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">Fraud Detection Timeline</CardTitle>
              <CardDescription>Cases detected vs. escalated — {dateRange} window</CardDescription>
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
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
        <CardContent>
          <AreaChart data={trendData} primaryLabel="Detected" secondaryLabel="Escalated" />
        </CardContent>
      </Card>

      {/* Row 2: Donut + Horizontal bar + Bar */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Fraud by type donut */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Fraud by Category</CardTitle>
            <CardDescription>Distribution across all cases</CardDescription>
          </CardHeader>
          <CardContent>
            <DonutChart
              data={TOP_FRAUD_CATEGORIES}
              centerLabel="1,847"
              centerSublabel="total cases"
              size={200}
            />
          </CardContent>
        </Card>

        {/* Loss by merchant category */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Loss by Merchant Category</CardTitle>
            <CardDescription>Estimated financial exposure ($)</CardDescription>
          </CardHeader>
          <CardContent>
            <BarChart
              data={TOP_MERCHANTS_LOSS.map((m) => ({
                ...m,
                label: m.label.split(" ")[0],
                value: Math.round(m.value / 1000),
              }))}
              horizontal
            />
          </CardContent>
        </Card>

        {/* Weekly flagged volume */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Flagged Volume by Day</CardTitle>
            <CardDescription>Transactions flagged this week</CardDescription>
          </CardHeader>
          <CardContent>
            <BarChart data={TX_VOLUME_WEEKLY} />
          </CardContent>
        </Card>
      </div>

      {/* Row 3: Agent performance */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Agent performance chart */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">AI Model Accuracy (7 Days)</CardTitle>
            <CardDescription>FraudDetect v2.1 detection confidence</CardDescription>
          </CardHeader>
          <CardContent>
            <AreaChart
              data={AGENT_PERFORMANCE}
              showSecondary={false}
              primaryLabel="Accuracy %"
            />
          </CardContent>
        </Card>

        {/* Agent table */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Agent Performance Summary</CardTitle>
            <CardDescription>All active detection agents</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 pt-2">
            {AGENT_METRICS.map((agent) => (
              <div key={agent.name} className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary/10">
                      <Cpu className="h-3 w-3 text-primary" />
                    </div>
                    <div>
                      <p className="text-xs font-medium leading-none">{agent.name}</p>
                      <p className="text-[10px] text-muted-foreground">{agent.type}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground">{agent.cases.toLocaleString()} cases</span>
                    <span
                      className={cn(
                        "rounded-full px-1.5 py-0.5 text-[10px] font-semibold",
                        agent.status === "active"
                          ? "bg-emerald-500/15 text-emerald-400"
                          : "bg-amber-500/15 text-amber-400",
                      )}
                    >
                      {agent.status}
                    </span>
                    <span className="w-10 text-right text-xs font-semibold tabular-nums">{agent.accuracy}%</span>
                  </div>
                </div>
                <Progress
                  value={agent.accuracy}
                  max={100}
                  className="h-1.5"
                  indicatorClassName={
                    agent.accuracy >= 97
                      ? "bg-emerald-500"
                      : agent.accuracy >= 94
                        ? "bg-blue-500"
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
          { label: "Mean Time to Detect", value: "4.2 min", sub: "from transaction to flag", color: "text-blue-400" },
          { label: "Mean Time to Investigate", value: "6.8 hrs", sub: "from flag to case open", color: "text-amber-400" },
          { label: "Mean Time to Resolve", value: "2.1 days", sub: "from open to closed", color: "text-emerald-400" },
        ].map((m) => (
          <Card key={m.label} className="text-center">
            <CardContent className="py-6">
              <p className={cn("text-3xl font-bold tabular-nums", m.color)}>{m.value}</p>
              <p className="mt-1 text-sm font-medium">{m.label}</p>
              <p className="text-xs text-muted-foreground">{m.sub}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
