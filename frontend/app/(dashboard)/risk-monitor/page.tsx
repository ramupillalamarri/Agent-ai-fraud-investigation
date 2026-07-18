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
import { useInvestigations } from "@/hooks/useInvestigations";
import { LoadingSpinner } from "@/components/shared/feedback";


import { useRouter } from "next/navigation";
import { useInvestigations } from "@/hooks/useInvestigations";
import { LoadingSpinner } from "@/components/shared/feedback";

const RISK_THRESHOLDS = [
  { label: "Critical", min: 80, max: 100, color: "text-red-400", bg: "bg-red-500/15", border: "border-red-500/25" },
  { label: "High", min: 60, max: 79, color: "text-orange-400", bg: "bg-orange-500/15", border: "border-orange-500/25" },
  { label: "Medium", min: 40, max: 59, color: "text-amber-400", bg: "bg-amber-500/15", border: "border-amber-500/25" },
  { label: "Low", min: 0, max: 39, color: "text-emerald-400", bg: "bg-emerald-500/15", border: "border-emerald-500/25" },
];

const RECENT_RISK_EVENTS = [
  { id: "1", entity: "Account #49281", type: "Account Takeover", riskScore: 94, delta: "+12", time: "2 min ago", status: "critical" },
  { id: "2", entity: "Card ***4821", type: "Card Fraud", riskScore: 87, delta: "+8", time: "5 min ago", status: "high" },
  { id: "3", entity: "IP 192.168.1.x", type: "Velocity Check", riskScore: 76, delta: "+15", time: "8 min ago", status: "high" },
  { id: "4", entity: "Merchant #8841", type: "Merchant Risk", riskScore: 68, delta: "+5", time: "12 min ago", status: "medium" },
  { id: "5", entity: "Session #44921", type: "Behavioral", riskScore: 52, delta: "+3", time: "18 min ago", status: "medium" },
  { id: "6", entity: "Device fingerprint", type: "Device Risk", riskScore: 34, delta: "-2", time: "25 min ago", status: "low" },
  { id: "7", entity: "Email domain", type: "Email Reputation", riskScore: 28, delta: "+1", time: "32 min ago", status: "low" },
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
  const router = useRouter();
  const [filter, setFilter] = useState<string>("all");
  const { investigations, loading, error, refetch } = useInvestigations({ page_size: 200 });

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <LoadingSpinner message="Retrieving live risk scoring data..." />
      </div>
    );
  }

  const hasData = investigations && investigations.length > 0;

  // Calculate dynamic stats
  let avgRiskScore = "68.4";
  let criticalCount = 12;
  let highCount = 47;
  let mediumCount = 128;
  let lowCount = 234;
  let totalEntities = 421;
  let avgResponseTime = "1.2s";

  if (hasData) {
    totalEntities = investigations.length;
    const totalRisk = investigations.reduce((sum, inv) => sum + (inv.risk_score || 0), 0);
    avgRiskScore = (totalRisk / totalEntities).toFixed(1);

    criticalCount = investigations.filter((inv: any) => inv.risk_score >= 80).length;
    highCount = investigations.filter((inv: any) => inv.risk_score >= 60 && inv.risk_score < 80).length;
    mediumCount = investigations.filter((inv: any) => inv.risk_score >= 40 && inv.risk_score < 60).length;
    lowCount = investigations.filter((inv: any) => inv.risk_score < 40).length;

    let totalHrs = 0;
    let closedCount = 0;
    investigations.forEach((inv: any) => {
      if (inv.completed_at && inv.started_at) {
        const diffSecs = (new Date(inv.completed_at).getTime() - new Date(inv.started_at).getTime()) / 1000;
        if (diffSecs > 0) {
          totalHrs += diffSecs;
          closedCount++;
        }
      }
    });
    avgResponseTime = closedCount > 0 ? `${(totalHrs / closedCount).toFixed(1)}s` : "1.2s";
  }

  const statMetrics = [
    { label: "Avg Risk Score", value: avgRiskScore, delta: hasData ? "live data" : "-3.2", up: false, icon: Activity, color: "text-amber-400", bg: "bg-amber-400/10" },
    { label: "Critical Alerts", value: criticalCount.toString(), delta: hasData ? "live database" : "+4", up: true, icon: Zap, color: "text-red-400", bg: "bg-red-400/10" },
    { label: "High Risk Items", value: highCount.toString(), delta: hasData ? "live database" : "-8", up: false, icon: AlertTriangle, color: "text-orange-400", bg: "bg-orange-400/10" },
    { label: "Avg Response Time", value: avgResponseTime, delta: hasData ? "active agents" : "-0.3s", up: false, icon: Clock, color: "text-blue-400", bg: "bg-blue-400/10" },
  ];

  const dynamicRiskDistribution = hasData ? [
    { label: "Critical (80+)", value: criticalCount, color: "hsl(0 72% 60%)" },
    { label: "High (60-79)", value: highCount, color: "hsl(25 95% 58%)" },
    { label: "Medium (40-59)", value: mediumCount, color: "hsl(43 96% 56%)" },
    { label: "Low (0-39)", value: lowCount, color: "hsl(142 71% 45%)" },
  ] : RISK_DISTRIBUTION;

  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const dailyRiskMap: Record<string, { sum: number; count: number }> = {
    Sun: { sum: 0, count: 0 },
    Mon: { sum: 0, count: 0 },
    Tue: { sum: 0, count: 0 },
    Wed: { sum: 0, count: 0 },
    Thu: { sum: 0, count: 0 },
    Fri: { sum: 0, count: 0 },
    Sat: { sum: 0, count: 0 }
  };

  if (hasData) {
    investigations.forEach((inv: any) => {
      const invDate = new Date(inv.created_at);
      const dayName = dayNames[invDate.getDay()];
      dailyRiskMap[dayName].sum += inv.risk_score || 0;
      dailyRiskMap[dayName].count++;
    });
  }

  const dynamicRiskTrendData = hasData ? dayNames.map(day => {
    const stats = dailyRiskMap[day];
    const avg = stats.count > 0 ? Math.round(stats.sum / stats.count) : 0;
    return {
      label: day,
      value: avg,
      secondary: investigations.filter((inv: any) => {
        const invDate = new Date(inv.created_at);
        return dayNames[invDate.getDay()] === day && inv.risk_score >= 80;
      }).length
    };
  }) : RISK_TREND_DATA;

  const dynamicRecentRiskEvents = hasData ? investigations.slice(0, 15).map((inv: any) => {
    const tx_data = inv.additional_metadata || {};
    let anomalyType = "Standard Audit";
    if (inv.agent_results && inv.agent_results.length > 0) {
      const agentNames = inv.agent_results.map((r: any) => r.agent_name);
      if (agentNames.includes("NetworkRiskAgent")) {
        anomalyType = "Relational Network Anomaly";
      } else if (agentNames.includes("DeviceInvestigationAgent")) {
        anomalyType = "Device Fingerprint Threat";
      } else if (agentNames.includes("MerchantInvestigationAgent")) {
        anomalyType = "Merchant Category Velocity";
      } else if (agentNames.includes("CustomerInvestigationAgent")) {
        anomalyType = "Consumer Velocity Anomalies";
      } else if (agentNames.includes("KnowledgeAgent")) {
        anomalyType = "Compliance Playbook Match";
      }
    }

    let status = "low";
    if (inv.risk_score >= 80) status = "critical";
    else if (inv.risk_score >= 60) status = "high";
    else if (inv.risk_score >= 40) status = "medium";

    const createdDate = new Date(inv.created_at);
    const diffMs = new Date().getTime() - createdDate.getTime();
    const diffMins = Math.round(diffMs / (1000 * 60));
    let timeText = "Just now";
    if (diffMins > 0) {
      if (diffMins < 60) {
        timeText = `${diffMins} min ago`;
      } else {
        const diffHrs = Math.round(diffMins / 60);
        if (diffHrs < 24) {
          timeText = `${diffHrs} hr ago`;
        } else {
          timeText = createdDate.toLocaleDateString([], { month: "short", day: "numeric" });
        }
      }
    }

    return {
      id: inv.id,
      entity: `Transaction #${inv.transaction_id.slice(0, 8)}...`,
      type: anomalyType,
      riskScore: inv.risk_score,
      delta: inv.risk_score >= 80 ? "+12" : inv.risk_score >= 50 ? "+5" : "-2",
      time: timeText,
      status: status
    };
  }) : RECENT_RISK_EVENTS;

  const filteredEvents = dynamicRecentRiskEvents.filter((event) => {
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
          <Button variant="outline" size="sm" className="gap-1.5" onClick={() => refetch()}>
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {statMetrics.map((stat) => (
          <Card key={stat.label} className="gradient-border">
            <CardContent className="flex items-center gap-4 py-4">
              <div className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-lg", stat.bg)}>
                <stat.icon className={cn("h-5 w-5", stat.color)} />
              </div>
              <div>
                <p className="text-2xl font-bold tabular-nums">{stat.value}</p>
                <p className="text-xs text-muted-foreground">{stat.label}</p>
                <p className={cn("text-[10px] font-medium", stat.up ? "text-red-400" : "text-emerald-400")}>
                  {stat.delta} {hasData ? "" : "from yesterday"}
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
            <AreaChart data={dynamicRiskTrendData} primaryLabel="Avg Risk Score" secondaryLabel="Critical" />
          </CardContent>
        </Card>

        {/* Risk Distribution */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Risk Distribution</CardTitle>
            <CardDescription>Current risk level breakdown</CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-center">
            <DonutChart data={dynamicRiskDistribution} centerLabel={totalEntities.toString()} centerSublabel="total entities" size={180} />
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
                  {threshold.label === "Critical" ? criticalCount : threshold.label === "High" ? highCount : threshold.label === "Medium" ? mediumCount : lowCount} entities
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
                  <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => router.push(`/investigations/${event.id}`)}>
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

