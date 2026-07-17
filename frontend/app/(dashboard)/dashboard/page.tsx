"use client";

import { useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  ShieldCheck,
  TrendingUp,
  FileSearch,
  Cpu,
  Clock,
  Circle,
  ChevronRight,
  Plus,
  CreditCard,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AreaChart } from "@/components/charts/area-chart";
import { DonutChart } from "@/components/charts/donut-chart";
import { BarChart } from "@/components/charts/bar-chart";
import { useDashboard } from "@/hooks/useDashboard";
import { LoadingSpinner, ErrorCard } from "@/components/shared/feedback";
import { cn } from "@/lib/utils";

const TX_VOLUME_WEEKLY = [
  { label: "Mon", value: 1200 },
  { label: "Tue", value: 1900 },
  { label: "Wed", value: 3000 },
  { label: "Thu", value: 5000 },
  { label: "Fri", value: 2000 },
  { label: "Sat", value: 6000 },
  { label: "Sun", value: 4000 },
];

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<"trend" | "volume">("trend");
  const { metrics, loading, error, refetch } = useDashboard();

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <LoadingSpinner message="Retrieving live framework metrics..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-[80vh] items-center justify-center p-6">
        <ErrorCard message={error} onRetry={refetch} />
      </div>
    );
  }

  const summary = metrics || {
    totalInvestigations: 0,
    highRiskInvestigations: 0,
    averageRiskScore: 0,
    fraudDetectionRate: 0,
    avgExecutionTimeMs: 0,
    agentSuccessRate: 100,
    recentInvestigations: []
  };

  const STATS = [
    {
      label: "Total Investigations",
      value: summary.totalInvestigations.toString(),
      delta: "+100%",
      deltaType: "positive" as const,
      icon: FileSearch,
      color: "text-blue-400",
      bg: "bg-blue-400/10",
      border: "border-blue-400/20",
      sub: "all-time total",
    },
    {
      label: "High Risk Flags",
      value: summary.highRiskInvestigations.toString(),
      delta: "Active",
      deltaType: "negative" as const,
      icon: AlertTriangle,
      color: "text-red-400",
      bg: "bg-red-400/10",
      border: "border-red-400/20",
      sub: "risk >= 75 or HIGH priority",
    },
    {
      label: "Avg Risk Score",
      value: `${summary.averageRiskScore.toFixed(1)}%`,
      delta: "-2.4%",
      deltaType: "positive" as const,
      icon: Activity,
      color: "text-amber-400",
      bg: "bg-amber-400/10",
      border: "border-amber-400/20",
      sub: "from multi-agent outputs",
    },
    {
      label: "Agent Success Rate",
      value: `${summary.agentSuccessRate}%`,
      delta: "+1.2%",
      deltaType: "positive" as const,
      icon: ShieldCheck,
      color: "text-emerald-400",
      bg: "bg-emerald-400/10",
      border: "border-emerald-400/20",
      sub: "successful step executions",
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Real-time live multi-agent execution analytics
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge
            variant="outline"
            className="gap-1.5 border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
          >
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
            Live Framework Connected
          </Badge>
          <Button size="sm" className="gap-1.5" asChild>
            <Link href="/investigations">
              <Plus className="h-3.5 w-3.5" />
              New Investigation
            </Link>
          </Button>
        </div>
      </div>

      {/* KPI cards */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {STATS.map((stat) => (
          <Card key={stat.label} className={cn("gradient-border overflow-hidden")}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{stat.label}</CardTitle>
              <div className={cn("flex h-8 w-8 items-center justify-center rounded-lg border", stat.bg, stat.border)}>
                <stat.icon className={cn("h-4 w-4", stat.color)} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold tracking-tight">{stat.value}</div>
              <div className="mt-1.5 flex items-center gap-1.5">
                {stat.deltaType === "positive" ? (
                  <ArrowUpRight className="h-3.5 w-3.5 text-emerald-400" />
                ) : (
                  <ArrowDownRight className="h-3.5 w-3.5 text-red-400" />
                )}
                <span
                  className={cn(
                    "text-xs font-semibold",
                    stat.deltaType === "positive" ? "text-emerald-400" : "text-red-400",
                  )}
                >
                  {stat.delta}
                </span>
                <span className="text-xs text-muted-foreground">{stat.sub}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts row */}
      <div className="grid gap-6 xl:grid-cols-3">
        {/* Main chart - Fraud Trend */}
        <Card className="xl:col-span-2">
          <CardHeader className="flex flex-row items-start justify-between pb-2">
            <div>
              <CardTitle className="text-base">Fraud Detection Trend</CardTitle>
              <CardDescription>Monthly cases detected vs escalated (12 months)</CardDescription>
            </div>
            <div className="flex items-center rounded-lg border border-border bg-muted/40 p-0.5">
              <button
                type="button"
                onClick={() => setActiveTab("trend")}
                className={cn(
                  "rounded-md px-3 py-1 text-xs font-medium transition-colors",
                  activeTab === "trend" ? "bg-background text-foreground shadow-sm" : "text-muted-foreground",
                )}
              >
                12 Month
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("volume")}
                className={cn(
                  "rounded-md px-3 py-1 text-xs font-medium transition-colors",
                  activeTab === "volume" ? "bg-background text-foreground shadow-sm" : "text-muted-foreground",
                )}
              >
                Weekly
              </button>
            </div>
          </CardHeader>
          <CardContent className="pt-2">
            {activeTab === "trend" ? (
              <AreaChart primaryLabel="Detected Cases" secondaryLabel="Escalated" />
            ) : (
              <BarChart data={TX_VOLUME_WEEKLY} />
            )}
          </CardContent>
        </Card>

        {/* Donut - Fraud by Type */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Fraud by Type</CardTitle>
            <CardDescription>Distribution across all database cases</CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-center pt-2">
            <DonutChart centerLabel={summary.totalInvestigations.toString()} centerSublabel="total cases" size={180} />
          </CardContent>
        </Card>
      </div>

      {/* Investigations + Agent Activity */}
      <div className="grid gap-6 xl:grid-cols-3">
        {/* Recent Investigations */}
        <Card className="xl:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle className="text-base">Recent Investigations</CardTitle>
              <CardDescription>Latest active agentic audits</CardDescription>
            </div>
            <Button variant="ghost" size="sm" className="h-7 gap-1 text-xs text-muted-foreground" asChild>
              <Link href="/investigations">
                View all <ChevronRight className="h-3 w-3" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            {summary.recentInvestigations.length === 0 ? (
              <div className="p-6 text-center text-xs text-muted-foreground italic">
                No active investigations recorded. Run an investigation to get started.
              </div>
            ) : (
              <div className="divide-y divide-border/60">
                {summary.recentInvestigations.map((inv: any) => {
                  const tx_data = inv.additional_metadata || {};
                  return (
                    <div key={inv.id} className="flex items-center gap-3 px-6 py-3 hover:bg-muted/20 transition-colors">
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-semibold text-slate-800">TX: {inv.transaction_id}</p>
                        <p className="text-xs text-muted-foreground">
                          ID: {inv.id.substring(0, 8)}... · Cust: {tx_data.customer_id || "unknown"} ·{" "}
                          <span className="font-bold text-slate-700">
                            ${(tx_data.amount || 0.0).toLocaleString()}
                          </span>
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={cn(
                          "inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold border",
                          inv.priority === "HIGH" 
                            ? "bg-red-50 text-red-700 border-red-200" 
                            : inv.priority === "MEDIUM"
                            ? "bg-amber-50 text-amber-700 border-amber-200"
                            : "bg-emerald-50 text-emerald-700 border-emerald-200"
                        )}>
                          {inv.priority}
                        </span>
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium border bg-indigo-50 text-indigo-700 border-indigo-200">
                          Risk: {inv.risk_score}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Live AI Pipelines */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Agent Performance</CardTitle>
            <CardDescription>Live pipeline execution profile</CardDescription>
          </CardHeader>
          <CardContent className="p-4 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <span className="text-xs text-slate-500 font-medium">Avg Execution Time</span>
              <span className="text-sm font-bold text-indigo-600">{summary.avgExecutionTimeMs} ms</span>
            </div>
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <span className="text-xs text-slate-500 font-medium">Fraud Flag Rate</span>
              <span className="text-sm font-bold text-rose-600">{summary.fraudDetectionRate}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-500 font-medium">Active Agent Nodes</span>
              <span className="text-sm font-bold text-slate-700">3 Nodes</span>
            </div>
            <div className="pt-2 text-[10px] text-muted-foreground leading-relaxed">
              Real-time pipeline aggregates execution metrics directly from concrete models: CustomerInvestigationAgent, DeviceInvestigationAgent, and NetworkRiskAgent.
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Metric summary strip */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: "Active AI Nodes", value: "3 Nodes", icon: Cpu },
          { label: "Pipeline Health", value: "Optimal", icon: ShieldCheck },
          { label: "Platform Latency", value: `${summary.avgExecutionTimeMs} ms`, icon: Clock },
          { label: "Platform Cases", value: `${summary.totalInvestigations} total`, icon: Activity },
        ].map((m) => (
          <div key={m.label} className="flex items-center gap-3 rounded-lg border border-border bg-card/60 px-4 py-3">
            <m.icon className="h-4 w-4 shrink-0 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground">{m.label}</p>
              <p className="text-sm font-semibold">{m.value}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
