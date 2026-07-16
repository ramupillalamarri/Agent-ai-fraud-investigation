"use client";

import { useState } from "react";
import {
  Cpu,
  Activity,
  Play,
  Pause,
  Settings,
  RefreshCw,
  Plus,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Zap,
  TrendingUp,
  BarChart3,
  Terminal,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";
import { AreaChart } from "@/components/charts/area-chart";

interface Agent {
  id: string;
  name: string;
  type: string;
  status: "active" | "paused" | "training" | "error";
  accuracy: number;
  casesProcessed: number;
  lastRun: string;
  enabled: boolean;
  description: string;
}

const AGENTS: Agent[] = [
  { id: "fraud-detect", name: "FraudDetect v2.1", type: "Card Fraud Detection", status: "active", accuracy: 98.1, casesProcessed: 1240, lastRun: "2 min ago", enabled: true, description: "Multi-layer neural network for real-time card fraud detection with velocity checks and behavioral analysis." },
  { id: "ato-sentinel", name: "ATO Sentinel", type: "Account Takeover", status: "active", accuracy: 96.4, casesProcessed: 384, lastRun: "5 min ago", enabled: true, description: "Detects account takeover attempts through login pattern analysis, device fingerprinting, and MFA challenges." },
  { id: "graph-analyzer", name: "Graph Analyzer", type: "Network Analysis", status: "active", accuracy: 94.8, casesProcessed: 127, lastRun: "18 min ago", enabled: true, description: "Identifies fraud rings and money mule networks through transaction graph analysis and clustering algorithms." },
  { id: "wire-guardian", name: "Wire Guardian", type: "Wire Fraud", status: "active", accuracy: 97.2, casesProcessed: 89, lastRun: "1 hr ago", enabled: true, description: "Monitors wire and ACH transfers for signs of business email compromise and authorized push payment fraud." },
  { id: "identity-shield", name: "Identity Shield", type: "Synthetic ID Detection", status: "training", accuracy: 93.1, casesProcessed: 203, lastRun: "2 hr ago", enabled: true, description: "Identifies synthetic identities using document verification, biometric analysis, and database cross-checks." },
  { id: "watchlist-monitor", name: "Watchlist Monitor", type: "Sanctions Screening", status: "active", accuracy: 99.9, casesProcessed: 2847, lastRun: "Real-time", enabled: true, description: "Real-time screening against OFAC, EU, UN, and other sanctions lists with automatic blocking." },
];

const AGENT_PERFORMANCE_DATA = [
  { label: "Mon", value: 94 },
  { label: "Tue", value: 91 },
  { label: "Wed", value: 96 },
  { label: "Thu", value: 93 },
  { label: "Fri", value: 97 },
  { label: "Sat", value: 95 },
  { label: "Sun", value: 98 },
];

export default function AgentsPage() {
  const [agents, setAgents] = useState(AGENTS);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(AGENTS[0]);

  function toggleAgent(id: string) {
    setAgents((prev) => prev.map((a) => a.id === id ? { ...a, enabled: !a.enabled } : a));
  }

  function pauseAgent(id: string) {
    setAgents((prev) => prev.map((a) => a.id === id ? { ...a, status: a.status === "active" ? "paused" : "active" } : a));
  }

  const activeCount = agents.filter((a) => a.status === "active" && a.enabled).length;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">AI Agents</h1>
          <p className="mt-1 text-sm text-muted-foreground">Manage fraud detection AI agents and pipelines</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-1.5">
            <Plus className="h-3.5 w-3.5" />
            Add Agent
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5">
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh Status
          </Button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { label: "Active Agents", value: `${activeCount} / ${agents.length}`, icon: Cpu, color: "text-emerald-400", bg: "bg-emerald-400/10" },
          { label: "Total Cases Processed", value: "4,890", icon: BarChart3, color: "text-blue-400", bg: "bg-blue-400/10" },
          { label: "Avg Accuracy", value: "96.5%", icon: TrendingUp, color: "text-violet-400", bg: "bg-violet-400/10" },
          { label: "Training Agents", value: agents.filter((a) => a.status === "training").length.toString(), icon: Zap, color: "text-amber-400", bg: "bg-amber-400/10" },
        ].map((stat) => (
          <Card key={stat.label} className="gradient-border">
            <CardContent className="flex items-center gap-4 py-4">
              <div className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-lg", stat.bg)}>
                <stat.icon className={cn("h-5 w-5", stat.color)} />
              </div>
              <div>
                <p className="text-2xl font-bold tabular-nums">{stat.value}</p>
                <p className="text-xs text-muted-foreground">{stat.label}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Agent List */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Detection Agents</CardTitle>
            <CardDescription>Configure and monitor AI agent performance</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {agents.map((agent) => (
              <div
                key={agent.id}
                className={cn(
                  "flex items-center gap-4 rounded-lg border p-4 transition-colors cursor-pointer",
                  selectedAgent?.id === agent.id ? "border-primary bg-primary/5" : "border-border hover:bg-muted/20"
                )}
                onClick={() => setSelectedAgent(agent)}
              >
                <div className={cn(
                  "flex h-10 w-10 shrink-0 items-center justify-center rounded-lg",
                  agent.status === "active" ? "bg-emerald-500/15" :
                  agent.status === "paused" ? "bg-slate-500/15" :
                  agent.status === "training" ? "bg-amber-500/15" : "bg-red-500/15"
                )}>
                  <Cpu className={cn(
                    "h-5 w-5",
                    agent.status === "active" ? "text-emerald-400" :
                    agent.status === "paused" ? "text-slate-400" :
                    agent.status === "training" ? "text-amber-400" : "text-red-400"
                  )} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium">{agent.name}</p>
                    <Badge
                      variant="outline"
                      className={cn(
                        "text-[10px]",
                        agent.status === "active" && "border-emerald-500/30 text-emerald-400",
                        agent.status === "paused" && "border-slate-500/30 text-slate-400",
                        agent.status === "training" && "border-amber-500/30 text-amber-400",
                        agent.status === "error" && "border-red-500/30 text-red-400"
                      )}
                    >
                      {agent.status}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">{agent.type}</p>
                </div>
                <div className="hidden items-center gap-4 sm:flex">
                  <div className="text-right">
                    <p className="text-sm font-semibold tabular-nums">{agent.accuracy}%</p>
                    <p className="text-[10px] text-muted-foreground">Accuracy</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold tabular-nums">{agent.casesProcessed.toLocaleString()}</p>
                    <p className="text-[10px] text-muted-foreground">Cases</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={agent.enabled}
                    onCheckedChange={() => toggleAgent(agent.id)}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={(e) => { e.stopPropagation(); pauseAgent(agent.id); }}
                  >
                    {agent.status === "active" ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Agent Detail Panel */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Agent Details</CardTitle>
            <CardDescription>Configuration and metrics</CardDescription>
          </CardHeader>
          <CardContent>
            {selectedAgent ? (
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <Cpu className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <p className="font-semibold">{selectedAgent.name}</p>
                    <p className="text-xs text-muted-foreground">{selectedAgent.type}</p>
                  </div>
                </div>

                <p className="text-xs text-muted-foreground">{selectedAgent.description}</p>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Accuracy</span>
                    <span className="text-sm font-semibold">{selectedAgent.accuracy}%</span>
                  </div>
                  <Progress value={selectedAgent.accuracy} max={100} className="h-2" />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="rounded-lg bg-muted/50 p-3">
                    <p className="text-xs text-muted-foreground">Cases Processed</p>
                    <p className="text-lg font-semibold">{selectedAgent.casesProcessed.toLocaleString()}</p>
                  </div>
                  <div className="rounded-lg bg-muted/50 p-3">
                    <p className="text-xs text-muted-foreground">Last Run</p>
                    <p className="text-sm font-semibold">{selectedAgent.lastRun}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-medium">Performance (7 days)</p>
                  <AreaChart data={AGENT_PERFORMANCE_DATA} primaryLabel="Accuracy %" showSecondary={false} />
                </div>

                <div className="flex gap-2 pt-2">
                  <Button variant="outline" size="sm" className="flex-1 gap-1.5">
                    <Settings className="h-3.5 w-3.5" />
                    Configure
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1 gap-1.5">
                    <Terminal className="h-3.5 w-3.5" />
                    Logs
                  </Button>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8">
                <Cpu className="h-8 w-8 text-muted-foreground/40" />
                <p className="mt-2 text-sm text-muted-foreground">Select an agent</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Recent Agent Activity</CardTitle>
          <CardDescription>Latest actions performed by AI agents</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y divide-border/60">
            {[
              { agent: "FraudDetect v2.1", action: "Blocked 3 transactions with risk score > 95", time: "2 min ago", type: "action" },
              { agent: "Graph Analyzer", action: "Identified new money mule network — 14 linked accounts", time: "18 min ago", type: "discovery" },
              { agent: "Watchlist Monitor", action: "Matched OFAC sanctions list — 2 transactions auto-blocked", time: "1 hr ago", type: "alert" },
              { agent: "ATO Sentinel", action: "Detected ATO pattern on account #49281 — alert raised", time: "2 hr ago", type: "alert" },
              { agent: "Identity Shield", action: "Training completed on 50,000 new samples — accuracy improved", time: "3 hr ago", type: "info" },
            ].map((activity, i) => (
              <div key={i} className="flex items-center gap-4 px-6 py-3">
                <div className={cn(
                  "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                  activity.type === "action" ? "bg-emerald-500/15" :
                  activity.type === "discovery" ? "bg-violet-500/15" :
                  activity.type === "alert" ? "bg-amber-500/15" : "bg-blue-500/15"
                )}>
                  {activity.type === "action" ? <CheckCircle2 className="h-4 w-4 text-emerald-400" /> :
                   activity.type === "discovery" ? <Activity className="h-4 w-4 text-violet-400" /> :
                   activity.type === "alert" ? <AlertTriangle className="h-4 w-4 text-amber-400" /> :
                   <Clock className="h-4 w-4 text-blue-400" />}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium">{activity.agent}</p>
                  <p className="text-xs text-muted-foreground">{activity.action}</p>
                </div>
                <span className="text-xs text-muted-foreground">{activity.time}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
