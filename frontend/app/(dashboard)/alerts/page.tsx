"use client";

import { useState } from "react";
import {
  AlertTriangle,
  Bell,
  BellOff,
  CheckCircle2,
  Clock,
  Filter,
  Search,
  ShieldAlert,
  Eye,
  X,
  Settings,
  RefreshCw,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

type AlertSeverity = "critical" | "high" | "medium" | "low" | "info";
type AlertStatus = "new" | "acknowledged" | "resolved" | "dismissed";

interface Alert {
  id: number;
  severity: AlertSeverity;
  status: AlertStatus;
  title: string;
  message: string;
  source: string;
  timestamp: string;
  assignee?: string;
}

const MOCK_ALERTS: Alert[] = [
  { id: 1, severity: "critical", status: "new", title: "Suspicious card testing pattern", message: "Multiple small-value transactions detected on card ***4821 from different countries within 5 minutes.", source: "FraudDetect v2.1", timestamp: "2 min ago" },
  { id: 2, severity: "critical", status: "new", title: "Account takeover detected", message: "Account #49281 shows signs of ATO: password reset from new IP, device fingerprint mismatch, multiple failed MFA attempts.", source: "ATO Sentinel", timestamp: "8 min ago" },
  { id: 3, severity: "high", status: "new", title: "Wire transfer velocity breach", message: "Account attempted 3 wire transfers exceeding $10,000 within 1 hour. Standard daily limit: 2 transfers.", source: "Wire Guardian", timestamp: "15 min ago" },
  { id: 4, severity: "high", status: "acknowledged", title: "Unusual login location", message: "User login from new location (Nigeria) detected for account that typically operates from US.", source: "Graph Analyzer", timestamp: "32 min ago", assignee: "Sarah Chen" },
  { id: 5, severity: "medium", status: "new", title: "Device fingerprint mismatch", message: "Transaction from device with new fingerprint attempted on account with established device history.", source: "Identity Shield", timestamp: "1 hr ago" },
  { id: 6, severity: "medium", status: "resolved", title: "Repeated declined transactions", message: "5 declined transactions followed by successful transaction - possible card testing behavior.", source: "FraudDetect v2.1", timestamp: "2 hr ago", assignee: "Marcus Reid" },
  { id: 7, severity: "low", status: "dismissed", title: "Low-value high-risk transaction", message: "Transaction of $12.50 flagged for review but below auto-action threshold.", source: "RiskScore Engine", timestamp: "3 hr ago" },
  { id: 8, severity: "info", status: "resolved", title: "OFAC sanctions list match", message: "Transaction matched OFAC sanctions screening - manually reviewed and cleared (false positive).", source: "Watchlist Monitor", timestamp: "4 hr ago", assignee: "Priya Nair" },
];

const SEVERITY_CONFIG: Record<AlertSeverity, { label: string; className: string; bgClass: string; icon: typeof ShieldAlert }> = {
  critical: { label: "Critical", className: "bg-red-500/15 text-red-400 border-red-500/25", bgClass: "bg-red-400/10", icon: ShieldAlert },
  high: { label: "High", className: "bg-orange-500/15 text-orange-400 border-orange-500/25", bgClass: "bg-orange-400/10", icon: AlertTriangle },
  medium: { label: "Medium", className: "bg-amber-500/15 text-amber-400 border-amber-500/25", bgClass: "bg-amber-400/10", icon: AlertTriangle },
  low: { label: "Low", className: "bg-emerald-500/15 text-emerald-400 border-emerald-500/25", bgClass: "bg-emerald-400/10", icon: Bell },
  info: { label: "Info", className: "bg-blue-500/15 text-blue-400 border-blue-500/25", bgClass: "bg-blue-400/10", icon: Bell },
};

const STATUS_CONFIG: Record<AlertStatus, { label: string; className: string }> = {
  new: { label: "New", className: "bg-primary/15 text-primary border-primary/25" },
  acknowledged: { label: "Acknowledged", className: "bg-amber-500/15 text-amber-400 border-amber-500/25" },
  resolved: { label: "Resolved", className: "bg-emerald-500/15 text-emerald-400 border-emerald-500/25" },
  dismissed: { label: "Dismissed", className: "bg-slate-500/15 text-slate-400 border-slate-500/25" },
};

const PAGE_SIZE = 10;

export default function AlertsPage() {
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState<AlertSeverity | "all">("all");
  const [statusFilter, setStatusFilter] = useState<AlertStatus | "all">("all");
  const [page, setPage] = useState(1);
  const [alerts, setAlerts] = useState(MOCK_ALERTS);

  const filteredAlerts = alerts.filter((alert) => {
    const matchSearch = !search || alert.title.toLowerCase().includes(search.toLowerCase()) || alert.message.toLowerCase().includes(search.toLowerCase());
    const matchSeverity = severityFilter === "all" || alert.severity === severityFilter;
    const matchStatus = statusFilter === "all" || alert.status === statusFilter;
    return matchSearch && matchSeverity && matchStatus;
  });

  const totalPages = Math.ceil(filteredAlerts.length / PAGE_SIZE);
  const pagedAlerts = filteredAlerts.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  function handleAcknowledge(id: number) {
    setAlerts((prev) => prev.map((a) => a.id === id ? { ...a, status: "acknowledged" as AlertStatus } : a));
  }

  function handleResolve(id: number) {
    setAlerts((prev) => prev.map((a) => a.id === id ? { ...a, status: "resolved" as AlertStatus } : a));
  }

  function handleDismiss(id: number) {
    setAlerts((prev) => prev.map((a) => a.id === id ? { ...a, status: "dismissed" as AlertStatus } : a));
  }

  const counts = {
    all: alerts.length,
    new: alerts.filter((a) => a.status === "new").length,
    acknowledged: alerts.filter((a) => a.status === "acknowledged").length,
    resolved: alerts.filter((a) => a.status === "resolved").length,
    dismissed: alerts.filter((a) => a.status === "dismissed").length,
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Alerts</h1>
          <p className="mt-1 text-sm text-muted-foreground">Manage and respond to fraud detection alerts</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-1.5">
            <Settings className="h-3.5 w-3.5" />
            Configure Rules
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5">
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { label: "Critical Alerts", value: alerts.filter((a) => a.severity === "critical" && a.status !== "resolved" && a.status !== "dismissed").length, icon: ShieldAlert, color: "text-red-400", bg: "bg-red-400/10" },
          { label: "New Alerts", value: counts.new, icon: Bell, color: "text-primary", bg: "bg-primary/10" },
          { label: "Acknowledged", value: counts.acknowledged, icon: Clock, color: "text-amber-400", bg: "bg-amber-400/10" },
          { label: "Resolved Today", value: counts.resolved, icon: CheckCircle2, color: "text-emerald-400", bg: "bg-emerald-400/10" },
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

      {/* Filters */}
      <Card>
        <CardContent className="flex flex-wrap items-center gap-3 py-4">
          <div className="relative min-w-[200px] flex-1">
            <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search alerts..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="h-8 pl-8 text-sm"
            />
          </div>

          <select
            value={severityFilter}
            onChange={(e) => { setSeverityFilter(e.target.value as AlertSeverity | "all"); setPage(1); }}
            className="h-8 rounded-md border border-input bg-background px-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
            <option value="info">Info</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value as AlertStatus | "all"); setPage(1); }}
            className="h-8 rounded-md border border-input bg-background px-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          >
            <option value="all">All Statuses</option>
            <option value="new">New</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="resolved">Resolved</option>
            <option value="dismissed">Dismissed</option>
          </select>

          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Filter className="h-3 w-3" />
            {filteredAlerts.length} results
          </div>
        </CardContent>
      </Card>

      {/* Tabs and Alerts List */}
      <Tabs defaultValue="all">
        <TabsList className="h-auto gap-0.5 mb-4">
          {[
            { value: "all", label: "All" },
            { value: "new", label: "New" },
            { value: "acknowledged", label: "Acknowledged" },
            { value: "resolved", label: "Resolved" },
            { value: "dismissed", label: "Dismissed" },
          ].map((tab) => (
            <TabsTrigger key={tab.value} value={tab.value} count={counts[tab.value as keyof typeof counts]}>
              {tab.label}
            </TabsTrigger>
          ))}
        </TabsList>

        {["all", "new", "acknowledged", "resolved", "dismissed"].map((status) => (
          <TabsContent key={status} value={status} className="mt-4">
            <Card>
              <CardContent className="p-0">
                {pagedAlerts.filter((a) => status === "all" || a.status === status).length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-16">
                    <BellOff className="h-8 w-8 text-muted-foreground/40" />
                    <p className="mt-2 text-sm text-muted-foreground">No alerts found</p>
                  </div>
                ) : (
                  <div className="divide-y divide-border/60">
                    {pagedAlerts
                      .filter((a) => status === "all" || a.status === status)
                      .map((alert) => {
                        const sev = SEVERITY_CONFIG[alert.severity];
                        const statusCfg = STATUS_CONFIG[alert.status];
                        const SeverityIcon = sev.icon;

                        return (
                          <div key={alert.id} className="flex items-start gap-4 px-6 py-4 hover:bg-muted/20 transition-colors">
                            <div className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-lg", sev.bgClass)}>
                              <SeverityIcon className={cn("h-4 w-4", alert.severity === "critical" ? "text-red-400" : alert.severity === "high" ? "text-orange-400" : alert.severity === "medium" ? "text-amber-400" : alert.severity === "info" ? "text-blue-400" : "text-emerald-400")} />
                            </div>
                            <div className="min-w-0 flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <span className={cn("inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide", sev.className)}>
                                  {sev.label}
                                </span>
                                <span className={cn("inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium", statusCfg.className)}>
                                  {statusCfg.label}
                                </span>
                              </div>
                              <p className="text-sm font-medium">{alert.title}</p>
                              <p className="mt-1 text-xs text-muted-foreground line-clamp-2">{alert.message}</p>
                              <div className="mt-2 flex items-center gap-4 text-xs text-muted-foreground">
                                <span>Source: {alert.source}</span>
                                <span className="flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  {alert.timestamp}
                                </span>
                                {alert.assignee && <span>Assigned to: {alert.assignee}</span>}
                              </div>
                            </div>
                            <div className="flex items-center gap-1 shrink-0">
                              {alert.status !== "resolved" && alert.status !== "dismissed" && (
                                <>
                                  <Button variant="ghost" size="sm" className="h-7 gap-1 text-xs" onClick={() => handleAcknowledge(alert.id)}>
                                    <Eye className="h-3 w-3" />
                                    Acknowledge
                                  </Button>
                                  <Button variant="ghost" size="sm" className="h-7 gap-1 text-xs text-emerald-400" onClick={() => handleResolve(alert.id)}>
                                    <CheckCircle2 className="h-3 w-3" />
                                    Resolve
                                  </Button>
                                </>
                              )}
                              {alert.status === "new" && (
                                <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground" onClick={() => handleDismiss(alert.id)}>
                                  <X className="h-4 w-4" />
                                </Button>
                              )}
                            </div>
                          </div>
                        );
                      })}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
