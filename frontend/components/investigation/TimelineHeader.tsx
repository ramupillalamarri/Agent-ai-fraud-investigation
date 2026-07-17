import React from "react";
import { Activity, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface TimelineHeaderProps {
  totalEvents: number;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export function TimelineHeader({ totalEvents, onRefresh, isRefreshing }: TimelineHeaderProps) {
  return (
    <div className="flex items-center justify-between border-b border-slate-100 pb-4 flex-wrap gap-2">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-indigo-50 text-indigo-700 rounded-lg">
          <Activity className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-slate-800">Framework Audit Trace</h3>
          <p className="text-[10px] text-slate-400">Dynamic agent routing decisions and metrics</p>
        </div>
      </div>
      
      <div className="flex items-center space-x-2">
        <span className="text-[10px] font-bold bg-indigo-50 text-indigo-700 px-2.5 py-0.5 rounded-full">
          {totalEvents} events logged
        </span>
        {onRefresh && (
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={onRefresh} 
            disabled={isRefreshing} 
            className="h-8 w-8 text-slate-400 hover:text-indigo-600 hover:bg-slate-50"
            aria-label="Refresh timeline events"
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
          </Button>
        )}
      </div>
    </div>
  );
}
