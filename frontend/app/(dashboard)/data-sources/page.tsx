"use client";

import { useState } from "react";
import {
  Database,
  RefreshCw,
  Plus,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Settings,
  Trash2,
  ExternalLink,
  FileJson,
  CreditCard,
  Building2,
  Shield,
  MessageSquare,
  BarChart3,
  Link2,
  XCircle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface DataSource {
  id: string;
  name: string;
  type: "api" | "database" | "file" | "webhook";
  provider: string;
  status: "connected" | "disconnected" | "error" | "syncing";
  lastSync: string;
  recordsCount: number;
  icon: string;
  description: string;
  syncInterval: string;
}

const DATA_SOURCES: DataSource[] = [
  { id: "stripe", name: "Stripe Radar", type: "api", provider: "Payment Gateway", status: "connected", lastSync: "2 min ago", recordsCount: 2847391, icon: "💳", description: "Real-time transaction data and payment signals from Stripe", syncInterval: "Real-time" },
  { id: "plaid", name: "Plaid", type: "api", provider: "Banking Data", status: "connected", lastSync: "15 min ago", recordsCount: 847293, icon: "🏦", description: "Bank account verification and ACH transfer data", syncInterval: "15 min" },
  { id: "ofac", name: "OFAC Sanctions List", type: "api", provider: "Government Database", status: "connected", lastSync: "1 hr ago", recordsCount: 12487, icon: "🛡️", description: "Real-time sanctions screening and watchlist data", syncInterval: "1 hour" },
  { id: "slack", name: "Slack", type: "webhook", provider: "Notifications", status: "connected", lastSync: "Real-time", recordsCount: 0, icon: "💬", description: "Alert notifications to Slack channels", syncInterval: "Event-driven" },
  { id: "splunk", name: "Splunk SIEM", type: "api", provider: "Security Analytics", status: "disconnected", lastSync: "—", recordsCount: 0, icon: "📊", description: "Security event log forwarding and correlation", syncInterval: "N/A" },
  { id: "salesforce", name: "Salesforce CRM", type: "api", provider: "Customer Data", status: "disconnected", lastSync: "—", recordsCount: 0, icon: "☁️", description: "Customer data enrichment and account intelligence", syncInterval: "N/A" },
  { id: "txn-history", name: "Transaction History", type: "database", provider: "Internal Database", status: "connected", lastSync: "5 min ago", recordsCount: 12847923, icon: "📁", description: "Historical transaction records for pattern analysis", syncInterval: "5 min" },
  { id: "merchant-db", name: "Merchant Database", type: "database", provider: "Internal Database", status: "connected", lastSync: "1 hr ago", recordsCount: 847293, icon: "🏪", description: "Merchant profiles, categories, and risk ratings", syncInterval: "1 hour" },
];

const STATUS_CONFIG = {
  connected: { label: "Connected", className: "bg-emerald-500/15 text-emerald-400", icon: CheckCircle2 },
  disconnected: { label: "Disconnected", className: "bg-slate-500/15 text-slate-400", icon: XCircle },
  error: { label: "Error", className: "bg-red-500/15 text-red-400", icon: AlertTriangle },
  syncing: { label: "Syncing", className: "bg-amber-500/15 text-amber-400", icon: RefreshCw },
};

const TYPE_CONFIG = {
  api: { label: "API", icon: Link2 },
  database: { label: "Database", icon: Database },
  file: { label: "File Import", icon: FileJson },
  webhook: { label: "Webhook", icon: MessageSquare },
};

export default function DataSourcesPage() {
  const [sources, setSources] = useState(DATA_SOURCES);
  const [filter, setFilter] = useState<"all" | "connected" | "disconnected">("all");

  const filteredSources = sources.filter((source) => {
    if (filter === "all") return true;
    return source.status === filter;
  });

  const connectedCount = sources.filter((s) => s.status === "connected").length;
  const totalRecords = sources.reduce((acc, s) => acc + s.recordsCount, 0);

  function reconnect(id: string) {
    setSources((prev) => prev.map((s) => s.id === id ? { ...s, status: "syncing" as const } : s));
    setTimeout(() => {
      setSources((prev) => prev.map((s) => s.id === id ? { ...s, status: "connected" as const } : s));
    }, 2000);
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Data Sources</h1>
          <p className="mt-1 text-sm text-muted-foreground">Connect and manage external data integrations</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-1.5">
            <Plus className="h-3.5 w-3.5" />
            Add Source
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5">
            <RefreshCw className="h-3.5 w-3.5" />
            Sync All
          </Button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { label: "Connected Sources", value: `${connectedCount} / ${sources.length}`, icon: Link2, color: "text-emerald-400", bg: "bg-emerald-400/10" },
          { label: "Total Records", value: totalRecords > 1000000 ? `${(totalRecords / 1000000).toFixed(1)}M` : `${(totalRecords / 1000).toFixed(0)}K`, icon: Database, color: "text-blue-400", bg: "bg-blue-400/10" },
          { label: "API Sources", value: sources.filter((s) => s.type === "api").length.toString(), icon: Link2, color: "text-violet-400", bg: "bg-violet-400/10" },
          { label: "Last Sync", value: "2 min ago", icon: Clock, color: "text-amber-400", bg: "bg-amber-400/10" },
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

      {/* Filter */}
      <Card>
        <CardContent className="flex items-center gap-3 py-4">
          <span className="text-sm text-muted-foreground">Filter:</span>
          {(["all", "connected", "disconnected"] as const).map((f) => (
            <button
              key={f}
              type="button"
              onClick={() => setFilter(f)}
              className={cn(
                "rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
                filter === f ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground hover:bg-muted"
              )}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
          <span className="ml-auto text-xs text-muted-foreground">{filteredSources.length} sources</span>
        </CardContent>
      </Card>

      {/* Data Sources Grid */}
      <div className="grid gap-4 md:grid-cols-2">
        {filteredSources.map((source) => {
          const statusCfg = STATUS_CONFIG[source.status];
          const typeCfg = TYPE_CONFIG[source.type];
          const StatusIcon = statusCfg.icon;
          const TypeIcon = typeCfg.icon;

          return (
            <Card key={source.id} className="overflow-hidden">
              <CardContent className="p-0">
                <div className="flex items-start gap-4 p-5">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-border bg-muted/50 text-2xl">
                    {source.icon}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-sm font-semibold">{source.name}</p>
                      <Badge variant="outline" className="text-[10px]">
                        <TypeIcon className="h-3 w-3 mr-1" />
                        {typeCfg.label}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">{source.provider}</p>
                    <p className="mt-2 text-xs text-muted-foreground line-clamp-2">{source.description}</p>
                  </div>
                </div>

                <div className="border-t border-border bg-muted/30 px-5 py-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <StatusIcon className={cn("h-3 w-3", source.status === "connected" ? "text-emerald-400" : source.status === "error" ? "text-red-400" : "text-muted-foreground")} />
                        {statusCfg.label}
                      </span>
                      {source.recordsCount > 0 && (
                        <span className="flex items-center gap-1">
                          <Database className="h-3 w-3" />
                          {source.recordsCount.toLocaleString()} records
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {source.lastSync}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 border-t border-border px-5 py-3">
                  {source.status === "connected" ? (
                    <>
                      <Button variant="outline" size="sm" className="h-7 flex-1 gap-1 text-xs">
                        <RefreshCw className="h-3 w-3" />
                        Sync Now
                      </Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </>
                  ) : source.status === "disconnected" || source.status === "error" ? (
                    <>
                      <Button variant="default" size="sm" className="h-7 flex-1 gap-1 text-xs" onClick={() => reconnect(source.id)}>
                        <Link2 className="h-3 w-3" />
                        Reconnect
                      </Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-destructive">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </>
                  ) : (
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <RefreshCw className="h-3 w-3 animate-spin" />
                      Syncing...
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Integration Guides */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Integration Guides</CardTitle>
          <CardDescription>Learn how to connect new data sources</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-3">
          {[
            { icon: CreditCard, title: "Payment Gateways", desc: "Connect Stripe, PayPal, Square, and other payment processors" },
            { icon: Building2, title: "Banking Data", desc: "Link bank accounts via Plaid, Yodlee, or direct API connections" },
            { icon: Shield, title: "Sanctions Lists", desc: "Integrate OFAC, EU, UN, and custom watchlists" },
            { icon: BarChart3, title: "Analytics Platforms", desc: "Connect Splunk, Datadog, and other SIEM solutions" },
            { icon: MessageSquare, title: "Communication", desc: "Set up Slack, Teams, and email notifications" },
            { icon: Database, title: "Custom Sources", desc: "Connect your own databases and internal systems" },
          ].map((guide, i) => (
            <div key={i} className="flex items-start gap-3 rounded-lg border border-border p-3 hover:bg-muted/20 transition-colors cursor-pointer">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                <guide.icon className="h-4 w-4 text-primary" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium">{guide.title}</p>
                <p className="text-xs text-muted-foreground">{guide.desc}</p>
              </div>
              <ExternalLink className="h-4 w-4 shrink-0 text-muted-foreground" />
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
