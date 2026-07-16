"use client";

import { useState } from "react";
import {
  Users,
  Search,
  Filter,
  MoreHorizontal,
  Shield,
  UserPlus,
  Settings,
  Trash2,
  CheckCircle2,
  XCircle,
  Mail,
  Clock,
  RefreshCw,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

type UserRole = "admin" | "investigator" | "analyst" | "viewer";
type UserStatus = "active" | "inactive" | "pending";

interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  status: UserStatus;
  initials: string;
  lastActive: string;
  casesAssigned: number;
  department: string;
}

const MOCK_USERS: User[] = [
  { id: "1", name: "Alex Morgan", email: "alex.morgan@company.com", role: "admin", status: "active", initials: "AM", lastActive: "Online now", casesAssigned: 12, department: "Security Operations" },
  { id: "2", name: "Sarah Chen", email: "sarah.chen@company.com", role: "investigator", status: "active", initials: "SC", lastActive: "2 min ago", casesAssigned: 8, department: "Fraud Investigation" },
  { id: "3", name: "Marcus Reid", email: "marcus.reid@company.com", role: "investigator", status: "active", initials: "MR", lastActive: "1 hr ago", casesAssigned: 15, department: "Fraud Investigation" },
  { id: "4", name: "Priya Nair", email: "priya.nair@company.com", role: "analyst", status: "active", initials: "PN", lastActive: "3 hr ago", casesAssigned: 0, department: "Analytics" },
  { id: "5", name: "James Wilson", email: "james.wilson@company.com", role: "analyst", status: "inactive", initials: "JW", lastActive: "2 days ago", casesAssigned: 0, department: "Analytics" },
  { id: "6", name: "Emily Torres", email: "emily.torres@company.com", role: "viewer", status: "pending", initials: "ET", lastActive: "Invite pending", casesAssigned: 0, department: "Compliance" },
  { id: "7", name: "David Kim", email: "david.kim@company.com", role: "investigator", status: "active", initials: "DK", lastActive: "5 min ago", casesAssigned: 6, department: "Fraud Investigation" },
  { id: "8", name: "Rachel Green", email: "rachel.green@company.com", role: "viewer", status: "active", initials: "RG", lastActive: "1 day ago", casesAssigned: 0, department: "Finance" },
];

const ROLE_CONFIG: Record<UserRole, { label: string; className: string; permissions: string }> = {
  admin: { label: "Admin", className: "bg-violet-500/15 text-violet-400 border-violet-500/25", permissions: "Full access" },
  investigator: { label: "Investigator", className: "bg-blue-500/15 text-blue-400 border-blue-500/25", permissions: "Investigate & resolve cases" },
  analyst: { label: "Analyst", className: "bg-emerald-500/15 text-emerald-400 border-emerald-500/25", permissions: "View & analyze data" },
  viewer: { label: "Viewer", className: "bg-slate-500/15 text-slate-400 border-slate-500/25", permissions: "Read-only access" },
};

const STATUS_CONFIG: Record<UserStatus, { label: string; className: string; icon: typeof CheckCircle2 }> = {
  active: { label: "Active", className: "bg-emerald-500/15 text-emerald-400", icon: CheckCircle2 },
  inactive: { label: "Inactive", className: "bg-slate-500/15 text-slate-400", icon: XCircle },
  pending: { label: "Pending", className: "bg-amber-500/15 text-amber-400", icon: Clock },
};

