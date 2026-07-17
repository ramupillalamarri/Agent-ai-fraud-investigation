"use client";

import { use, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  AlertTriangle,
  CheckCircle2,
  Circle,
  Activity,
  Cpu,
  ShieldAlert,
  Clock,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useInvestigation } from "@/hooks/useInvestigation";
import { LoadingSpinner, ErrorCard, StatusBadge, RiskBadge } from "@/components/shared/feedback";
import { EvidenceCard, RecommendationCard } from "@/components/shared/cards";
import { Timeline } from "@/components/shared/timeline";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function CaseDetailsPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const router = useRouter();
  const caseId = resolvedParams.id;

  const {
    investigation,
    report,
    timeline,
    loading,
    error,
    deleteDossier,
    refetch,
  } = useInvestigation(caseId);

  const [activeTab, setActiveTab] = useState<"overview" | "agent" | "history">("overview");

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <LoadingSpinner message="Querying live framework dossier registry..." />
      </div>
    );
  }

  if (error || !investigation) {
    return (
      <div className="flex h-[80vh] items-center justify-center p-6">
        <ErrorCard 
          message={error || `The case ID "${caseId}" could not be found in PostgreSQL.`} 
          onRetry={refetch} 
        />
      </div>
    );
  }

  // Extract variables
  const tx_data = investigation.additional_metadata || {};
  const agentResults = investigation.agent_results || [];
  const evidenceList = investigation.evidence || [];
  const recommendationsList = investigation.recommendations || [];

  const handleDeleteClick = async () => {
    if (confirm("Are you sure you want to soft delete this case dossier?")) {
      try {
        await deleteDossier();
        router.push("/investigations");
      } catch (e: any) {
        alert(e.message || "Failed to soft delete the dossier.");
      }
    }
  };

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      {/* Back button & title */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <Button onClick={() => router.push("/investigations")} variant="ghost" size="icon" className="h-8 w-8">
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <span className="font-mono text-xs text-slate-400">ID: {investigation.id.substring(0, 8)}...</span>
          <Separator orientation="vertical" className="h-4" />
          <h1 className="text-xl font-bold tracking-tight text-slate-800">
            Transaction: {investigation.transaction_id}
          </h1>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleDeleteClick} 
          className="text-red-600 hover:text-red-700 border-red-200 bg-red-50/50 hover:bg-red-50"
        >
          Soft Delete Dossier
        </Button>
      </div>

      {/* Grid container */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left Side: Detail Contents & Tabs */}
        <div className="lg:col-span-2 space-y-6">
          {/* Stats Bar */}
          <Card className="grid grid-cols-2 gap-4 p-5 sm:grid-cols-4 bg-white border border-slate-100 shadow-sm rounded-xl">
            <div>
              <p className="text-xs text-slate-500 font-medium">Transaction Amount</p>
              <p className="mt-1 text-2xl font-extrabold text-slate-800 tabular-nums">
                ${(tx_data.amount || 0.0).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium">Fraud Probability</p>
              <p className="mt-1 text-2xl font-extrabold text-indigo-600 tabular-nums">
                {(investigation.fraud_probability * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium">Risk Score Badge</p>
              <div className="mt-1.5">
                <RiskBadge score={investigation.risk_score} />
              </div>
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium">Resolution Status</p>
              <div className="mt-1">
                <StatusBadge status={investigation.status} />
              </div>
            </div>
          </Card>

          {/* Navigation Tabs */}
          <div className="flex border-b border-slate-200">
            {([
              { id: "overview", label: "Case Overview", icon: Activity },
              { id: "agent", label: `Agent Executions (${agentResults.length})`, icon: Cpu },
              { id: "history", label: `Audit Timeline (${timeline.length})`, icon: Clock },
            ] as const).map((t) => {
              const TabIcon = t.icon;
              return (
                <button
                  key={t.id}
                  onClick={() => setActiveTab(t.id)}
                  className={`flex items-center gap-2 border-b-2 px-4 py-2.5 text-xs font-bold transition-colors ${
                    activeTab === t.id
                      ? "border-indigo-600 text-indigo-600"
                      : "border-transparent text-slate-400 hover:text-slate-600"
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
              {/* Summary Description */}
              {report && (
                <Card className="p-6 space-y-3 bg-white border border-slate-100 shadow-sm rounded-xl">
                  <h3 className="text-sm font-bold text-slate-800">Executive Summary</h3>
                  <p className="text-xs text-slate-500 leading-relaxed">
                    {report.executive_summary}
                  </p>
                </Card>
              )}

              {/* Transaction Metadata Profile */}
              <Card className="p-6 space-y-4 bg-white border border-slate-100 shadow-sm rounded-xl">
                <h3 className="text-sm font-bold text-slate-800">Transaction Profile & Indicators</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-xs">
                  <div>
                    <span className="text-slate-400 block mb-1">Customer ID</span>
                    <strong className="text-slate-700 font-mono text-xs">{tx_data.customer_id || "N/A"}</strong>
                  </div>
                  <div>
                    <span className="text-slate-400 block mb-1">IP Address</span>
                    <strong className="text-slate-700 font-mono text-xs">{tx_data.ip_address || "N/A"}</strong>
                  </div>
                  <div>
                    <span className="text-slate-400 block mb-1">Device ID</span>
                    <strong className="text-slate-700 font-mono text-xs">{tx_data.device_id || "N/A"}</strong>
                  </div>
                  <div>
                    <span className="text-slate-400 block mb-1">Browser User Agent</span>
                    <strong className="text-slate-700 font-mono text-xs truncate max-w-[120px] block">
                      {tx_data.user_agent || "N/A"}
                    </strong>
                  </div>
                  <div>
                    <span className="text-slate-400 block mb-1">Demographics Country</span>
                    <strong className="text-slate-700 text-xs">{tx_data.location_country || "US"}</strong>
                  </div>
                  <div>
                    <span className="text-slate-400 block mb-1">Account Balance</span>
                    <strong className="text-slate-700 text-xs">${(tx_data.account_balance || 2000.0).toLocaleString()}</strong>
                  </div>
                </div>
              </Card>

              {/* Evidence & Findings */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Flagged Evidence Cards</h3>
                {evidenceList.length === 0 ? (
                  <p className="text-xs text-slate-400 italic">No evidence items flagged.</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {evidenceList.map((ev: any, idx: number) => (
                      <EvidenceCard key={idx} evidence={ev} />
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "agent" && (
            <div className="space-y-6">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Multi-Agent Orchestrator Executions</h3>
              {agentResults.length === 0 ? (
                <div className="p-6 text-center text-xs text-slate-400 italic bg-white border border-slate-100 rounded-xl">
                  No agents executed for this case.
                </div>
              ) : (
                <div className="space-y-4">
                  {agentResults.map((ar: any) => (
                    <Card key={ar.id} className="p-5 bg-white border border-slate-100 shadow-sm rounded-xl space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="p-2 bg-indigo-50 text-indigo-700 rounded-lg">
                            <Cpu className="w-5 h-5" />
                          </div>
                          <div>
                            <h4 className="text-sm font-bold text-slate-800">{ar.agent_name}</h4>
                            <span className="text-[10px] text-slate-400 block">ID: {ar.id}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                            ar.status === "SUCCESS" 
                              ? "bg-emerald-50 text-emerald-700 border-emerald-200" 
                              : "bg-red-50 text-red-700 border-red-200"
                          }`}>
                            {ar.status}
                          </span>
                          <span className="text-xs font-bold text-slate-600 bg-slate-50 px-2 py-0.5 rounded border border-slate-100">
                            Latency: {ar.execution_time_ms} ms
                          </span>
                        </div>
                      </div>

                      {/* Agent Reasoning Output details */}
                      <div className="bg-slate-50 p-4 rounded-lg border border-slate-100 text-xs">
                        <div className="flex items-center justify-between mb-2 pb-2 border-b border-slate-200">
                          <span className="font-bold text-slate-700">Agent Confidence Score</span>
                          <strong className="text-indigo-600 font-extrabold">{Math.round(ar.confidence_score * 100)}%</strong>
                        </div>
                        {ar.additional_metadata?.findings && ar.additional_metadata.findings.length > 0 && (
                          <div className="space-y-2">
                            <span className="font-bold text-slate-700 block mb-1">Agent Specific Findings:</span>
                            <ul className="list-disc pl-4 space-y-1 text-slate-500">
                              {ar.additional_metadata.findings.map((f: string, fIdx: number) => (
                                <li key={fIdx}>{f}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === "history" && (
            <Card className="p-6 bg-white border border-slate-100 shadow-sm rounded-xl space-y-4">
              <h4 className="text-sm font-bold text-slate-800">Framework Audit Trail</h4>
              <Timeline events={timeline} />
            </Card>
          )}
        </div>

        {/* Right Side: Recommendations & Actions */}
        <div className="space-y-6">
          <Card className="p-6 bg-white border border-slate-100 shadow-sm rounded-xl space-y-6">
            <h3 className="text-sm font-bold text-slate-800 uppercase tracking-widest">Mitigation Recommendations</h3>
            {recommendationsList.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No automated actions recommended.</p>
            ) : (
              <div className="space-y-4">
                {recommendationsList.map((rec: any, idx: number) => (
                  <RecommendationCard key={idx} recommendation={rec} />
                ))}
              </div>
            )}
            
            <Separator className="border-slate-100" />

            <div className="space-y-2.5">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Security Action Overrides</label>
              <Button 
                variant="outline" 
                className="w-full justify-start text-xs h-9 text-rose-600 hover:text-rose-700 hover:bg-rose-50/50 border-rose-200" 
                onClick={() => alert("Mitigation freeze override request sent to security team.")}
              >
                <ShieldAlert className="mr-2 h-4 w-4" /> Freeze Billing Profile
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
