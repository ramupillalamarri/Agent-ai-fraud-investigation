import React from "react";

export interface TimelineEvent {
  id: string;
  event_type: string;
  event_description: string;
  agent_name?: string;
  timestamp: string;
  additional_metadata?: any;
}

export function Timeline({ events }: { events: TimelineEvent[] }) {
  if (!events || events.length === 0) {
    return <p className="text-xs text-slate-400 italic">No timeline events logged.</p>;
  }

  return (
    <div className="flow-root">
      <ul role="list" className="-mb-8">
        {events.map((event, eventIdx) => (
          <li key={event.id}>
            <div className="relative pb-8">
              {eventIdx !== events.length - 1 ? (
                <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-slate-200" aria-hidden="true" />
              ) : null}
              <div className="relative flex space-x-3">
                <div>
                  <span className="h-8 w-8 rounded-full bg-slate-100 flex items-center justify-center ring-8 ring-white text-slate-500">
                    <span className="text-[10px] font-bold">{eventIdx + 1}</span>
                  </span>
                </div>
                <div className="flex-1 min-w-0 pt-1.5 flex justify-between space-x-4">
                  <div>
                    <p className="text-xs font-bold text-slate-800">
                      {event.event_type.replace(/_/g, " ")}{" "}
                      {event.agent_name && (
                        <span className="text-[10px] font-medium bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded ml-1">
                          {event.agent_name}
                        </span>
                      )}
                    </p>
                    <p className="text-xs text-slate-500 mt-0.5">{event.event_description}</p>
                  </div>
                  <div className="text-right text-[10px] whitespace-nowrap text-slate-400">
                    <time dateTime={event.timestamp}>
                      {new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </time>
                  </div>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