export default function UsersPage() {
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState<UserRole | "all">("all");
  const [statusFilter, setStatusFilter] = useState<UserStatus | "all">("all");
  const [users, setUsers] = useState(MOCK_USERS);

  const filteredUsers = users.filter((user) => {
    const matchSearch = !search || user.name.toLowerCase().includes(search.toLowerCase()) || user.email.toLowerCase().includes(search.toLowerCase());
    const matchRole = roleFilter === "all" || user.role === roleFilter;
    const matchStatus = statusFilter === "all" || user.status === statusFilter;
    return matchSearch && matchRole && matchStatus;
  });

  const activeCount = users.filter((u) => u.status === "active").length;
  const pendingCount = users.filter((u) => u.status === "pending").length;

  function resendInvite(email: string) {
    console.warn("Resending invite to:", email);
  }

  function handleToggleStatus(userId: string) {
    setUsers((prev) =>
      prev.map((u) =>
        u.id === userId
          ? { ...u, status: u.status === "active" ? "inactive" : "active" }
          : u
      )
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Users</h1>
          <p className="mt-1 text-sm text-muted-foreground">Manage team members and permissions</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-1.5">
            <UserPlus className="h-3.5 w-3.5" />
            Invite Member
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5">
            <Shield className="h-3.5 w-3.5" />
            Roles & Permissions
          </Button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { label: "Total Users", value: users.length.toString(), icon: Users, color: "text-blue-400", bg: "bg-blue-400/10" },
          { label: "Active", value: activeCount.toString(), icon: CheckCircle2, color: "text-emerald-400", bg: "bg-emerald-400/10" },
          { label: "Pending Invites", value: pendingCount.toString(), icon: Clock, color: "text-amber-400", bg: "bg-amber-400/10" },
          { label: "Investigators", value: users.filter((u) => u.role === "investigator").length.toString(), icon: Shield, color: "text-violet-400", bg: "bg-violet-400/10" },
        ].map((stat) => (
          <Card key={stat.label} className="gradient-border">
            <CardContent className="flex items-center gap-4 py-4">
              <div className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-lg", stat.bg)}>
                <stat.icon className={cn("h-5 w-5", stat.color)} />
              </div>
              <div>
                <p className="text-2xl font-bold tabular-nums">{stat.value}</p>
                <p className="text-xs text-muted-foreground">{stat.label}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="flex flex-wrap items-center gap-3 py-4">
          <div className="relative min-w-[200px] flex-1">
            <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search users..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-8 pl-8 text-sm"
            />
          </div>

          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value as UserRole | "all")}
            className="h-8 rounded-md border border-input bg-background px-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          >
            <option value="all">All Roles</option>
            <option value="admin">Admin</option>
            <option value="investigator">Investigator</option>
            <option value="analyst">Analyst</option>
            <option value="viewer">Viewer</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as UserStatus | "all")}
            className="h-8 rounded-md border border-input bg-background px-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="pending">Pending</option>
          </select>

          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Filter className="h-3 w-3" />
            {filteredUsers.length} users
          </div>
        </CardContent>
      </Card>

      {/* Users List */}
      <Card>
        <CardContent className="p-0">
          <div className="divide-y divide-border/60">
            {filteredUsers.map((user) => {
              const roleCfg = ROLE_CONFIG[user.role];
              const statusCfg = STATUS_CONFIG[user.status];
              const StatusIcon = statusCfg.icon;

              return (
                <div key={user.id} className="flex items-center gap-4 px-6 py-4 hover:bg-muted/20 transition-colors">
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={undefined} alt={user.name} />
                    <AvatarFallback className="bg-primary/15 text-xs font-bold text-primary">
                      {user.initials}
                    </AvatarFallback>
                  </Avatar>

                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium">{user.name}</p>
                      {user.status === "active" && (
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground">{user.email}</p>
                  </div>

                  <div className="hidden items-center gap-2 lg:flex">
                    <Badge variant="outline" className={cn("text-[10px]", roleCfg.className)}>
                      {roleCfg.label}
                    </Badge>
                    <span className="flex items-center gap-1 text-xs text-muted-foreground">
                      <StatusIcon className={cn("h-3 w-3", user.status === "active" ? "text-emerald-400" : user.status === "pending" ? "text-amber-400" : "text-muted-foreground")} />
                      {statusCfg.label}
                    </span>
                  </div>

                  <div className="hidden text-right lg:block">
                    <p className="text-sm font-medium">{user.department}</p>
                    {user.casesAssigned > 0 && (
                      <p className="text-xs text-muted-foreground">{user.casesAssigned} cases</p>
                    )}
                  </div>

                  <span className="hidden text-xs text-muted-foreground lg:block">
                    {user.lastActive}
                  </span>

                  <div className="flex items-center gap-1">
                    {user.status === "pending" ? (
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-7 gap-1 text-xs"
                        onClick={() => resendInvite(user.email)}
                      >
                        <RefreshCw className="h-3 w-3" />
                        Resend
                      </Button>
                    ) : (
                      <Button variant="ghost" size="icon" className="h-7 w-7">
                        <Settings className="h-4 w-4" />
                      </Button>
                    )}
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-7 w-7">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-44">
                        <DropdownMenuItem className="gap-2">
                          <Settings className="h-4 w-4" /> Edit user
                        </DropdownMenuItem>
                        <DropdownMenuItem className="gap-2">
                          <Mail className="h-4 w-4" /> Send email
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        {user.status === "active" ? (
                          <DropdownMenuItem className="gap-2 text-amber-400" onClick={() => handleToggleStatus(user.id)}>
                            <XCircle className="h-4 w-4" /> Deactivate
                          </DropdownMenuItem>
                        ) : user.status === "inactive" ? (
                          <DropdownMenuItem className="gap-2 text-emerald-400" onClick={() => handleToggleStatus(user.id)}>
                            <CheckCircle2 className="h-4 w-4" /> Activate
                          </DropdownMenuItem>
                        ) : null}
                        <DropdownMenuSeparator />
                        <DropdownMenuItem className="gap-2 text-destructive focus:text-destructive">
                          <Trash2 className="h-4 w-4" /> Remove user
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Role Permissions */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Role Permissions</CardTitle>
          <CardDescription>Overview of permissions by role</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {Object.entries(ROLE_CONFIG).map(([role, config]) => (
              <div key={role} className="rounded-lg border border-border bg-card p-4">
                <div className="mb-3 flex items-center justify-between">
                  <Badge variant="outline" className={config.className}>
                    {config.label}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground mb-3">{config.permissions}</p>
                <div className="space-y-2 text-xs">
                  {role === "admin" && (
                    <>
                      <div className="flex items-center gap-2 text-emerald-400"><CheckCircle2 className="h-3 w-3" /> Full system access</div>
                      <div className="flex items-center gap-2 text-emerald-400"><CheckCircle2 className="h-3 w-3" /> Manage users</div>
                      <div className="flex items-center gap-2 text-emerald-400"><CheckCircle2 className="h-3 w-3" /> Configure settings</div>
                      <div className="flex items-center gap-2 text-slate-400"><XCircle className="h-3 w-3" /> Delete audit logs</div>
                    </>
                  )}
                  {role === "investigator" && (
                    <>
                      <div className="flex items-center gap-2 text-emerald-400"><CheckCircle2 className="h-3 w-3" /> View all cases</div>
                      <div className="flex items-center gap-2 text-emerald-400"><CheckCircle2 className="h-3 w-3" /> Investigate & resolve</div>
                      <div className="flex items-center gap-2 text-emerald-400"><CheckCircle2 className="h-3 w-3" /> Block transactions</div>
                      <div className="flex items-center gap-2 text-slate-400"><XCircle className="h-3 w-3" /> Manage users</div>
                    </>
                  )}
                  {role === "analyst" && (
                    <>
                      <div className="flex items-center gap-2 text-emerald-400"><CheckCircle2 className="h-3 w-3" /> View reports</div>
                      <div className="flex items-center gap-2 text-emerald-400"><CheckCircle2 className="h-3 w-3" /> Export data</div>
                      <div className="flex items-center gap-2 text-slate-400"><XCircle className="h-3 w-3" /> Resolve cases</div>
                      <div className="flex items-center gap-2 text-slate-400"><XCircle className="h-3 w-3" /> Block transactions</div>
                    </>
                  )}
                  {role === "viewer" && (
                    <>
                      <div className="flex items-center gap-2 text-emerald-400"><CheckCircle2 className="h-3 w-3" /> View dashboard</div>
                      <div className="flex items-center gap-2 text-emerald-400"><CheckCircle2 className="h-3 w-3" /> View cases (read-only)</div>
                      <div className="flex items-center gap-2 text-slate-400"><XCircle className="h-3 w-3" /> Export data</div>
                      <div className="flex items-center gap-2 text-slate-400"><XCircle className="h-3 w-3" /> Modify anything</div>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
