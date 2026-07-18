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
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { useUsers } from "@/hooks/useUsers";
import { userApi } from "@/lib/api/user";
import { LoadingSpinner, ErrorCard } from "@/components/shared/feedback";

type UserRole = "admin" | "investigator" | "analyst" | "viewer";
type UserStatus = "active" | "inactive" | "pending";

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

  const { users, total, loading, error, refetch } = useUsers({
    limit: 100
  });

  const handleToggleStatus = async (userId: string, currentStatus: boolean) => {
    try {
      await userApi.update(userId, { is_active: !currentStatus });
      refetch();
    } catch (e: any) {
      alert(e.message || "Failed to update user status.");
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (confirm("Are you sure you want to delete this user?")) {
      try {
        await userApi.delete(userId);
        refetch();
      } catch (e: any) {
        alert(e.message || "Failed to delete user.");
      }
    }
  };

  // Local filtering is useful for live filters across role and status
  const filteredUsers = users.filter((u: any) => {
    const roleName = (u.roles?.[0]?.name || "viewer").toLowerCase() as UserRole;
    const statusStr: UserStatus = u.is_active ? "active" : "inactive";
    
    const matchSearch = !search || 
      u.full_name?.toLowerCase().includes(search.toLowerCase()) || 
      u.email?.toLowerCase().includes(search.toLowerCase());
    
    const matchRole = roleFilter === "all" || roleName === roleFilter;
    const matchStatus = statusFilter === "all" || statusStr === statusFilter;
    
    return matchSearch && matchRole && matchStatus;
  });

  const activeCount = users.filter((u: any) => u.is_active).length;
  const inactiveCount = users.filter((u: any) => !u.is_active).length;

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <LoadingSpinner message="Querying user directory registry..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-[80vh] items-center justify-center p-6">
        <ErrorCard message={error} onRetry={refetch} />
      </div>
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
          <Button variant="outline" size="sm" className="gap-1.5" onClick={() => refetch()}>
            Refresh Live
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5">
            <UserPlus className="h-3.5 w-3.5" />
            Invite Member
          </Button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { label: "Total Users", value: total.toString(), icon: Users, color: "text-blue-400", bg: "bg-blue-400/10" },
          { label: "Active Users", value: activeCount.toString(), icon: CheckCircle2, color: "text-emerald-400", bg: "bg-emerald-400/10" },
          { label: "Inactive Users", value: inactiveCount.toString(), icon: XCircle, color: "text-slate-400", bg: "bg-slate-400/10" },
          { label: "Investigators", value: users.filter((u: any) => u.roles?.[0]?.name?.toLowerCase() === "investigator").length.toString(), icon: Shield, color: "text-violet-400", bg: "bg-violet-400/10" },
        ].map((stat) => (
          <Card key={stat.label} className="gradient-border bg-white border border-slate-100 shadow-sm rounded-xl">
            <CardContent className="flex items-center gap-4 py-4">
              <div className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-lg", stat.bg)}>
                <stat.icon className={cn("h-5 w-5", stat.color)} />
              </div>
              <div>
                <p className="text-2xl font-bold tabular-nums text-slate-800">{stat.value}</p>
                <p className="text-xs font-semibold text-slate-500">{stat.label}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <Card className="bg-white border border-slate-100 shadow-sm rounded-xl">
        <CardContent className="flex flex-wrap items-center gap-3 py-4">
          <div className="relative min-w-[200px] flex-1">
            <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
            <Input
              placeholder="Search users..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-8 pl-8 text-sm bg-slate-50 border-0"
            />
          </div>

          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value as UserRole | "all")}
            className="h-8 rounded-md border border-slate-200 bg-white px-2 text-xs text-slate-700 font-semibold focus:outline-none focus:ring-1 focus:ring-indigo-500"
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
            className="h-8 rounded-md border border-slate-200 bg-white px-2 text-xs text-slate-700 font-semibold focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>

          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-semibold">
            <Filter className="h-3 w-3" />
            {filteredUsers.length} users filtered
          </div>
        </CardContent>
      </Card>

      {/* Users List */}
      <Card className="bg-white border border-slate-100 shadow-sm rounded-xl overflow-hidden">
        <CardContent className="p-0">
          <div className="divide-y divide-slate-100">
            {filteredUsers.map((user: any) => {
              const roleName = (user.roles?.[0]?.name || "viewer").toLowerCase() as UserRole;
              const roleCfg = ROLE_CONFIG[roleName] || ROLE_CONFIG.viewer;
              const userStatus: UserStatus = user.is_active ? "active" : "inactive";
              const statusCfg = STATUS_CONFIG[userStatus];
              const StatusIcon = statusCfg.icon;

              const initials = user.full_name
                ? user.full_name.split(' ').map((n: string) => n[0]).join('').substring(0, 2).toUpperCase()
                : "US";

              return (
                <div key={user.id} className="flex items-center gap-4 px-6 py-4 hover:bg-slate-50/50 transition-colors">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback className="bg-indigo-50 text-indigo-700 text-xs font-bold border border-indigo-100">
                      {initials}
                    </AvatarFallback>
                  </Avatar>

                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-semibold text-slate-800">{user.full_name}</p>
                      {user.is_active && (
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                      )}
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">{user.email}</p>
                  </div>

                  <div className="hidden items-center gap-2 lg:flex">
                    <Badge variant="outline" className={cn("text-[10px] font-bold border", roleCfg.className)}>
                      {roleCfg.label}
                    </Badge>
                    <span className="flex items-center gap-1 text-xs text-slate-500 font-medium">
                      <StatusIcon className={cn("h-3 w-3", user.is_active ? "text-emerald-500" : "text-slate-400")} />
                      {statusCfg.label}
                    </span>
                  </div>

                  <div className="hidden text-right lg:block">
                    <p className="text-sm font-semibold text-slate-800">{user.roles?.[0]?.description || "Operations"}</p>
                  </div>

                  <span className="hidden text-xs text-slate-400 lg:block font-medium">
                    {user.is_active ? "Online now" : "Inactive"}
                  </span>

                  <div className="flex items-center gap-1">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-7 w-7 text-slate-500 hover:bg-slate-100">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-44">
                        <DropdownMenuItem className="gap-2 cursor-pointer">
                          <Settings className="h-4 w-4" /> Edit user
                        </DropdownMenuItem>
                        <DropdownMenuItem className="gap-2 cursor-pointer">
                          <Mail className="h-4 w-4" /> Send email
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem 
                          className={cn("gap-2 cursor-pointer font-semibold", user.is_active ? "text-amber-600 focus:bg-amber-50/50" : "text-emerald-600 focus:bg-emerald-50/50")} 
                          onClick={() => handleToggleStatus(user.id, user.is_active)}
                        >
                          {user.is_active ? (
                            <>
                              <XCircle className="h-4 w-4" /> Deactivate
                            </>
                          ) : (
                            <>
                              <CheckCircle2 className="h-4 w-4" /> Activate
                            </>
                          )}
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem 
                          className="gap-2 cursor-pointer text-rose-600 focus:bg-rose-50/50 font-semibold"
                          onClick={() => handleDeleteUser(user.id)}
                        >
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
      <Card className="bg-white border border-slate-100 shadow-sm rounded-xl">
        <CardHeader className="pb-2 bg-slate-50/50">
          <CardTitle className="text-base font-bold text-slate-800">Role Permissions</CardTitle>
          <CardDescription className="text-xs text-slate-500">Overview of permissions by role</CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {Object.entries(ROLE_CONFIG).map(([role, config]) => (
              <div key={role} className="rounded-lg border border-slate-100 bg-slate-50/30 p-4">
                <div className="mb-3 flex items-center justify-between">
                  <Badge variant="outline" className={cn("text-[10px] font-bold border", config.className)}>
                    {config.label}
                  </Badge>
                </div>
                <p className="text-xs font-semibold text-slate-600 mb-3">{config.permissions}</p>
                <div className="space-y-2 text-xs font-medium text-slate-500">
                  {role === "admin" && (
                    <>
                      <div className="flex items-center gap-2 text-emerald-600"><CheckCircle2 className="h-3.5 w-3.5" /> Full system access</div>
                      <div className="flex items-center gap-2 text-emerald-600"><CheckCircle2 className="h-3.5 w-3.5" /> Manage users</div>
                      <div className="flex items-center gap-2 text-emerald-600"><CheckCircle2 className="h-3.5 w-3.5" /> Configure settings</div>
                      <div className="flex items-center gap-2 text-slate-400"><XCircle className="h-3.5 w-3.5" /> Delete audit logs</div>
                    </>
                  )}
                  {role === "investigator" && (
                    <>
                      <div className="flex items-center gap-2 text-emerald-600"><CheckCircle2 className="h-3.5 w-3.5" /> View all cases</div>
                      <div className="flex items-center gap-2 text-emerald-600"><CheckCircle2 className="h-3.5 w-3.5" /> Investigate & resolve</div>
                      <div className="flex items-center gap-2 text-emerald-600"><CheckCircle2 className="h-3.5 w-3.5" /> Block transactions</div>
                      <div className="flex items-center gap-2 text-slate-400"><XCircle className="h-3.5 w-3.5" /> Manage users</div>
                    </>
                  )}
                  {role === "analyst" && (
                    <>
                      <div className="flex items-center gap-2 text-emerald-600"><CheckCircle2 className="h-3.5 w-3.5" /> View reports</div>
                      <div className="flex items-center gap-2 text-emerald-600"><CheckCircle2 className="h-3.5 w-3.5" /> Export data</div>
                      <div className="flex items-center gap-2 text-slate-400"><XCircle className="h-3.5 w-3.5" /> Resolve cases</div>
                      <div className="flex items-center gap-2 text-slate-400"><XCircle className="h-3.5 w-3.5" /> Block transactions</div>
                    </>
                  )}
                  {role === "viewer" && (
                    <>
                      <div className="flex items-center gap-2 text-emerald-600"><CheckCircle2 className="h-3.5 w-3.5" /> View dashboard</div>
                      <div className="flex items-center gap-2 text-emerald-600"><CheckCircle2 className="h-3.5 w-3.5" /> View cases (read-only)</div>
                      <div className="flex items-center gap-2 text-slate-400"><XCircle className="h-3.5 w-3.5" /> Export data</div>
                      <div className="flex items-center gap-2 text-slate-400"><XCircle className="h-3.5 w-3.5" /> Modify anything</div>
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
