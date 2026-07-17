"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  CreditCard,
  AlertTriangle,
  Search,
  Filter,
  Eye,
  FileSearch,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useTransactions } from "@/hooks/useTransactions";
import { LoadingSpinner, ErrorCard, StatusBadge, RiskBadge } from "@/components/shared/feedback";

const PAGE_SIZE = 10;

export default function TransactionsPage() {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [page, setPage] = useState(1);

  const {
    transactions,
    total,
    loading,
    error,
    updateFilters,
    refetch,
  } = useTransactions({
    page,
    page_size: PAGE_SIZE,
    priority: priorityFilter !== "all" ? priorityFilter.toUpperCase() : undefined,
  });

  useEffect(() => {
    updateFilters({
      page,
      priority: priorityFilter !== "all" ? priorityFilter.toUpperCase() : undefined,
    });
  }, [page, priorityFilter]);

  const handleSearchChange = (val: string) => {
    setSearch(val);
    setPage(1);
  };

  const handlePriorityFilterChange = (val: string) => {
    setPriorityFilter(val);
    setPage(1);
  };

  const filteredTransactions = transactions.filter((tx) => {
    if (!search) return true;
    return (
      tx.id.toLowerCase().includes(search.toLowerCase()) ||
      tx.customer_id.toLowerCase().includes(search.toLowerCase())
    );
  });

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-800">Transactions</h1>
          <p className="mt-1 text-sm text-slate-500">Live payment validation audits and risk parameters</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-1.5" onClick={() => refetch()}>
            Refresh Live
          </Button>
          <Button size="sm" onClick={() => router.push("/dashboard")}>
            Dashboard
          </Button>
        </div>
      </div>

      {/* Filters Strip */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-100 shadow-sm">
        <div className="flex flex-1 items-center gap-2 max-w-md">
          <div className="relative w-full">
            <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
            <Input
              placeholder="Search by Transaction ID or Customer..."
              value={search}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="h-9 pl-8 text-xs bg-slate-50 border-0 focus-visible:ring-1 focus-visible:ring-indigo-500"
            />
          </div>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={priorityFilter}
            onChange={(e) => handlePriorityFilterChange(e.target.value)}
            className="h-9 rounded-md border border-slate-200 bg-white px-2.5 text-xs font-semibold text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="all">All Priorities</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="low">Low Risk</option>
          </select>
          <div className="flex items-center gap-1 text-xs font-semibold text-slate-500 bg-slate-50 px-2 py-1.5 rounded-lg border border-slate-100">
            <Filter className="h-3.5 w-3.5" />
            <span>{filteredTransactions.length} items</span>
          </div>
        </div>
      </div>

      {/* Main Table */}
      <Card className="overflow-hidden bg-white shadow-sm border border-slate-100 rounded-xl">
        {loading ? (
          <div className="py-24">
            <LoadingSpinner message="Querying transactions database..." />
          </div>
        ) : error ? (
          <div className="py-12 px-6">
            <ErrorCard message={error} onRetry={refetch} />
          </div>
        ) : filteredTransactions.length === 0 ? (
          <div className="py-20 text-center">
            <p className="text-sm font-semibold text-slate-500 italic">No transactions found matching criteria.</p>
          </div>
        ) : (
          <Table>
            <TableHeader className="bg-slate-50">
              <TableRow>
                <TableHead className="font-bold text-slate-700">Transaction ID</TableHead>
                <TableHead className="font-bold text-slate-700">Customer ID</TableHead>
                <TableHead className="w-28 font-bold text-slate-700">Amount</TableHead>
                <TableHead className="w-32 font-bold text-slate-700">Date/Time</TableHead>
                <TableHead className="w-32 font-bold text-slate-700">Risk Score</TableHead>
                <TableHead className="w-32 font-bold text-slate-700">Status</TableHead>
                <TableHead className="w-24 text-right" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredTransactions.map((tx) => (
                <TableRow key={tx.id} className="hover:bg-slate-50/50 transition-colors">
                  <TableCell className="font-mono text-xs font-bold text-slate-800">
                    {tx.id}
                  </TableCell>
                  <TableCell className="font-medium text-slate-700">
                    {tx.customer_id}
                  </TableCell>
                  <TableCell className="font-bold text-slate-900">
                    ${(tx.amount || 0.0).toLocaleString()}
                  </TableCell>
                  <TableCell className="text-xs text-slate-500">
                    {new Date(tx.timestamp).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                  </TableCell>
                  <TableCell>
                    <RiskBadge score={tx.risk_score} />
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={tx.status} />
                  </TableCell>
                  <TableCell className="text-right">
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      onClick={() => router.push(`/investigations/${tx.investigation_id}`)}
                      className="h-8 w-8 hover:bg-slate-100 hover:text-indigo-600"
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}

        {/* Pagination controls */}
        {!loading && !error && total > 0 && (
          <div className="flex items-center justify-between border-t border-slate-100 px-6 py-4 bg-slate-50/50">
            <p className="text-xs text-slate-500 font-medium">
              Showing {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, total)} of {total} transactions
            </p>
            <div className="flex items-center gap-1">
              <Button
                variant="outline"
                size="sm"
                className="h-8 px-3 text-xs"
                disabled={page === 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </Button>
              <span className="text-xs font-semibold text-slate-700 px-3">
                Page {page} of {Math.max(totalPages, 1)}
              </span>
              <Button
                variant="outline"
                size="sm"
                className="h-8 px-3 text-xs"
                disabled={page === totalPages || totalPages === 0}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
