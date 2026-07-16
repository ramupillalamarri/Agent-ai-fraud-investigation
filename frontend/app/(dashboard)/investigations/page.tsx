"use client";

import { useState, useMemo } from "react";
import {
  Plus,
  Search,
  Filter,
  Download,
  ChevronLeft,
  ChevronRight,
  MoreHorizontal,
  Eye,
  UserPlus,
  ArrowUpRight,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Circle,
  XCircle,
  FileSearch,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { SeverityBadge } from "@/components/shared/severity-badge";
import { MOCK_INVESTIGATIONS, type Investigation } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import type { CaseStatus, Severity } from "@/types";

const PAGE_SIZE = 8;

const STATUS_CONFIG: Record<CaseStatus, { label: string; className: string; icon: typeof Circle }> = {
  open: { label: "Open", className: "bg-blue-500/15 text-blue-400", icon: Circle },
  in_review: { label: "In Review", className: "bg-amber-500/15 text-amber-400", icon: Clock },
  escalated: { label: "Escalated", className: "bg-red-500/15 text-red-400", icon: AlertTriangle },
  resolved: { label: "Resolved", className: "bg-emerald-500/15 text-emerald-400", icon: CheckCircle2 },
  closed: { label: "Closed", className: "bg-slate-500/15 text-slate-400", icon: XCircle },
};

const TAB_STATUSES: Record<string, CaseStatus[] | "all"> = {
  all: "all",
  open: ["open"],
  in_review: ["in_review"],
  escalated: ["escalated"],
  resolved: ["resolved", "closed"],
};

function countByStatus(invs: Investigation[], statuses: CaseStatus[] | "all") {
  if (statuses === "all") return invs.length;
  return invs.filter((i) => statuses.includes(i.status)).length;
}

export default function InvestigationsPage() {
  const [activeTab, setActiveTab] = useState("all");
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [page, setPage] = useState(1);

  const filtered = useMemo(() => {
    const statuses = TAB_STATUSES[activeTab];
    return MOCK_INVESTIGATIONS.filter((inv) => {
      const matchTab = statuses === "all" || statuses.includes(inv.status);
      const matchSearch =
        !search ||
        inv.id.toLowerCase().includes(search.toLowerCase()) ||
        inv.title.toLowerCase().includes(search.toLowerCase()) ||
        inv.assignedTo.toLowerCase().includes(search.toLowerCase());
      const matchSev = severityFilter === "all" || inv.severity === severityFilter;
      return matchTab && matchSearch && matchSev;
    });
  }, [activeTab, search, severityFilter]);

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paged = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  function resetPage() {
    setPage(1);
  }

  const tabs = [
    { value: "all", label: "All" },
    { value: "open", label: "Open" },
    { value: "in_review", label: "In Review" },
    { value: "escalated", label: "Escalated" },
    { value: "resolved", label: "Resolved" },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Investigations</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {MOCK_INVESTIGATIONS.length} total cases · {countByStatus(MOCK_INVESTIGATIONS, ["open"])} open ·{" "}
            {countByStatus(MOCK_INVESTIGATIONS, ["escalated"])} escalated
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-1.5">
            <Download className="h-3.5 w-3.5" />
            Export
          </Button>
          <Button size="sm" className="gap-1.5">
            <Plus className="h-3.5 w-3.5" />
            New Investigation
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={(v) => { setActiveTab(v); resetPage(); }}>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <TabsList className="h-auto gap-0.5">
            {tabs.map((t) => (
              <TabsTrigger
                key={t.value}
                value={t.value}
                count={countByStatus(MOCK_INVESTIGATIONS, TAB_STATUSES[t.value])}
              >
                {t.label}
              </TabsTrigger>
            ))}
          </TabsList>

          {/* Filters */}
          <div className="flex items-center gap-2">
            <div className="relative w-56">
              <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search cases…"
                value={search}
                onChange={(e) => { setSearch(e.target.value); resetPage(); }}
                className="h-8 pl-8 text-sm"
              />
            </div>
            <select
              value={severityFilter}
              onChange={(e) => { setSeverityFilter(e.target.value); resetPage(); }}
              className="h-8 rounded-md border border-input bg-background px-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Filter className="h-3 w-3" />
              {filtered.length}
            </div>
          </div>
        </div>

        {/* One TabsContent for all tabs to share the table */}
        {tabs.map((t) => (
          <TabsContent key={t.value} value={t.value} className="mt-4">
            <Card>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-32">Case ID</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead className="w-24">Severity</TableHead>
                    <TableHead className="w-28">Status</TableHead>
                    <TableHead className="w-32">Investigator</TableHead>
                    <TableHead className="w-24 text-right">Est. Loss</TableHead>
                    <TableHead className="w-24">Txns</TableHead>
                    <TableHead className="w-24">Updated</TableHead>
                    <TableHead className="w-12" />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paged.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={9} className="py-16 text-center">
                        <div className="flex flex-col items-center gap-2">
                          <FileSearch className="h-8 w-8 text-muted-foreground/40" />
                          <p className="text-sm text-muted-foreground">No investigations found</p>
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    paged.map((inv) => {
                      const sc = STATUS_CONFIG[inv.status];
                      const StatusIcon = sc.icon;
                      return (
                        <TableRow key={inv.id}>
                          <TableCell>
                            <span className="font-mono text-xs text-muted-foreground">{inv.id}</span>
                          </TableCell>
                          <TableCell>
                            <div className="max-w-sm">
                              <p className="text-sm font-medium leading-snug">{inv.title}</p>
                              <div className="mt-1 flex flex-wrap gap-1">
                                {inv.tags.slice(0, 2).map((tag) => (
                                  <span
                                    key={tag}
                                    className="rounded-full bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground"
                                  >
                                    {tag}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <SeverityBadge severity={inv.severity as Severity} />
                          </TableCell>
                          <TableCell>
                            <span
                              className={cn(
                                "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium",
                                sc.className,
                              )}
                            >
                              <StatusIcon className="h-2.5 w-2.5" />
                              {sc.label}
                            </span>
                          </TableCell>
                          <TableCell>
                            {inv.assignedTo === "Unassigned" ? (
                              <span className="text-xs text-muted-foreground italic">Unassigned</span>
                            ) : (
                              <div className="flex items-center gap-1.5">
                                <div className="flex h-5 w-5 items-center justify-center rounded-full bg-primary/20 text-[10px] font-bold text-primary">
                                  {inv.assigneeInitials}
                                </div>
                                <span className="text-xs">{inv.assignedTo.split(" ")[0]}</span>
                              </div>
                            )}
                          </TableCell>
                          <TableCell className="text-right">
                            <span className="text-sm font-semibold tabular-nums">
                              ${(inv.estimatedLoss / 1000).toFixed(0)}k
                            </span>
                          </TableCell>
                          <TableCell>
                            <span className="text-xs text-muted-foreground">{inv.transactionCount.toLocaleString()}</span>
                          </TableCell>
                          <TableCell>
                            <span className="text-xs text-muted-foreground">{inv.updatedAt}</span>
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
                                  <Eye className="h-4 w-4" /> View case
                                </DropdownMenuItem>
                                <DropdownMenuItem className="gap-2">
                                  <UserPlus className="h-4 w-4" /> Assign investigator
                                </DropdownMenuItem>
                                <DropdownMenuItem className="gap-2">
                                  <ArrowUpRight className="h-4 w-4" /> Escalate
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem className="gap-2">
                                  <CheckCircle2 className="h-4 w-4" /> Mark resolved
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
                  {filtered.length === 0
                    ? "0 results"
                    : `Showing ${(page - 1) * PAGE_SIZE + 1}–${Math.min(page * PAGE_SIZE, filtered.length)} of ${filtered.length}`}
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
                  {Array.from({ length: Math.max(totalPages, 1) }, (_, i) => i + 1).map((p) => (
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
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
