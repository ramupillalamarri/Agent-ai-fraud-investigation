"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import {
  Search,
  Menu,
  ChevronRight,
  Settings,
  User,
  LogOut,
  HelpCircle,
  Moon,
  Keyboard,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuShortcut,
} from "@/components/ui/dropdown-menu";
import { NotificationPanel } from "@/components/shared/notification-panel";

const ROUTE_LABELS: Record<string, string> = {
  dashboard: "Dashboard",
  transactions: "Transactions",
  investigations: "Investigations",
  "risk-monitor": "Risk Monitor",
  alerts: "Alerts",
  agents: "AI Agents",
  analytics: "Analytics",
  "data-sources": "Data Sources",
  users: "Users",
  settings: "Settings",
};

function useBreadcrumbs() {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);
  return segments.map((seg, i) => ({
    label: ROUTE_LABELS[seg] ?? seg.charAt(0).toUpperCase() + seg.slice(1),
    href: "/" + segments.slice(0, i + 1).join("/"),
    isLast: i === segments.length - 1,
  }));
}

interface TopNavProps {
  sidebarCollapsed?: boolean;
  onToggleSidebar: () => void;
}

export function TopNav({ onToggleSidebar }: TopNavProps) {
  const breadcrumbs = useBreadcrumbs();

  return (
    <header className="flex h-14 shrink-0 items-center gap-4 border-b border-border bg-background/95 px-4 backdrop-blur-sm lg:px-6">
      {/* Mobile sidebar toggle */}
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8 shrink-0 lg:hidden"
        onClick={onToggleSidebar}
        aria-label="Toggle sidebar"
      >
        <Menu className="h-4 w-4" />
      </Button>

      {/* Breadcrumbs */}
      <nav aria-label="Breadcrumb" className="hidden items-center gap-1 text-sm lg:flex">
        <Link href="/dashboard" className="text-muted-foreground transition-colors hover:text-foreground">
          Home
        </Link>
        {breadcrumbs.map((crumb) => (
          <span key={crumb.href} className="flex items-center gap-1">
            <ChevronRight className="h-3.5 w-3.5 shrink-0 text-muted-foreground/40" />
            {crumb.isLast ? (
              <span className="font-medium text-foreground">{crumb.label}</span>
            ) : (
              <Link
                href={crumb.href}
                className="text-muted-foreground transition-colors hover:text-foreground"
              >
                {crumb.label}
              </Link>
            )}
          </span>
        ))}
      </nav>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Search */}
      <div className="relative hidden w-60 xl:block">
        <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Search investigations…"
          className="h-8 border-border bg-muted/40 pl-8 text-sm placeholder:text-muted-foreground/60 focus-visible:bg-background"
        />
        <kbd className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 rounded border border-border bg-muted px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground">
          ⌘K
        </kbd>
      </div>

      {/* Notifications */}
      <NotificationPanel />

      <Separator orientation="vertical" className="h-5" />

      {/* User menu */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            className="h-8 gap-2 rounded-lg px-2 pr-1 hover:bg-accent"
            aria-label="User menu"
          >
            <div className="hidden flex-col items-end text-right sm:flex">
              <span className="text-xs font-medium leading-none">Alex Morgan</span>
              <span className="text-[10px] leading-none text-muted-foreground">Lead Investigator</span>
            </div>
            <Avatar className="h-7 w-7">
              <AvatarImage src={undefined} alt="Alex Morgan" />
              <AvatarFallback className="bg-primary/20 text-xs font-semibold text-primary">
                AM
              </AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-52" sideOffset={8}>
          <DropdownMenuLabel className="pb-1">
            <div className="flex flex-col">
              <span className="text-sm font-semibold">Alex Morgan</span>
              <span className="text-xs font-normal text-muted-foreground">alex.morgan@company.com</span>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem asChild>
            <Link href="/settings/profile" className="flex cursor-pointer items-center">
              <User className="mr-2 h-4 w-4" />
              Profile
              <DropdownMenuShortcut>⌘P</DropdownMenuShortcut>
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem asChild>
            <Link href="/settings" className="flex cursor-pointer items-center">
              <Settings className="mr-2 h-4 w-4" />
              Settings
              <DropdownMenuShortcut>⌘,</DropdownMenuShortcut>
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem>
            <Keyboard className="mr-2 h-4 w-4" />
            Keyboard shortcuts
            <DropdownMenuShortcut>?</DropdownMenuShortcut>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem>
            <Moon className="mr-2 h-4 w-4" />
            Appearance
          </DropdownMenuItem>
          <DropdownMenuItem>
            <HelpCircle className="mr-2 h-4 w-4" />
            Help & Support
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem className="text-destructive focus:text-destructive" asChild>
            <Link href="/login" className="flex cursor-pointer items-center">
              <LogOut className="mr-2 h-4 w-4" />
              Sign out
              <DropdownMenuShortcut>⇧⌘Q</DropdownMenuShortcut>
            </Link>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
