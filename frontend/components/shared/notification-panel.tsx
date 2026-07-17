"use client";

import * as React from "react";
import {
  Bell,
  X,
  AlertTriangle,
  CheckCircle2,
  Info,
  ShieldAlert,
  ExternalLink,
  BellOff,
  Cpu,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

type NotifType = "critical" | "warning" | "success" | "info";

interface Notification {
  id: number;
  type: NotifType;
  title: string;
  message: string;
  time: string;
  read: boolean;
}

const INITIAL_NOTIFICATIONS: Notification[] = [
  {
    id: 1,
    type: "critical",
    title: "Critical Fraud Alert",
    message: "Transaction TXN-20241 flagged with risk score 94 — card skimming pattern detected across 12 accounts.",
    time: "2 min ago",
    read: false,
  },
  {
    id: 2,
    type: "warning",
    title: "Escalation Required",
    message: "Investigation INV-2024-047 has been pending review for 48+ hours with no assigned investigator.",
    time: "15 min ago",
    read: false,
  },
  {
    id: 3,
    type: "info",
    title: "AI Agent Completed Analysis",
    message: "FraudDetect Agent v2.1 finished processing 1,240 transactions. 38 flagged for manual review.",
    time: "1 hr ago",
    read: false,
  },
  {
    id: 4,
    type: "success",
    title: "Case Resolved",
    message: "Investigation INV-2024-038 closed by Sarah Chen. $84,200 in fraudulent charges recovered.",
    time: "3 hr ago",
    read: true,
  },
  {
    id: 5,
    type: "info",
    title: "New Data Source Connected",
    message: "Stripe Radar transaction feed successfully connected and streaming live data.",
    time: "1 day ago",
    read: true,
  },
  {
    id: 6,
    type: "warning",
    title: "Model Confidence Drop",
    message: "AI model confidence score dropped below threshold (78%) for Account Takeover detection. Review recommended.",
    time: "1 day ago",
    read: true,
  },
];

const typeConfig: Record<NotifType, { icon: React.ElementType; iconClass: string; bg: string }> = {
  critical: { icon: ShieldAlert, iconClass: "text-red-400", bg: "bg-red-500/15" },
  warning: { icon: AlertTriangle, iconClass: "text-amber-400", bg: "bg-amber-500/15" },
  success: { icon: CheckCircle2, iconClass: "text-emerald-400", bg: "bg-emerald-500/15" },
  info: { icon: Info, iconClass: "text-blue-400", bg: "bg-blue-500/15" },
};

export function NotificationPanel() {
  const [open, setOpen] = React.useState(false);
  const [notifications, setNotifications] = React.useState(INITIAL_NOTIFICATIONS);
  const unreadCount = notifications.filter((n) => !n.read).length;

  function markAllRead() {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }

  function markRead(id: number) {
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
  }

  function dismiss(id: number) {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }

  return (
    <>
      {/* Bell trigger */}
      <Button
        variant="ghost"
        size="icon"
        className="relative h-8 w-8"
        aria-label="Notifications"
        onClick={() => setOpen(true)}
      >
        <Bell className="h-4 w-4" />
        {unreadCount > 0 && (
          <Badge className="absolute -right-0.5 -top-0.5 h-3.5 min-w-3.5 rounded-full px-0.5 text-[9px] font-bold">
            {unreadCount}
          </Badge>
        )}
      </Button>

      {/* Backdrop */}
      <div
        className={cn(
          "fixed inset-0 z-40 bg-black/50 backdrop-blur-sm transition-opacity duration-300",
          open ? "opacity-100" : "pointer-events-none opacity-0",
        )}
        onClick={() => setOpen(false)}
      />

      {/* Panel */}
      <div
        className={cn(
          "fixed inset-y-0 right-0 z-50 flex w-96 flex-col border-l border-border bg-background shadow-2xl",
          "transition-transform duration-300 ease-in-out",
          open ? "translate-x-0" : "translate-x-full",
        )}
      >
        {/* Header */}
        <div className="flex h-14 shrink-0 items-center justify-between border-b border-border px-4">
          <div className="flex items-center gap-2">
            <Cpu className="h-4 w-4 text-muted-foreground" />
            <span className="font-semibold">Notifications</span>
            {unreadCount > 0 && (
              <Badge variant="secondary" className="text-[10px]">
                {unreadCount} new
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-1">
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                className="h-7 px-2 text-xs text-muted-foreground"
                onClick={markAllRead}
              >
                Mark all read
              </Button>
            )}
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setOpen(false)}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto">
          {notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
                <BellOff className="h-5 w-5 text-muted-foreground" />
              </div>
              <p className="mt-3 text-sm font-medium">All caught up</p>
              <p className="mt-1 text-xs text-muted-foreground">No notifications right now.</p>
            </div>
          ) : (
            <div className="divide-y divide-border/60">
              {notifications.map((n) => {
                const { icon: Icon, iconClass, bg } = typeConfig[n.type];
                return (
                  <div
                    key={n.id}
                    className={cn(
                      "group relative flex gap-3 px-4 py-3.5 transition-colors hover:bg-muted/20",
                      !n.read && "bg-primary/5",
                    )}
                    onClick={() => markRead(n.id)}
                  >
                    {!n.read && (
                      <span className="absolute left-2 top-1/2 h-1.5 w-1.5 -translate-y-1/2 rounded-full bg-primary" />
                    )}
                    <div
                      className={cn(
                        "mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                        bg,
                      )}
                    >
                      <Icon className={cn("h-4 w-4", iconClass)} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className={cn("text-sm font-medium", !n.read ? "text-foreground" : "text-muted-foreground")}>
                        {n.title}
                      </p>
                      <p className="mt-0.5 text-xs leading-relaxed text-muted-foreground line-clamp-2">{n.message}</p>
                      <p className="mt-1 text-[10px] text-muted-foreground/60">{n.time}</p>
                    </div>
                    <button
                      type="button"
                      className="mt-1 hidden h-5 w-5 shrink-0 items-center justify-center rounded text-muted-foreground hover:text-foreground group-hover:flex"
                      onClick={(e) => {
                        e.stopPropagation();
                        dismiss(n.id);
                      }}
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="shrink-0 border-t border-border p-3">
          <Button variant="outline" size="sm" className="w-full gap-1.5 text-xs">
            View all notifications
            <ExternalLink className="h-3 w-3" />
          </Button>
        </div>
      </div>
    </>
  );
}

export function NotificationSeparator() {
  return <Separator orientation="vertical" className="h-5" />;
}
