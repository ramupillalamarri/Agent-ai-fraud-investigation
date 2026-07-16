"use client";

import { useState } from "react";
import {
  Activity,
  AlertTriangle,
  Clock,
  Zap,
  RefreshCw,
  Eye,
  Ban,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { AreaChart } from "@/components/charts/area-chart";
import { DonutChart } from "@/components/charts/donut-chart";
import { cn } from "@/lib/utils";
import { RiskScoreBadge } from "@/components/shared/risk-score";

const RISK_THRESHOLDS = [
  { label: "Critical", min: 80, max: 100, color: "text-red-400", bg: "bg-red-500/15", border: "border-red-500/25" },
  { label: "High", min: 60, max: 79, color: "text-orange-400", bg: "bg-orange-500/15", border: "border-orange-500/25" },
  { label: "Medium", min: 40, max: 59, color: "text-amber-400", bg: "bg-amber-500/15", border: "border-amber-500/25" },
  { label: "Low", min: 0, max: 39, color: "text-emerald-400", bg: "bg-emerald-500/15", border: "border-emerald-500/25" },
];

const RECENT_RISK_EVENTS = [
  { id: 1, entity: "Account #49281", type: "Account Takeover", riskScore: 94, delta: "+12", time: "2 min ago", status: "critical" },
  { id: 2, entity: "Card ***4821", type: "Card Fraud", riskScore: 87, delta: "+8", time: "5 min ago", status: "high" },
  { id: 3, entity: "IP 192.168.1.x", type: "Velocity Check", riskScore: 76, delta: "+15", time: "8 min ago", status: "high" },
  { id: 4, entity: "Merchant #8841", type: "Merchant Risk", riskScore: 68, delta: "+5", time: "12 min ago", status: "medium" },
  { id: 5, entity: "Session #44921", type: "Behavioral", riskScore: 52, delta: "+3", time: "18 min ago", status: "medium" },
  { id: 6, entity: "Device fingerprint", type: "Device Risk", riskScore: 34, delta: "-2", time: "25 min ago", status: "low" },
  { id: 7, entity: "Email domain", type: "Email Reputation", riskScore: 28, delta: "+1", time: "32 min ago", status: "low" },
];

const RISK_DISTRIBUTION = [
  { label: "Critical (80+)", value: 12, color: "hsl(0 72% 60%)" },
  { label: "High (60-79)", value: 47, color: "hsl(25 95% 58%)" },
  { label: "Medium (40-59)", value: 128, color: "hsl(43 96% 56%)" },
  { label: "Low (0-39)", value: 234, color: "hsl(142 71% 45%)" },
];

const RISK_TREND_DATA = [
  { label: "Mon", value: 42, secondary: 8 },
  { label: "Tue", value: 38, secondary: 6 },
  { label: "Wed", value: 51, secondary: 12 },
  { label: "Thu", value: 47, secondary: 9 },
  { label: "Fri", value: 63, secondary: 15 },
  { label: "Sat", value: 35, secondary: 5 },
  { label: "Sun", value: 28, secondary: 4 },
];

export default function RiskMonitorPage() {
  const [filter, setFilter] = useState<string>("all");

  const filteredEvents = RECENT_RISK_EVENTS.filter((event) => {
    if (filter === "all") return true;
    return event.status === filter;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Risk Monitor</h1>
          <p className="mt-1 text-sm text-muted-foreground">Real-time risk scoring and threat detection</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="gap-1.5 border-emerald-500/30 bg-emerald-500/10 text-emerald-400">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
            Live Monitoring
          </Badge>
          <Button variant="outline" size="sm" className="gap-1.5">
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { label: "Avg Risk Score", value: "68.4", delta: "-3.2", up: false, icon: Activity, color: "text-amber-400", bg: "bg-amber-400/10" },
          { label: "Critical Alerts", value: "12", delta: "+4", up: true, icon: Zap, color: "text-red-400", bg: "bg-red-400/10" },
          { label: "High Risk Items", value: "47", delta: "-8", up: false, icon: AlertTriangle, color: "text-orange-400", bg: "bg-orange-400/10" },
          { label: "Avg Response Time", value: "1.2s", delta: "-0.3s", up: false, icon: Clock, color: "text-blue-400", bg: "bg-blue-400/10" },
        ].map((stat) => (
          <Card key={stat.label} className="gradient-border">
            <CardContent className="flex items-center gap-4 py-4">
              <div className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-lg", stat.bg)}>
                <stat.icon className={cn("h-5 w-5", stat.color)} />
              </div>
              <div>
                <p className="text-2xl font-bold tabular-nums">{stat.value}</p>
                <p className="text-xs text-muted-foreground">{stat.label}</p>
                <p className={cn("text-[10px] font-medium", stat.up ? "text-red-400" : "text-emerald-400")}>
                  {stat.delta} from yesterday
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Risk Trend */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Risk Score Trend</CardTitle>
            <CardDescription>Average risk scores over the past week</CardDescription>
          </CardHeader>
          <CardContent>
            <AreaChart data={RISK_TREND_DATA} primaryLabel="Avg Risk Score" secondaryLabel="Critical" />
          </CardContent>
        </Card>

        {/* Risk Distribution */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Risk Distribution</CardTitle>
            <CardDescription>Current risk level breakdown</CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-center">
            <DonutChart data={RISK_DISTRIBUTION} centerLabel="421" centerSublabel="total entities" size={180} />
          </CardContent>
        </Card>
      </div>

      {/* Risk Thresholds */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Risk Thresholds</CardTitle>
          <CardDescription>Configure alert thresholds for risk levels</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {RISK_THRESHOLDS.map((threshold) => (
            <div key={threshold.label} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={cn("flex h-8 w-8 items-center justify-center rounded-lg", threshold.bg, threshold.border)}>
                  <span className={cn("text-xs font-bold", threshold.color)}>{threshold.min}+</span>
                </div>
                <div>
                  <p className="text-sm font-medium">{threshold.label}</p>
                  <p className="text-xs text-muted-foreground">Score range: {threshold.min} - {threshold.max}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <Progress
                  value={threshold.min}
                  max={100}
                  className="w-32 h-2"
                />
                <span className="text-xs text-muted-foreground w-16 text-right">
                  {threshold.label === "Critical" ? "12" : threshold.label === "High" ? "47" : threshold.label === "Medium" ? "128" : "234"} entities
                </span>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Recent Risk Events */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <CardTitle className="text-base">Recent Risk Events</CardTitle>
            <CardDescription>Latest risk scoring events</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="h-8 rounded-md border border-input bg-background px-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            >
              <option value="all">All Levels</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y divide-border/60">
            {filteredEvents.map((event) => (
              <div key={event.id} className="flex items-center gap-4 px-6 py-4 hover:bg-muted/20 transition-colors">
                <div className={cn(
                  "flex h-10 w-10 shrink-0 items-center justify-center rounded-lg",
                  event.status === "critical" ? "bg-red-500/15" :
                  event.status === "high" ? "bg-orange-500/15" :
                  event.status === "medium" ? "bg-amber-500/15" : "bg-emerald-500/15"
                )}>
                  <AlertTriangle className={cn(
                    "h-4 w-4",
                    event.status === "critical" ? "text-red-400" :
                    event.status === "high" ? "text-orange-400" :
                    event.status === "medium" ? "text-amber-400" : "text-emerald-400"
                  )} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium">{event.entity}</p>
                  <p className="text-xs text-muted-foreground">{event.type}</p>
                </div>
                <div className="text-right">
                  <RiskScoreBadge score={event.riskScore} />
                  <p className={cn("text-[10px] font-medium mt-1", event.delta.startsWith("+") ? "text-red-400" : "text-emerald-400")}>
                    {event.delta}
                  </p>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  {event.time}
                </div>
                <div className="flex items-center gap-1">
                  <Button variant="ghost" size="icon" className="h-7 w-7">
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-7 w-7">
                    <Ban className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
