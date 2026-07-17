"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  AlertTriangle,
  Bell,
  Search,
  Filter,
  Eye,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useInvestigations } from "@/hooks/useInvestigations";
import { LoadingSpinner, ErrorCard, StatusBadge, RiskBadge } from "@/components/shared/feedback";

const PAGE_SIZE = 8;

export default function AlertsPage() {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  // Load high-risk investigations (risk score >= 75 or priority is HIGH)
  const {
    investigations,
    total,
    loading,
    error,
    updateFilters,
    refetch,
  } = useInvestigations({
    page,
    page_size: PAGE_SIZE,
    priority: "HIGH"
  });

  useEffect(() => {
    updateFilters({
      page,
      priority: "HIGH"
    });
  }, [page]);

  const handleSearchChange = (val: string) => {
    setSearch(val);
    setPage(1);
  };

  const filteredAlerts = investigations.filter((inv) => {
    if (!search) return true;
    return (
      inv.id.toLowerCase().includes(search.toLowerCase()) ||
      inv.transaction_id.toLowerCase().includes(search.toLowerCase())
    );
  });

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-800">Risk Alerts</h1>
          <p className="mt-1 text-sm text-slate-500">
            Real-time critical events and potential account takeovers
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            Refresh List
          </Button>
          <Button size="sm" onClick={() => router.push("/dashboard")}>
            Dashboard
          </Button>
        </div>
      </div>

      {/* Quick Search */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-100 shadow-sm">
        <div className="flex flex-1 items-center gap-2 max-w-md">
          <div className="relative w-full">
            <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
            <Input
              placeholder="Search by Alert ID or TX ID..."
              value={search}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="h-9 pl-8 text-xs bg-slate-50 border-0 focus-visible:ring-1 focus-visible:ring-indigo-500"
            />
          </div>
        </div>
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 bg-slate-50 px-2 py-1.5 rounded-lg border border-slate-100">
          <Filter className="h-3.5 w-3.5" />
          <span>{filteredAlerts.length} active risk alerts</span>
        </div>
      </div>

      {/* Main Alert Grid */}
      <div className="space-y-4">
        {loading ? (
          <div className="py-24">
            <LoadingSpinner message="Scanning active pipelines for alerts..." />
          </div>
        ) : error ? (
          <div className="py-12 px-6">
            <ErrorCard message={error} onRetry={refetch} />
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="py-20 text-center bg-white border border-slate-200 border-dashed rounded-xl">
            <p className="text-sm font-semibold text-slate-500 italic">No critical high-risk alerts active.</p>
          </div>
        ) : (
          filteredAlerts.map((inv) => {
            const tx_data = inv.additional_metadata || {};
            return (
              <div 
                key={inv.id} 
                className="p-5 bg-white border border-l-4 border-l-red-500 border-slate-100 rounded-r-xl shadow-sm hover:shadow transition-shadow flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-extrabold border bg-red-50 text-red-700 border-red-200 animate-pulse">
                      CRITICAL RISK
                    </span>
                    <span className="text-xs font-mono text-slate-400">ID: {inv.id.substring(0, 8)}...</span>
                    <span className="text-[10px] text-slate-400">
                      {new Date(inv.created_at).toLocaleString()}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-slate-800">
                    High Risk Detection on Transaction {inv.transaction_id}
                  </h4>
                  <p className="text-xs text-slate-500 leading-relaxed max-w-2xl">
                    Fraud probability evaluated by machine learning: <strong>{(inv.fraud_probability * 100).toFixed(1)}%</strong>. 
                    Assoc customer ID: <strong>{tx_data.customer_id || "unknown"}</strong> | IP: <strong>{tx_data.ip_address || "unknown"}</strong> | Device: <strong>{tx_data.device_id || "unknown"}</strong>.
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <RiskBadge score={inv.risk_score} />
                  <StatusBadge status={inv.status} />
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="h-8 gap-1.5 text-xs text-indigo-600 hover:text-indigo-700"
                    onClick={() => router.push(`/investigations/${inv.id}`)}
                  >
                    <Eye className="h-4 w-4" /> View dossier
                  </Button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Pagination controls */}
      {!loading && !error && total > 0 && (
        <div className="flex items-center justify-between border-t border-slate-100 px-6 py-4 bg-slate-50/50">
          <p className="text-xs text-slate-500 font-medium">
            Showing {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, total)} of {total} alerts
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
    </div>
  );
}
