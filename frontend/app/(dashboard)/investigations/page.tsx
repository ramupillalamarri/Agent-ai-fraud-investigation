"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Eye,
  Trash,
  X,
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
import { useInvestigations } from "@/hooks/useInvestigations";
import { LoadingSpinner, ErrorCard, StatusBadge, RiskBadge } from "@/components/shared/feedback";
import { investigationApi } from "@/lib/api/investigation";
import { clearApiCache } from "@/lib/api-manager";

const PAGE_SIZE = 8;

export default function InvestigationsPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState("all");
  const [search, setSearch] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [page, setPage] = useState(1);

  // New Investigation Modal States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    transaction_id: "",
    customer_id: "",
    amount: "",
    category: "Online Retail",
    merchant: "Store Front",
    ip_address: "127.0.0.1",
    device_id: "",
    payment_instrument: "Credit Card",
  });

  const {
    investigations,
    total,
    loading,
    error,
    params,
    updateFilters,
    refetch,
  } = useInvestigations({
    page,
    page_size: PAGE_SIZE,
    status: activeTab !== "all" ? activeTab.toUpperCase() : undefined,
    priority: priorityFilter !== "all" ? priorityFilter.toUpperCase() : undefined,
  });

  // Keep filters in sync
  useEffect(() => {
    updateFilters({
      page,
      status: activeTab !== "all" ? activeTab.toUpperCase() : undefined,
      priority: priorityFilter !== "all" ? priorityFilter.toUpperCase() : undefined,
    });
  }, [page, activeTab, priorityFilter]);

  const handleSearchChange = (val: string) => {
    setSearch(val);
    setPage(1);
  };

  const handlePriorityFilterChange = (val: string) => {
    setPriorityFilter(val);
    setPage(1);
  };

  const handleTabChange = (val: string) => {
    setActiveTab(val);
    setPage(1);
  };

  // Local filtering for search (allows live character-by-character filter)
  const filteredInvestigations = investigations.filter((inv) => {
    if (!search) return true;
    return (
      inv.id.toLowerCase().includes(search.toLowerCase()) ||
      inv.transaction_id.toLowerCase().includes(search.toLowerCase()) ||
      inv.status.toLowerCase().includes(search.toLowerCase())
    );
  });

  const totalPages = Math.ceil(total / PAGE_SIZE);

  const handleDelete = async (id: string) => {
    if (confirm("Are you sure you want to soft delete this investigation dossier?")) {
      try {
        await investigationApi.delete(id);
        clearApiCache("inv-list");
        refetch();
      } catch (e: any) {
        alert(e.message || "Failed to delete investigation.");
      }
    }
  };

  const handleRunInvestigation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.transaction_id || !formData.customer_id || !formData.amount) {
      setFormError("Transaction ID, Customer ID, and Amount are required.");
      return;
    }
    
    setIsSubmitting(true);
    setFormError(null);
    try {
      const payload = {
        ...formData,
        amount: parseFloat(formData.amount),
        timestamp: new Date().toISOString()
      };
      
      const newDossier = await investigationApi.run(payload);
      setIsModalOpen(false);
      clearApiCache("inv-list");
      router.push(`/investigations/${newDossier.id}`);
    } catch (err: any) {
      setFormError(err.response?.data?.detail || err.message || "Failed to run investigation.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const tabs = [
    { value: "all", label: "All Cases" },
    { value: "pending", label: "Pending" },
    { value: "running", label: "Running" },
    { value: "completed", label: "Completed" },
    { value: "deleted", label: "Deleted" },
  ];

  return (
    <div className="space-y-6 animate-fade-in relative">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-800">Investigations</h1>
          <p className="mt-1 text-sm text-slate-500">
            {total} total records found in live PostgreSQL registry
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-1.5" onClick={() => refetch()}>
            Refresh Live
          </Button>
          <Button size="sm" className="gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold" onClick={() => setIsModalOpen(true)}>
            <Plus className="h-3.5 w-3.5" />
            New Investigation
          </Button>
        </div>
      </div>

      {/* Tabs & Filters */}
      <Tabs value={activeTab} onValueChange={handleTabChange}>
        <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-2 rounded-xl border border-slate-100 shadow-sm mb-4">
          <TabsList className="h-auto gap-0.5 bg-slate-50 p-1">
            {tabs.map((t) => (
              <TabsTrigger key={t.value} value={t.value} className="text-xs font-semibold px-3 py-1.5">
                {t.label}
              </TabsTrigger>
            ))}
          </TabsList>

          {/* Filters */}
          <div className="flex items-center gap-2">
            <div className="relative w-56">
              <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
              <Input
                placeholder="Search by ID or TX..."
                value={search}
                onChange={(e) => handleSearchChange(e.target.value)}
                className="h-8 pl-8 text-xs bg-slate-50 border-0"
              />
            </div>
            <select
              value={priorityFilter}
              onChange={(e) => handlePriorityFilterChange(e.target.value)}
              className="h-8 rounded-md border border-slate-200 bg-white px-2.5 text-xs text-slate-700 font-semibold focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="all">All Priorities</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 bg-slate-50 px-2 py-1.5 rounded-lg border border-slate-100">
              <Filter className="h-3 w-3" />
              {filteredInvestigations.length} on page
            </div>
          </div>
        </div>

        {/* Content Box */}
        {tabs.map((t) => (
          <TabsContent key={t.value} value={t.value} className="mt-0">
            <Card className="overflow-hidden bg-white shadow-sm border border-slate-100 rounded-xl">
              {loading ? (
                <div className="py-24">
                  <LoadingSpinner message="Fetching matching investigations..." />
                </div>
              ) : error ? (
                <div className="py-12 px-6">
                  <ErrorCard message={error} onRetry={refetch} />
                </div>
              ) : filteredInvestigations.length === 0 ? (
                <div className="py-20 text-center">
                  <p className="text-sm font-semibold text-slate-500 italic">No investigations match the selected filters.</p>
                </div>
              ) : (
                <Table>
                  <TableHeader className="bg-slate-50">
                    <TableRow>
                      <TableHead className="w-32 font-bold text-slate-700">Investigation ID</TableHead>
                      <TableHead className="font-bold text-slate-700">Transaction ID</TableHead>
                      <TableHead className="w-24 font-bold text-slate-700">Priority</TableHead>
                      <TableHead className="w-28 font-bold text-slate-700">Status</TableHead>
                      <TableHead className="w-24 font-bold text-slate-700">Risk Score</TableHead>
                      <TableHead className="w-24 font-bold text-slate-700">Fraud Prob</TableHead>
                      <TableHead className="w-32 font-bold text-slate-700">Created At</TableHead>
                      <TableHead className="w-12" />
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredInvestigations.map((inv) => (
                      <TableRow key={inv.id} className="hover:bg-slate-50/50 transition-colors">
                        <TableCell>
                          <span
                            className="cursor-pointer font-mono text-xs text-indigo-600 font-semibold hover:underline"
                            onClick={() => router.push(`/investigations/${inv.id}`)}
                          >
                            {inv.id.substring(0, 8)}...
                          </span>
                        </TableCell>
                        <TableCell>
                          <span
                            className="cursor-pointer font-semibold text-slate-800 hover:text-indigo-600 hover:underline"
                            onClick={() => router.push(`/investigations/${inv.id}`)}
                          >
                            {inv.transaction_id}
                          </span>
                        </TableCell>
                        <TableCell>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                            inv.priority === "HIGH" 
                              ? "bg-red-50 text-red-700 border-red-200" 
                              : inv.priority === "MEDIUM"
                              ? "bg-amber-50 text-amber-700 border-amber-200"
                              : "bg-emerald-50 text-emerald-700 border-emerald-200"
                          }`}>
                            {inv.priority}
                          </span>
                        </TableCell>
                        <TableCell>
                          <StatusBadge status={inv.status} />
                        </TableCell>
                        <TableCell>
                          <RiskBadge score={inv.risk_score} />
                        </TableCell>
                        <TableCell className="font-mono text-xs text-slate-700 font-semibold">
                          {(inv.fraud_probability * 100).toFixed(1)}%
                        </TableCell>
                        <TableCell className="text-xs text-slate-500">
                          {new Date(inv.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                        </TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon" className="h-7 w-7 text-slate-500 hover:bg-slate-100">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-44">
                              <DropdownMenuItem
                                className="gap-2 cursor-pointer font-semibold"
                                onClick={() => router.push(`/investigations/${inv.id}`)}
                              >
                                <Eye className="h-4 w-4" /> View dossier
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem 
                                className="gap-2 cursor-pointer text-rose-600 focus:bg-rose-50/50 font-semibold"
                                onClick={() => handleDelete(inv.id)}
                              >
                                <Trash className="h-4 w-4" /> Soft Delete
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
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
                    Showing {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, total)} of {total} results
                  </p>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-8 px-3 text-xs font-semibold"
                      disabled={page === 1}
                      onClick={() => setPage((p) => p - 1)}
                    >
                      Previous
                    </Button>
                    <span className="text-xs font-bold text-slate-700 px-3">
                      Page {page} of {Math.max(totalPages, 1)}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-8 px-3 text-xs font-semibold"
                      disabled={page === totalPages || totalPages === 0}
                      onClick={() => setPage((p) => p + 1)}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      {/* New Investigation Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm transition-opacity">
          <div className="relative w-full max-w-lg p-6 bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden transform transition-all space-y-4 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-slate-800">Launch Fraud Investigation</h3>
                <p className="text-xs text-slate-400">Trigger multi-agent retail fraud validation pipeline</p>
              </div>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {formError && (
              <div className="p-3 text-xs font-semibold text-rose-700 bg-rose-50 border border-rose-100 rounded-lg">
                {formError}
              </div>
            )}

            <form onSubmit={handleRunInvestigation} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Transaction ID</label>
                  <Input 
                    placeholder="e.g. TXN-84920" 
                    value={formData.transaction_id}
                    onChange={e => setFormData(p => ({ ...p, transaction_id: e.target.value }))}
                    className="h-9 text-xs"
                    required
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Customer ID</label>
                  <Input 
                    placeholder="e.g. CUST-3920" 
                    value={formData.customer_id}
                    onChange={e => setFormData(p => ({ ...p, customer_id: e.target.value }))}
                    className="h-9 text-xs"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Transaction Amount ($)</label>
                  <Input 
                    type="number"
                    step="0.01"
                    placeholder="e.g. 150.00" 
                    value={formData.amount}
                    onChange={e => setFormData(p => ({ ...p, amount: e.target.value }))}
                    className="h-9 text-xs"
                    required
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Category</label>
                  <select
                    value={formData.category}
                    onChange={e => setFormData(p => ({ ...p, category: e.target.value }))}
                    className="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-xs text-slate-700 font-semibold focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  >
                    <option value="Online Retail">Online Retail</option>
                    <option value="Electronics Store">Electronics Store</option>
                    <option value="Gift Cards">Gift Cards</option>
                    <option value="High-Risk Luxury">High-Risk Luxury</option>
                    <option value="Apparel & Clothing">Apparel & Clothing</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Merchant Name</label>
                  <Input 
                    placeholder="e.g. Amazon Inc" 
                    value={formData.merchant}
                    onChange={e => setFormData(p => ({ ...p, merchant: e.target.value }))}
                    className="h-9 text-xs"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">IP Address</label>
                  <Input 
                    placeholder="e.g. 74.125.19.14" 
                    value={formData.ip_address}
                    onChange={e => setFormData(p => ({ ...p, ip_address: e.target.value }))}
                    className="h-9 text-xs"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Device ID</label>
                  <Input 
                    placeholder="e.g. dev_mac_84928" 
                    value={formData.device_id}
                    onChange={e => setFormData(p => ({ ...p, device_id: e.target.value }))}
                    className="h-9 text-xs"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Payment Method</label>
                  <Input 
                    placeholder="e.g. VISA-4242" 
                    value={formData.payment_instrument}
                    onChange={e => setFormData(p => ({ ...p, payment_instrument: e.target.value }))}
                    className="h-9 text-xs"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <Button 
                  type="button" 
                  variant="outline" 
                  size="sm"
                  onClick={() => setIsModalOpen(false)}
                  disabled={isSubmitting}
                  className="font-bold text-xs"
                >
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  size="sm"
                  disabled={isSubmitting}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs gap-1.5"
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Auditing...
                    </>
                  ) : (
                    "Run Audit Dossier"
                  )}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
