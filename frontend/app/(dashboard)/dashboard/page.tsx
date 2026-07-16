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
  CheckCircle2,
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
import { SeverityBadge } from "@/components/shared/severity-badge";
import { MOCK_INVESTIGATIONS, TX_VOLUME_WEEKLY } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import type { Severity } from "@/types";

const STATS = [
  {
    label: "Active Investigations",
    value: "127",
    delta: "+14",
    deltaType: "negative" as const,
    icon: FileSearch,
    color: "text-blue-400",
    bg: "bg-blue-400/10",
    border: "border-blue-400/20",
    sub: "vs last month",
  },
  {
    label: "Flagged Transactions",
    value: "1,847",
    delta: "+203",
    deltaType: "negative" as const,
    icon: AlertTriangle,
    color: "text-red-400",
    bg: "bg-red-400/10",
    border: "border-red-400/20",
    sub: "today",
  },
  {
    label: "Avg Risk Score",
    value: "68.4",
    delta: "-3.2",
    deltaType: "positive" as const,
    icon: Activity,
    color: "text-amber-400",
    bg: "bg-amber-400/10",
    border: "border-amber-400/20",
    sub: "vs last week",
  },
  {
    label: "Resolution Rate",
    value: "94.2%",
    delta: "+1.8%",
    deltaType: "positive" as const,
    icon: ShieldCheck,
    color: "text-emerald-400",
    bg: "bg-emerald-400/10",
    border: "border-emerald-400/20",
    sub: "this quarter",
  },
];

const AGENT_ACTIVITY = [
  { id: 1, agent: "FraudDetect v2.1", action: "Completed batch analysis — 1,240 transactions scanned", time: "2 min ago", status: "success", color: "text-emerald-400", dot: "bg-emerald-400" },
  { id: 2, agent: "RiskScore Engine", action: "Model retrained on 48h dataset — accuracy improved to 98.1%", time: "18 min ago", status: "success", color: "text-emerald-400", dot: "bg-emerald-400" },
  { id: 3, agent: "ATO Detector", action: "High-confidence ATO pattern detected on account #49281", time: "34 min ago", status: "alert", color: "text-red-400", dot: "bg-red-400" },
  { id: 4, agent: "Graph Analyzer", action: "New money mule network identified — 14 linked accounts", time: "1 hr ago", status: "alert", color: "text-amber-400", dot: "bg-amber-400" },
  { id: 5, agent: "Watchlist Monitor", action: "3 transactions matched OFAC sanctions list — auto-blocked", time: "2 hr ago", status: "info", color: "text-blue-400", dot: "bg-blue-400" },
];

const STATUS_CONFIG: Record<string, { label: string; className: string; icon: typeof Circle }> = {
  open: { label: "Open", className: "bg-blue-500/15 text-blue-400", icon: Circle },
  in_review: { label: "In Review", className: "bg-amber-500/15 text-amber-400", icon: Clock },
  escalated: { label: "Escalated", className: "bg-red-500/15 text-red-400", icon: AlertTriangle },
  resolved: { label: "Resolved", className: "bg-emerald-500/15 text-emerald-400", icon: CheckCircle2 },
  closed: { label: "Closed", className: "bg-slate-500/15 text-slate-400", icon: CheckCircle2 },
};

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<"trend" | "volume">("trend");
  const recentInvestigations = MOCK_INVESTIGATIONS.slice(0, 5);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Real-time overview — FraudShield Enterprise
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge
            variant="outline"
            className="gap-1.5 border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
          >
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
            All Systems Operational
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
                    "text-xs font-medium",
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
            <CardDescription>Distribution across all open cases</CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-center pt-2">
            <DonutChart centerLabel="1,847" centerSublabel="total cases" size={180} />
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
              <CardDescription>Latest 5 active cases</CardDescription>
            </div>
            <Button variant="ghost" size="sm" className="h-7 gap-1 text-xs text-muted-foreground" asChild>
              <Link href="/investigations">
                View all <ChevronRight className="h-3 w-3" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-border/60">
              {recentInvestigations.map((inv) => {
                const sc = STATUS_CONFIG[inv.status];
                return (
                  <div key={inv.id} className="flex items-center gap-3 px-6 py-3 hover:bg-muted/20 transition-colors">
                    <SeverityBadge severity={inv.severity as Severity} showDot />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">{inv.title}</p>
                      <p className="text-xs text-muted-foreground">
                        {inv.id} · {inv.transactionCount} txns ·{" "}
                        <span className="font-medium text-foreground/70">
                          ${inv.estimatedLoss.toLocaleString()}
                        </span>
                      </p>
                    </div>
                    <span className={cn("hidden rounded-full px-2 py-0.5 text-[11px] font-medium sm:block", sc.className)}>
                      {sc.label}
                    </span>
                    <span className="hidden text-xs text-muted-foreground lg:block whitespace-nowrap">
                      {inv.updatedAt}
                    </span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Agent Activity */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Agent Activity</CardTitle>
            <CardDescription>Live AI pipeline events</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-border/60">
              {AGENT_ACTIVITY.map((event) => (
                <div key={event.id} className="flex items-start gap-3 px-4 py-3">
                  <span className={cn("mt-1.5 h-2 w-2 shrink-0 rounded-full", event.dot)} />
                  <div className="min-w-0 flex-1">
                    <p className={cn("text-xs font-semibold", event.color)}>{event.agent}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground leading-relaxed line-clamp-2">{event.action}</p>
                    <p className="mt-1 text-[10px] text-muted-foreground/60">{event.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="mb-3 text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
          Quick Actions
        </h2>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {[
            { label: "New Investigation", icon: FileSearch, description: "Start an agentic fraud case", href: "/investigations" },
            { label: "Risk Analysis", icon: TrendingUp, description: "Run ML-powered risk scoring", href: "/analytics" },
            { label: "Review Transactions", icon: CreditCard, description: "Triage flagged transactions", href: "/transactions" },
            { label: "Agent Pipelines", icon: Cpu, description: "Manage AI detection agents", href: "/agents" },
          ].map((action) => (
            <Link
              key={action.label}
              href={action.href}
              className="group flex items-start gap-4 rounded-xl border border-border bg-card p-4 transition-all hover:border-primary/30 hover:bg-accent/30"
            >
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 transition-colors group-hover:bg-primary/20">
                <action.icon className="h-4 w-4 text-primary" />
              </div>
              <div>
                <div className="text-sm font-medium">{action.label}</div>
                <div className="mt-0.5 text-xs text-muted-foreground">{action.description}</div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Metric summary strip */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: "Transactions Today", value: "48,291", icon: CreditCard },
          { label: "AI Agents Active", value: "7 / 10", icon: Cpu },
          { label: "Avg Response Time", value: "1.8 hrs", icon: Clock },
          { label: "Cases This Week", value: "34 new", icon: Activity },
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
