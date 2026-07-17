"use client";

import { use, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Circle,
  XCircle,
  TrendingUp,
  User,
  Activity,
  Send,
  Cpu,
  ShieldAlert,
  ExternalLink,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Separator } from "@/components/ui/separator";
import { SeverityBadge } from "@/components/shared/severity-badge";
import { MOCK_INVESTIGATIONS, MOCK_TRANSACTIONS, type Investigation } from "@/lib/mock-data";
import type { Severity, CaseStatus } from "@/types";

interface PageProps {
  params: Promise<{ id: string }>;
}

const STATUS_OPTIONS: { value: CaseStatus; label: string; icon: typeof Circle; className: string }[] = [
  { value: "open", label: "Open", icon: Circle, className: "text-blue-400 border-blue-500/30 bg-blue-500/10" },
  { value: "in_review", label: "In Review", icon: Clock, className: "text-amber-400 border-amber-500/30 bg-amber-500/10" },
  { value: "escalated", label: "Escalated", icon: AlertTriangle, className: "text-red-400 border-red-500/30 bg-red-500/10" },
  { value: "resolved", label: "Resolved", icon: CheckCircle2, className: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10" },
  { value: "closed", label: "Closed", icon: XCircle, className: "text-slate-400 border-slate-500/30 bg-slate-500/10" },
];

const INVESTIGATORS = [
  { name: "Alex Morgan", initials: "AM" },
  { name: "Sarah Chen", initials: "SC" },
  { name: "Marcus Reid", initials: "MR" },
  { name: "Priya Nair", initials: "PN" },
  { name: "James Wilson", initials: "JW" },
];

interface TimelineEvent {
  id: string;
  time: string;
  user: string;
  type: "system" | "agent" | "analyst";
  message: string;
}

export default function CaseDetailsPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const router = useRouter();
  const caseId = resolvedParams.id;

  const [caseData, setCaseData] = useState<Investigation | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "transactions" | "agent" | "history">("overview");
  const [newNote, setNewNote] = useState("");
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);

  // Find the investigation matching the dynamic URL parameter ID
  useEffect(() => {
    const inv = MOCK_INVESTIGATIONS.find((i) => i.id === caseId);
    if (inv) {
      setCaseData(inv);
      // Initialize timeline with realistic events
      setTimeline([
        {
          id: "1",
          time: "2024-01-14 09:12:00",
          user: "System",
          type: "system",
          message: `Investigation automatically opened based on Risk Monitor triggers.`,
        },
        {
          id: "2",
          time: "2024-01-14 09:15:33",
          user: "FraudShield-Agent-09",
          type: "agent",
          message: `Autonomous agent assigned to scan东北 corridor card activity logs. Flagged 14 matching transactions.`,
        },
        {
          id: "3",
          time: "2024-01-14 10:30:12",
          user: inv.assignedTo !== "Unassigned" ? inv.assignedTo : "Supervisor",
          type: "analyst",
          message: `Case file assigned to investigator: ${inv.assignedTo}.`,
        },
      ]);
    }
  }, [caseId]);

  if (!caseData) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center space-y-4">
        <AlertTriangle className="h-10 w-10 text-amber-500 animate-pulse" />
        <h2 className="text-xl font-bold">Investigation Not Found</h2>
        <p className="text-sm text-muted-foreground">The case ID &quot;{caseId}&quot; does not exist in the database.</p>
        <Button onClick={() => router.push("/investigations")} variant="outline" size="sm">
          <ArrowLeft className="mr-2 h-4 w-4" /> Return to Investigations
        </Button>
      </div>
    );
  }

  // Filter transactions related to this case based on the case tags
  const associatedTransactions = MOCK_TRANSACTIONS.filter((txn) => {
    // If case has a tag like card-fraud, match card transactions
    if (caseData.tags.includes("card-fraud") && txn.type.startsWith("card")) return true;
    if (caseData.tags.includes("crypto") && txn.type === "crypto") return true;
    if (caseData.tags.includes("wire") && txn.type === "wire_transfer") return true;
    // Fallback: match category or high risk score
    return txn.riskScore > 75;
  });

  const handleStatusChange = (status: CaseStatus) => {
    setCaseData((prev) => (prev ? { ...prev, status } : null));
    const now = new Date().toISOString().replace("T", " ").slice(0, 19);
    setTimeline((prev) => [
      ...prev,
      {
        id: Math.random().toString(),
        time: now,
        user: "Analyst",
        type: "analyst",
        message: `Status updated to ${status.replace("_", " ").toUpperCase()}`,
      },
    ]);
  };

  const handleAssigneeChange = (name: string) => {
    const inv = INVESTIGATORS.find((i) => i.name === name);
    setCaseData((prev) =>
      prev
        ? {
            ...prev,
            assignedTo: name,
            assigneeInitials: inv ? inv.initials : "—",
          }
        : null
    );
    const now = new Date().toISOString().replace("T", " ").slice(0, 19);
    setTimeline((prev) => [
      ...prev,
      {
        id: Math.random().toString(),
        time: now,
        user: "Analyst",
        type: "analyst",
        message: `Investigator assigned: ${name}`,
      },
    ]);
  };

  const handleAddNote = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNote.trim()) return;

    const now = new Date().toISOString().replace("T", " ").slice(0, 19);
    setTimeline((prev) => [
      ...prev,
      {
        id: Math.random().toString(),
        time: now,
        user: "Analyst (You)",
        type: "analyst",
        message: newNote,
      },
    ]);
    setNewNote("");
  };

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      {/* Back button & title */}
      <div className="flex items-center gap-3">
        <Button onClick={() => router.push("/investigations")} variant="ghost" size="icon" className="h-8 w-8">
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <span className="font-mono text-xs text-muted-foreground">{caseData.id}</span>
        <Separator orientation="vertical" className="h-4" />
        <h1 className="text-xl font-bold tracking-tight">{caseData.title}</h1>
      </div>

      {/* Grid container */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left Side: Detail Contents & Tabs */}
        <div className="lg:col-span-2 space-y-6">
          {/* Stats Bar */}
          <Card className="grid grid-cols-2 gap-4 p-5 sm:grid-cols-4 bg-card/65 backdrop-blur-md">
            <div>
              <p className="text-xs text-muted-foreground">Estimated Loss</p>
              <p className="mt-1 text-2xl font-bold text-red-400 tabular-nums">${caseData.estimatedLoss.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Linked Txns</p>
              <p className="mt-1 text-2xl font-bold tabular-nums">{caseData.transactionCount}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Risk Level</p>
              <div className="mt-1.5">
                <SeverityBadge severity={caseData.severity as Severity} />
              </div>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Case Age</p>
              <p className="mt-1 text-sm font-semibold text-foreground">2 days open</p>
            </div>
          </Card>

          {/* Navigation Tabs */}
          <div className="flex border-b border-border">
            {([
              { id: "overview", label: "Overview", icon: Activity },
              { id: "transactions", label: `Linked Transactions (${associatedTransactions.length})`, icon: TrendingUp },
              { id: "agent", label: "AI Investigator", icon: Cpu },
              { id: "history", label: "Audit Timeline", icon: Calendar },
            ] as const).map((t) => {
              const TabIcon = t.icon;
              return (
                <button
                  key={t.id}
                  onClick={() => setActiveTab(t.id)}
                  className={`flex items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-medium transition-colors ${
                    activeTab === t.id
                      ? "border-primary text-primary"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <TabIcon className="h-4 w-4" />
                  {t.label}
                </button>
              );
            })}
          </div>

          {/* Tab Contents */}
          {activeTab === "overview" && (
            <div className="space-y-6">
              {/* Summary description */}
              <Card className="p-6 space-y-4 bg-card/40">
                <h3 className="text-sm font-semibold text-foreground">Investigation Summary</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Active fraud cluster investigation targeting card-skimming network anomalies across retail
                  locations. The pattern involves rapid consecutive card-not-present (CNP) purchases, mismatched geographic IPs,
                  and transaction signatures pointing to automated credential stuffing. Autonomous AI Agent telemetry is mapping
                  threat actors to localized mule nodes.
                </p>
                <div className="flex flex-wrap gap-1.5 pt-2">
                  {caseData.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-primary/10 border border-primary/20 px-2 py-0.5 text-xs text-primary"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </Card>

              {/* Fraud Entity Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="p-5 space-y-3 bg-card/40 border-border/80">
                  <h4 className="text-xs font-semibold text-primary uppercase tracking-wider flex items-center gap-1.5">
                    <ShieldAlert className="h-3.5 w-3.5" /> High-Risk Indicators
                  </h4>
                  <ul className="space-y-2.5 text-sm text-muted-foreground">
                    <li className="flex justify-between border-b border-border/40 pb-1.5">
                      <span>Velocity Violations</span>
                      <span className="font-semibold text-foreground">18 triggers</span>
                    </li>
                    <li className="flex justify-between border-b border-border/40 pb-1.5">
                      <span>Device Fingerprint Match</span>
                      <span className="font-semibold text-foreground">4 accounts</span>
                    </li>
                    <li className="flex justify-between">
                      <span>Mismatched IP/Billing</span>
                      <span className="font-semibold text-foreground">100% mismatch</span>
                    </li>
                  </ul>
                </Card>
                <Card className="p-5 space-y-3 bg-card/40 border-border/80">
                  <h4 className="text-xs font-semibold text-primary uppercase tracking-wider flex items-center gap-1.5">
                    <User className="h-3.5 w-3.5" /> Target Entities
                  </h4>
                  <ul className="space-y-2.5 text-sm text-muted-foreground">
                    <li className="flex justify-between border-b border-border/40 pb-1.5">
                      <span>Card Signatures</span>
                      <span className="font-mono font-semibold text-foreground">Visa ending 4821</span>
                    </li>
                    <li className="flex justify-between border-b border-border/40 pb-1.5">
                      <span>Target Merchants</span>
                      <span className="font-semibold text-foreground">Amazon, Target, CVS</span>
                    </li>
                    <li className="flex justify-between">
                      <span>Geographic Source</span>
                      <span className="font-semibold text-foreground">Northeastern US Corridor</span>
                    </li>
                  </ul>
                </Card>
              </div>
            </div>
          )}

          {activeTab === "transactions" && (
            <Card className="overflow-hidden border border-border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Txn ID</TableHead>
                    <TableHead>Merchant</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Risk Score</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                    <TableHead>Timestamp</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {associatedTransactions.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="py-8 text-center text-muted-foreground text-sm">
                        No transactions linked.
                      </TableCell>
                    </TableRow>
                  ) : (
                    associatedTransactions.map((t) => (
                      <TableRow key={t.id}>
                        <TableCell className="font-mono text-xs text-muted-foreground">{t.id}</TableCell>
                        <TableCell className="font-medium">{t.merchant}</TableCell>
                        <TableCell className="text-xs">{t.category}</TableCell>
                        <TableCell>
                          <span
                            className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${
                              t.riskScore > 80
                                ? "bg-red-500/10 text-red-400"
                                : t.riskScore > 50
                                ? "bg-amber-500/10 text-amber-400"
                                : "bg-emerald-500/10 text-emerald-400"
                            }`}
                          >
                            {t.riskScore}
                          </span>
                        </TableCell>
                        <TableCell className="text-right font-semibold tabular-nums">${t.amount.toFixed(2)}</TableCell>
                        <TableCell className="text-xs text-muted-foreground">{t.timestamp}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </Card>
          )}

          {activeTab === "agent" && (
            <div className="space-y-6">
              {/* Agent Profile */}
              <Card className="p-6 bg-card/65 border-border/80 flex items-start gap-4">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 border border-primary/20 text-primary">
                  <Cpu className="h-6 w-6" />
                </div>
                <div className="space-y-1">
                  <h3 className="text-sm font-semibold">FraudShield-Agent-09</h3>
                  <p className="text-xs text-muted-foreground">Model: <span className="font-mono">gemini-1.5-pro</span> · Temperature: <span className="font-mono">0.0</span></p>
                  <p className="text-xs text-muted-foreground">Status: <span className="text-emerald-400 font-semibold">Active Scanning</span></p>
                </div>
                <div className="ml-auto text-right">
                  <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/15 px-2.5 py-0.5 text-xs font-medium text-emerald-400">
                    98% Confidence
                  </span>
                </div>
              </Card>

              {/* Agent Telemetry Reasoning Log */}
              <Card className="p-6 space-y-4">
                <h4 className="text-sm font-semibold">Agent Reasoning Steps</h4>
                <div className="space-y-4 border-l border-border pl-4">
                  {[
                    { step: "Step 1: Identity Aggregation", desc: "Cross-referenced mismatched shipping/billing details. Flagged device fingerprint match (ID: dfp_東北_449) on regional cards." },
                    { step: "Step 2: Transaction Velocity Map", desc: "Monitored velocity spike. Target cards registered consecutive CNP purchases at regional merchants within 4.5 seconds." },
                    { step: "Step 3: Fraud Cluster Graphing", desc: "Linked Northeast region electronics purchase records to active international carding telegram rings. Probability score: 94.8%." },
                    { step: "Step 4: Recommended Action", desc: "Trigger automatic transaction hold on target regional merchant IDs. Request human investigator approval to update case status to 'Escalated'." },
                  ].map((s, idx) => (
                    <div key={idx} className="relative space-y-1">
                      <div className="absolute -left-[21px] top-1.5 h-2 w-2 rounded-full bg-primary" />
                      <h5 className="text-sm font-semibold text-foreground">{s.step}</h5>
                      <p className="text-xs text-muted-foreground leading-relaxed">{s.desc}</p>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {activeTab === "history" && (
            <Card className="p-6 space-y-4">
              <h4 className="text-sm font-semibold">Audit Event History</h4>
              <div className="space-y-4 pl-1">
                {timeline.map((event) => (
                  <div key={event.id} className="flex gap-4 text-sm pb-4 border-b border-border/40 last:border-0 last:pb-0">
                    <span className="text-xs font-mono text-muted-foreground/60 w-32 shrink-0">{event.time}</span>
                    <div className="space-y-1">
                      <p className="font-semibold text-foreground flex items-center gap-2">
                        {event.user}
                        <span
                          className={`text-[10px] font-normal px-1.5 py-0.2 rounded-full ${
                            event.type === "agent"
                              ? "bg-purple-500/10 text-purple-400 border border-purple-500/20"
                              : event.type === "system"
                              ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                              : "bg-slate-500/10 text-slate-400 border border-slate-500/20"
                          }`}
                        >
                          {event.type}
                        </span>
                      </p>
                      <p className="text-sm text-muted-foreground leading-relaxed">{event.message}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Add Note Form */}
              <form onSubmit={handleAddNote} className="flex gap-2 pt-4 border-t border-border">
                <Input
                  placeholder="Type an analyst comment..."
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  className="flex-1 h-9 text-sm"
                />
                <Button type="submit" size="sm" className="gap-1.5">
                  <Send className="h-3.5 w-3.5" />
                  Add Note
                </Button>
              </form>
            </Card>
          )}
        </div>

        {/* Right Side: Case Action Controllers */}
        <div className="space-y-6">
          <Card className="p-6 space-y-6 bg-card/65 backdrop-blur-md border-border">
            <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider">Case Management</h3>

            {/* Status controller */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-muted-foreground">Update Case Status</label>
              <div className="grid grid-cols-1 gap-1.5">
                {STATUS_OPTIONS.map((opt) => {
                  const Icon = opt.icon;
                  const isActive = caseData.status === opt.value;
                  return (
                    <button
                      key={opt.value}
                      onClick={() => handleStatusChange(opt.value)}
                      className={`flex items-center justify-between px-3 py-2 rounded-lg border text-sm font-medium transition-all ${
                        isActive
                          ? `${opt.className} border-primary/50 shadow-sm shadow-primary/5`
                          : "border-border bg-transparent text-muted-foreground hover:bg-accent/40"
                      }`}
                    >
                      <span className="flex items-center gap-2">
                        <Icon className="h-4 w-4" />
                        {opt.label}
                      </span>
                      {isActive && <div className="h-1.5 w-1.5 rounded-full bg-primary" />}
                    </button>
                  );
                })}
              </div>
            </div>

            <Separator className="border-border/60" />

            {/* Assignee controller */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-muted-foreground">Assign Investigator</label>
              <select
                value={caseData.assignedTo}
                onChange={(e) => handleAssigneeChange(e.target.value)}
                className="w-full h-9 rounded-md border border-input bg-background px-3 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              >
                <option value="Unassigned">Unassigned</option>
                {INVESTIGATORS.map((inv) => (
                  <option key={inv.name} value={inv.name}>
                    {inv.name}
                  </option>
                ))}
              </select>
            </div>

            <Separator className="border-border/60" />

            {/* Quick Actions */}
            <div className="space-y-2.5">
              <label className="text-xs font-medium text-muted-foreground">Security Action Overrides</label>
              <Button variant="outline" className="w-full justify-start text-xs h-8 text-red-400 hover:text-red-300 hover:bg-red-500/5 border-red-500/20" size="sm">
                <ShieldAlert className="mr-2 h-3.5 w-3.5 text-red-500" /> Freeze Billing Profile
              </Button>
              <Button variant="outline" className="w-full justify-start text-xs h-8" size="sm">
                <ExternalLink className="mr-2 h-3.5 w-3.5 text-muted-foreground" /> Export Legal Case Briefinging
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
