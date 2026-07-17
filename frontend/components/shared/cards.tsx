import React from "react";

export interface EvidenceItem {
  id?: string;
  type: string;
  severity: string;
  confidence: number;
  description: string;
  source: string;
}

export interface RecommendationItem {
  id?: string;
  recommendation: string;
  priority: string;
  generated_by: string;
  status: string;
}

export function EvidenceCard({ evidence }: { evidence: EvidenceItem }) {
  let severityColor = "bg-slate-100 text-slate-700 border-slate-200";
  if (evidence.severity?.toUpperCase() === "HIGH" || evidence.severity?.toUpperCase() === "CRITICAL") {
    severityColor = "bg-red-50 text-red-700 border-red-200";
  } else if (evidence.severity?.toUpperCase() === "MEDIUM") {
    severityColor = "bg-amber-50 text-amber-700 border-amber-200";
  }

  return (
    <div className="p-4 bg-white border border-slate-100 rounded-xl shadow-sm hover:shadow transition-shadow space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold text-slate-800">{evidence.type.replace(/([A-Z])/g, ' $1').trim()}</span>
        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${severityColor}`}>
          {evidence.severity}
        </span>
      </div>
      <p className="text-xs text-slate-500">{evidence.description}</p>
      <div className="flex items-center justify-between pt-1 border-t border-slate-50 text-[10px] text-slate-400">
        <span>Source: <strong className="text-slate-600">{evidence.source}</strong></span>
        <span>Confidence: <strong className="text-slate-600">{Math.round(evidence.confidence * 100)}%</strong></span>
      </div>
    </div>
  );
}

export function RecommendationCard({ recommendation }: { recommendation: RecommendationItem }) {
  let priorityColor = "text-slate-500";
  if (recommendation.priority?.toUpperCase() === "HIGH") {
    priorityColor = "text-red-600 font-bold";
  } else if (recommendation.priority?.toUpperCase() === "MEDIUM") {
    priorityColor = "text-amber-600 font-semibold";
  }

  return (
    <div className="p-4 bg-indigo-50/30 border border-indigo-50/50 rounded-xl flex items-start space-x-3">
      <div className="p-1.5 bg-indigo-100 text-indigo-700 rounded-lg mt-0.5">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      </div>
      <div className="flex-1 space-y-1">
        <p className="text-xs font-bold text-indigo-950">{recommendation.recommendation}</p>
        <div className="flex items-center justify-between text-[10px] text-indigo-700">
          <span>Priority: <strong className={priorityColor}>{recommendation.priority}</strong></span>
          <span>By: <strong>{recommendation.generated_by}</strong></span>
        </div>
      </div>
    </div>
  );
}
