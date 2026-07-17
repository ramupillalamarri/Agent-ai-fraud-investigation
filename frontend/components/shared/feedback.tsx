import React from "react";

export function LoadingSpinner({ message = "Loading data..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      <p className="text-xs font-semibold text-slate-500">{message}</p>
    </div>
  );
}

export function EmptyState({ 
  title = "No records found", 
  description = "There are no entries available matching the current search parameters." 
}: { 
  title?: string; 
  description?: string; 
}) {
  return (
    <div className="flex flex-col items-center justify-center p-12 border border-dashed border-slate-200 rounded-xl text-center bg-white shadow-sm">
      <div className="p-3 bg-slate-50 rounded-full text-slate-400 mb-4">
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0a2 2 0 01-2 2H6a2 2 0 01-2-2m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5" />
        </svg>
      </div>
      <h3 className="text-sm font-bold text-slate-800 mb-1">{title}</h3>
      <p className="text-xs text-slate-500 max-w-sm">{description}</p>
    </div>
  );
}

export function ErrorCard({ 
  message = "An unexpected server error occurred. Please try again.", 
  onRetry 
}: { 
  message?: string; 
  onRetry?: () => void; 
}) {
  return (
    <div className="p-6 bg-red-50 border border-red-100 rounded-xl flex flex-col items-center space-y-4">
      <div className="p-2 bg-red-100 text-red-600 rounded-full">
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <div className="text-center">
        <h4 className="text-sm font-bold text-red-800">Connection Error</h4>
        <p className="text-xs text-red-600 mt-1 max-w-md">{message}</p>
      </div>
      {onRetry && (
        <button 
          onClick={onRetry} 
          className="px-4 py-1.5 bg-red-600 hover:bg-red-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const normalized = status?.toUpperCase() || "PENDING";
  
  const config: Record<string, { bg: string; label: string }> = {
    PENDING: { bg: "bg-amber-50 text-amber-700 border-amber-200", label: "Pending" },
    RUNNING: { bg: "bg-blue-50 text-blue-700 border-blue-200", label: "Running" },
    COMPLETED: { bg: "bg-emerald-50 text-emerald-700 border-emerald-200", label: "Completed" },
    ARCHIVED: { bg: "bg-slate-50 text-slate-700 border-slate-200", label: "Archived" },
    CLOSED: { bg: "bg-purple-50 text-purple-700 border-purple-200", label: "Closed" },
    DELETED: { bg: "bg-red-50 text-red-700 border-red-200", label: "Deleted" }
  };
  
  const current = config[normalized] || config.PENDING;
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${current.bg}`}>
      {current.label}
    </span>
  );
}

export function RiskBadge({ score }: { score: number }) {
  let bg = "bg-emerald-50 text-emerald-700 border-emerald-200";
  let label = "Low Risk";
  
  if (score >= 80) {
    bg = "bg-rose-50 text-rose-700 border-rose-200 animate-pulse";
    label = "Critical";
  } else if (score >= 50) {
    bg = "bg-amber-50 text-amber-700 border-amber-200";
    label = "Medium Risk";
  }
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${bg}`}>
      {label} ({score})
    </span>
  );
}
