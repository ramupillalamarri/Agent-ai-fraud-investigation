import React, { useState } from "react";
import {
  Play,
  TrendingUp,
  User,
  Monitor,
  Network,
  Store,
  BookOpen,
  Cpu,
  Database,
  CheckCircle2,
  AlertOctagon,
  ChevronDown,
  ChevronUp,
  Clock
} from "lucide-react";

export interface TimelineEventData {
  id: string;
  timestamp: string;
  event_type: string;
  event_description: string;
  agent_name?: string;
  status?: string;
  metadata?: any;
}

interface TimelineEventProps {
  event: TimelineEventData;
  isLast: boolean;
}

export function TimelineEvent({ event, isLast }: TimelineEventProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Derive Icons dynamically based on event types
  const getIcon = (type: string) => {
    const typeLower = type.toLowerCase();
    if (typeLower.includes("start")) return <Play className="w-4 h-4 text-emerald-600" />;
    if (typeLower.includes("predict")) return <TrendingUp className="w-4 h-4 text-blue-600" />;
    if (typeLower.includes("customer")) return <User className="w-4 h-4 text-indigo-600" />;
    if (typeLower.includes("device")) return <Monitor className="w-4 h-4 text-violet-600" />;
    if (typeLower.includes("network")) return <Network className="w-4 h-4 text-amber-600" />;
    if (typeLower.includes("merchant")) return <Store className="w-4 h-4 text-teal-600" />;
    if (typeLower.includes("knowledge") || typeLower.includes("rag")) return <BookOpen className="w-4 h-4 text-cyan-600" />;
    if (typeLower.includes("reason") || typeLower.includes("llm")) return <Cpu className="w-4 h-4 text-fuchsia-600" />;
    if (typeLower.includes("save") || typeLower.includes("db")) return <Database className="w-4 h-4 text-slate-600" />;
    if (typeLower.includes("complete") || typeLower.includes("finish")) return <CheckCircle2 className="w-4 h-4 text-emerald-600" />;
    return <AlertOctagon className="w-4 h-4 text-rose-600" />;
  };

  const getIconBg = (type: string) => {
    const typeLower = type.toLowerCase();
    if (typeLower.includes("start")) return "bg-emerald-50 border-emerald-200";
    if (typeLower.includes("predict")) return "bg-blue-50 border-blue-200";
    if (typeLower.includes("customer")) return "bg-indigo-50 border-indigo-200";
    if (typeLower.includes("device")) return "bg-violet-50 border-violet-200";
    if (typeLower.includes("network")) return "bg-amber-50 border-amber-200";
    if (typeLower.includes("merchant")) return "bg-teal-50 border-teal-200";
    if (typeLower.includes("knowledge") || typeLower.includes("rag")) return "bg-cyan-50 border-cyan-200";
    if (typeLower.includes("reason") || typeLower.includes("llm")) return "bg-fuchsia-50 border-fuchsia-200";
    if (typeLower.includes("save") || typeLower.includes("db")) return "bg-slate-50 border-slate-200";
    if (typeLower.includes("complete") || typeLower.includes("finish")) return "bg-emerald-50 border-emerald-200";
    return "bg-rose-50 border-rose-200";
  };

  // Format type name for display title
  const getEventTitle = (type: string) => {
    return type
      .replace(/_/g, " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };

  // Safe time formatting
  const formattedTime = (() => {
    try {
      const d = new Date(event.timestamp);
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
    } catch {
      return "00:00:00";
    }
  })();

  const rawMetadata = event.metadata || event.metadata === null ? event.metadata : (event as any).additional_metadata;
  const hasMetadata = rawMetadata && Object.keys(rawMetadata).length > 0;
  const duration = rawMetadata?.latency_ms || rawMetadata?.execution_time_ms;

  return (
    <div className="relative flex gap-4 pb-6 group" role="listitem">
      {/* Connector line */}
      {!isLast && (
        <span 
          className="absolute top-8 left-4 -ml-px h-[calc(100%-1.5rem)] w-0.5 bg-slate-100 group-hover:bg-indigo-100 transition-colors"
          aria-hidden="true" 
        />
      )}

      {/* Icon node wrapper */}
      <div className="relative">
        <span className={`flex h-8 w-8 items-center justify-center rounded-full border shadow-sm transition-transform group-hover:scale-110 duration-200 ${getIconBg(event.event_type)}`}>
          {getIcon(event.event_type)}
        </span>
      </div>

      {/* Content Card container */}
      <div className="flex-1 min-w-0 bg-white border border-slate-100 hover:border-slate-200/80 rounded-xl p-4 shadow-sm transition-all hover:shadow-md duration-200">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
          {/* Title and Badge layout */}
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="text-xs font-bold text-slate-800 tracking-tight">
              {getEventTitle(event.event_type)}
            </h4>
            
            {event.agent_name && (
              <span className="text-[9px] font-bold bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded border border-indigo-100">
                {event.agent_name}
              </span>
            )}

            {event.status && (
              <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${
                event.status === "SUCCESS"
                  ? "bg-emerald-50 text-emerald-700 border-emerald-100"
                  : event.status === "SKIPPED"
                  ? "bg-slate-50 text-slate-500 border-slate-200"
                  : "bg-red-50 text-red-700 border-red-100"
              }`}>
                {event.status}
              </span>
            )}
          </div>

          {/* Time & Duration layout */}
          <div className="flex items-center space-x-2 text-[10px] text-slate-400 font-mono self-end sm:self-auto">
            {duration !== undefined && (
              <span className="flex items-center bg-slate-50 px-1.5 py-0.5 rounded text-slate-500 border border-slate-100">
                <Clock className="w-3 h-3 mr-1" />
                {duration}ms
              </span>
            )}
            <span>{formattedTime}</span>
          </div>
        </div>

        {/* Description body */}
        <p className="text-xs text-slate-500 leading-relaxed break-words">
          {event.event_description}
        </p>

        {/* Metadata Details section */}
        {hasMetadata && (
          <div className="mt-3 border-t border-slate-50 pt-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center gap-1 text-[10px] font-bold text-slate-400 hover:text-indigo-600 transition-colors"
              aria-expanded={isExpanded}
            >
              {isExpanded ? (
                <>
                  <ChevronUp className="w-3 h-3" /> Hide parameters trace
                </>
              ) : (
                <>
                  <ChevronDown className="w-3 h-3" /> View parameters trace
                </>
              )}
            </button>

            {isExpanded && (
              <pre className="mt-2 bg-slate-900 text-[10px] text-slate-300 font-mono rounded-lg p-3 overflow-x-auto max-h-48 border border-slate-800 shadow-inner select-all">
                <code>{JSON.stringify(rawMetadata, null, 2)}</code>
              </pre>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
