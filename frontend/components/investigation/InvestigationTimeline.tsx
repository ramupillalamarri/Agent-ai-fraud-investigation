import React from "react";
import { TimelineHeader } from "./TimelineHeader";
import { TimelineEvent, TimelineEventData } from "./TimelineEvent";
import { AlertCircle } from "lucide-react";

interface InvestigationTimelineProps {
  events: TimelineEventData[];
  loading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export function InvestigationTimeline({
  events,
  loading = false,
  error = null,
  onRefresh,
  isRefreshing = false
}: InvestigationTimelineProps) {
  
  // 1. Loading Skeleton State
  if (loading) {
    return (
      <div className="space-y-6" aria-busy="true">
        <div className="h-10 bg-slate-50 rounded animate-pulse w-1/3 mb-4" />
        <div className="space-y-6 relative pl-4">
          <div className="absolute top-4 left-4 h-[calc(100%-2rem)] w-0.5 bg-slate-100" />
          {[1, 2, 3].map((n) => (
            <div key={n} className="flex gap-4 relative animate-pulse">
              <div className="h-8 w-8 rounded-full bg-slate-100 border border-slate-200" />
              <div className="flex-1 bg-slate-50 border border-slate-100 rounded-xl p-4 h-24" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  // 2. Error State
  if (error) {
    return (
      <div className="flex items-center space-x-3 p-5 border border-red-100 bg-red-50/30 text-red-700 rounded-xl">
        <AlertCircle className="w-5 h-5 flex-shrink-0" />
        <div className="text-xs">
          <h5 className="font-bold">Failed to load audit timeline</h5>
          <p className="text-red-500/90">{error}</p>
        </div>
      </div>
    );
  }

  // 3. Empty State
  if (!events || events.length === 0) {
    return (
      <div className="text-center py-10 border border-dashed border-slate-200 rounded-xl bg-slate-50/50">
        <p className="text-xs text-slate-400 italic">No framework trace events found in database registry.</p>
      </div>
    );
  }

  // 4. Chronological Sorting
  const sortedEvents = [...events].sort((a, b) => {
    return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
  });

  return (
    <div className="space-y-6" aria-label="Investigation Execution Audit Timeline">
      <TimelineHeader 
        totalEvents={sortedEvents.length} 
        onRefresh={onRefresh} 
        isRefreshing={isRefreshing} 
      />
      
      <div className="relative pl-2 mt-4" role="list">
        {sortedEvents.map((event, index) => (
          <TimelineEvent 
            key={event.id || index} 
            event={event} 
            isLast={index === sortedEvents.length - 1} 
          />
        ))}
      </div>
    </div>
  );
}
export default InvestigationTimeline;
