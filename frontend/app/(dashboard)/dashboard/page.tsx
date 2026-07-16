import type { Metadata } from "next";
import {
  AlertTriangle,
  ArrowUpRight,
  Activity,
  ShieldCheck,
  TrendingUp,
  Users,
  FileSearch,
  Cpu,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export const metadata: Metadata = {
  title: "Dashboard",
  description: "Fraud investigation overview and key metrics.",
};

const stats = [
  {
    label: "Active Investigations",
    value: "—",
    delta: null,
    icon: FileSearch,
    color: "text-blue-400",
    bg: "bg-blue-400/10",
  },
  {
    label: "Risk Score Avg.",
    value: "—",
    delta: null,
    icon: Activity,
    color: "text-amber-400",
    bg: "bg-amber-400/10",
  },
  {
    label: "Flagged Transactions",
    value: "—",
    delta: null,
    icon: AlertTriangle,
    color: "text-red-400",
    bg: "bg-red-400/10",
  },
  {
    label: "Cases Resolved",
    value: "—",
    delta: null,
    icon: ShieldCheck,
    color: "text-emerald-400",
    bg: "bg-emerald-400/10",
  },
];

const quickActions = [
  { label: "New Investigation", icon: FileSearch, description: "Start an agentic fraud investigation" },
  { label: "Risk Analysis", icon: TrendingUp, description: "Run ML-powered risk scoring" },
  { label: "Agent Pipelines", icon: Cpu, description: "View active AI agent workflows" },
  { label: "Analyst Reports", icon: Users, description: "Assign cases to analysts" },
];

export default function DashboardPage() {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page header */}
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Overview of your fraud investigation platform activity.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="gap-1.5 border-emerald-500/30 bg-emerald-500/10 text-emerald-400">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
            All Systems Operational
          </Badge>
          <Button size="sm" className="gap-1.5">
            <FileSearch className="h-3.5 w-3.5" />
            New Investigation
          </Button>
        </div>
      </div>

      {/* KPI stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label} className="gradient-border">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{stat.label}</CardTitle>
              <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${stat.bg}`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold tracking-tight">{stat.value}</div>
              <p className="mt-1 text-xs text-muted-foreground">No data connected yet</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main content grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Activity feed placeholder */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-base">Recent Activity</CardTitle>
              <CardDescription>Latest fraud signals and agent actions</CardDescription>
            </div>
            <Button variant="ghost" size="sm" className="gap-1 text-xs text-muted-foreground">
              View all <ArrowUpRight className="h-3 w-3" />
            </Button>
          </CardHeader>
          <CardContent>
            <EmptyState
              icon={Activity}
              title="No activity yet"
              description="Connect your data sources to start seeing real-time fraud signals and investigation activity."
            />
          </CardContent>
        </Card>

        {/* Agent status placeholder */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Agent Status</CardTitle>
            <CardDescription>Active AI investigation pipelines</CardDescription>
          </CardHeader>
          <CardContent>
            <EmptyState
              icon={Cpu}
              title="No agents running"
              description="Start an investigation to launch autonomous fraud detection agents."
            />
          </CardContent>
        </Card>
      </div>

      {/* Quick actions */}
      <div>
        <h2 className="mb-4 text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          Quick Actions
        </h2>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {quickActions.map((action) => (
            <button
              key={action.label}
              type="button"
              className="group flex items-start gap-4 rounded-xl border border-border bg-card p-4 text-left transition-all hover:border-primary/30 hover:bg-accent"
            >
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 transition-colors group-hover:bg-primary/20">
                <action.icon className="h-4 w-4 text-primary" />
              </div>
              <div>
                <div className="text-sm font-medium">{action.label}</div>
                <div className="mt-0.5 text-xs text-muted-foreground">{action.description}</div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function EmptyState({
  icon: Icon,
  title,
  description,
}: {
  icon: React.ElementType;
  title: string;
  description: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-10 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
        <Icon className="h-5 w-5 text-muted-foreground" />
      </div>
      <h3 className="mt-3 text-sm font-medium">{title}</h3>
      <p className="mt-1 max-w-xs text-xs text-muted-foreground">{description}</p>
    </div>
  );
}
