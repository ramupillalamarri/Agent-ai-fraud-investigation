"use client";

import { useState, useMemo } from "react";
import {
  CreditCard,
  AlertTriangle,
  CheckCircle2,
  Ban,
  Search,
  Filter,
  Download,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  MoreHorizontal,
  Eye,
  Flag,
  Shield,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { RiskScoreBadge } from "@/components/shared/risk-score";
import { MOCK_TRANSACTIONS, type TxStatus } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

const PAGE_SIZE = 10;

const STATUS_CONFIG: Record<TxStatus, { label: string; className: string; icon: typeof CheckCircle2 }> = {
  flagged: { label: "Flagged", className: "bg-red-500/15 text-red-400 border-red-500/20", icon: Flag },
  reviewed: { label: "Reviewed", className: "bg-amber-500/15 text-amber-400 border-amber-500/20", icon: Eye },
  blocked: { label: "Blocked", className: "bg-slate-500/15 text-slate-400 border-slate-500/20", icon: Ban },
  cleared: { label: "Cleared", className: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20", icon: CheckCircle2 },
};

const TYPE_LABELS: Record<string, string> = {
  card_not_present: "Card — CNP",
  card_present: "Card — Present",
  ach_transfer: "ACH Transfer",
  wire_transfer: "Wire Transfer",
  crypto: "Crypto",
};

const SUMMARY_STATS = [
  { label: "Total Transactions", value: "48,291", sub: "today", icon: CreditCard, color: "text-blue-400", bg: "bg-blue-400/10" },
  { label: "Flagged", value: "1,847", sub: "pending review", icon: AlertTriangle, color: "text-red-400", bg: "bg-red-400/10" },
  { label: "Reviewed", value: "12,430", sub: "this week", icon: Eye, color: "text-amber-400", bg: "bg-amber-400/10" },
  { label: "Blocked", value: "284", sub: "auto-blocked", icon: Shield, color: "text-emerald-400", bg: "bg-emerald-400/10" },
];

export default function TransactionsPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | TxStatus>("all");
  const [riskFilter, setRiskFilter] = useState<"all" | "critical" | "high" | "medium" | "low">("all");
  const [page, setPage] = useState(1);

  const filtered = useMemo(() => {
    return MOCK_TRANSACTIONS.filter((tx) => {
      const matchSearch =
        !search ||
        tx.id.toLowerCase().includes(search.toLowerCase()) ||
        tx.merchant.toLowerCase().includes(search.toLowerCase());
      const matchStatus = statusFilter === "all" || tx.status === statusFilter;
      const matchRisk =
        riskFilter === "all" ||
        (riskFilter === "critical" && tx.riskScore >= 80) ||
        (riskFilter === "high" && tx.riskScore >= 60 && tx.riskScore < 80) ||
        (riskFilter === "medium" && tx.riskScore >= 40 && tx.riskScore < 60) ||
        (riskFilter === "low" && tx.riskScore < 40);
      return matchSearch && matchStatus && matchRisk;
    });
  }, [search, statusFilter, riskFilter]);

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paged = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  function handleFilterChange() {
    setPage(1);
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Transactions</h1>
          <p className="mt-1 text-sm text-muted-foreground">Monitor and triage flagged payment activity</p>
        </div>
        <Button variant="outline" size="sm" className="gap-1.5">
          <Download className="h-3.5 w-3.5" />
          Export CSV
        </Button>
      </div>

      {/* Summary cards */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {SUMMARY_STATS.map((s) => (
          <Card key={s.label} className="gradient-border">
            <CardContent className="flex items-center gap-4 py-4">
              <div className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-lg", s.bg)}>
                <s.icon className={cn("h-5 w-5", s.color)} />
              </div>
              <div>
                <p className="text-2xl font-bold tabular-nums">{s.value}</p>
                <p className="text-xs text-muted-foreground">{s.label}</p>
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
              placeholder="Search by ID or merchant…"
              value={search}
              onChange={(e) => { setSearch(e.target.value); handleFilterChange(); }}
              className="h-8 pl-8 text-sm"
            />
          </div>

          {/* Status filter */}
          <div className="flex items-center gap-1.5 rounded-lg border border-border bg-muted/40 p-1">
            {(["all", "flagged", "reviewed", "blocked", "cleared"] as const).map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => { setStatusFilter(s); handleFilterChange(); }}
                className={cn(
                  "rounded-md px-2.5 py-1 text-xs font-medium capitalize transition-colors",
                  statusFilter === s
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                {s === "all" ? "All" : STATUS_CONFIG[s].label}
              </button>
            ))}
          </div>

          {/* Risk filter */}
          <select
            value={riskFilter}
            onChange={(e) => { setRiskFilter(e.target.value as typeof riskFilter); handleFilterChange(); }}
            className="h-8 rounded-md border border-input bg-background px-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          >
            <option value="all">All Risk Levels</option>
            <option value="critical">Critical (80+)</option>
            <option value="high">High (60–79)</option>
            <option value="medium">Medium (40–59)</option>
            <option value="low">Low (&lt;40)</option>
          </select>

          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Filter className="h-3 w-3" />
            {filtered.length} results
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-32">
                <div className="flex items-center gap-1">Tx ID <ArrowUpDown className="h-3 w-3 opacity-50" /></div>
              </TableHead>
              <TableHead>Timestamp</TableHead>
              <TableHead>Merchant</TableHead>
              <TableHead className="text-right">Amount</TableHead>
              <TableHead className="w-36">Risk Score</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-12" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {paged.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="py-16 text-center text-muted-foreground">
                  No transactions match your filters.
                </TableCell>
              </TableRow>
            ) : (
              paged.map((tx) => {
                const sc = STATUS_CONFIG[tx.status];
                return (
                  <TableRow key={tx.id}>
                    <TableCell>
                      <span className="font-mono text-xs text-muted-foreground">{tx.id}</span>
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="text-xs">{tx.timestamp.split(" ")[0]}</p>
                        <p className="text-[11px] text-muted-foreground">{tx.timestamp.split(" ")[1]}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="text-sm font-medium">{tx.merchant}</p>
                        <p className="text-[11px] text-muted-foreground">
                          {tx.category} · {tx.country}
                          {tx.cardLast4 !== "—" && ` · ···${tx.cardLast4}`}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <span className="font-semibold tabular-nums">
                        ${tx.amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                      </span>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <RiskScoreBadge score={tx.riskScore} />
                        <div className="h-1.5 w-16 overflow-hidden rounded-full bg-muted">
                          <div
                            className={cn(
                              "h-full rounded-full",
                              tx.riskScore >= 80 ? "bg-red-500" : tx.riskScore >= 60 ? "bg-orange-500" : tx.riskScore >= 40 ? "bg-amber-500" : "bg-emerald-500",
                            )}
                            style={{ width: `${tx.riskScore}%` }}
                          />
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="text-xs text-muted-foreground">{TYPE_LABELS[tx.type] ?? tx.type}</span>
                    </TableCell>
                    <TableCell>
                      <span
                        className={cn(
                          "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium",
                          sc.className,
                        )}
                      >
                        <sc.icon className="h-2.5 w-2.5" />
                        {sc.label}
                      </span>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-7 w-7">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-44">
                          <DropdownMenuItem className="gap-2">
                            <Eye className="h-4 w-4" /> View details
                          </DropdownMenuItem>
                          <DropdownMenuItem className="gap-2">
                            <Flag className="h-4 w-4" /> Flag for review
                          </DropdownMenuItem>
                          <DropdownMenuItem className="gap-2">
                            <FileSearch className="h-4 w-4" /> Open investigation
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem className="gap-2 text-destructive focus:text-destructive">
                            <Ban className="h-4 w-4" /> Block transaction
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>

        {/* Pagination */}
        <div className="flex items-center justify-between border-t border-border px-4 py-3">
          <p className="text-xs text-muted-foreground">
            {filtered.length === 0 ? "0 results" : `Showing ${(page - 1) * PAGE_SIZE + 1}–${Math.min(page * PAGE_SIZE, filtered.length)} of ${filtered.length}`}
          </p>
          <div className="flex items-center gap-1">
            <Button
              variant="outline"
              size="sm"
              className="h-7 w-7 p-0"
              disabled={page === 1}
              onClick={() => setPage((p) => p - 1)}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
              <Button
                key={p}
                variant={p === page ? "default" : "ghost"}
                size="sm"
                className="h-7 w-7 p-0 text-xs"
                onClick={() => setPage(p)}
              >
                {p}
              </Button>
            ))}
            <Button
              variant="outline"
              size="sm"
              className="h-7 w-7 p-0"
              disabled={page === totalPages || totalPages === 0}
              onClick={() => setPage((p) => p + 1)}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}

// needed for page-level icon reference
function FileSearch({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><circle cx="11.5" cy="14.5" r="2.5" /><path d="M13.25 16.25 15 18" />
    </svg>
  );
}
