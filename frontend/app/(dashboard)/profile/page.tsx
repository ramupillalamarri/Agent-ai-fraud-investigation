"use client";

import { useState, useEffect } from "react";
import {
  User,
  Mail,
  Building2,
  Shield,
  Lock,
  Bell,
  Eye,
  EyeOff,
  Save,
  CheckCircle2,
  Camera,
  LogOut,
  Smartphone,
  Globe,
  Moon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface UserProfile {
  name: string;
  email: string;
  role: string;
  organization: string;
  phone: string;
  timezone: string;
  department: string;
  employeeId: string;
}

const TIMEZONES = [
  "UTC",
  "America/New_York",
  "America/Chicago",
  "America/Denver",
  "America/Los_Angeles",
  "Europe/London",
  "Europe/Paris",
  "Asia/Tokyo",
  "Asia/Singapore",
  "Australia/Sydney",
];

function SaveBanner({ visible }: { visible: boolean }) {
  if (!visible) return null;
  return (
    <div className="flex items-center gap-2 rounded-lg border border-green-500/20 bg-green-500/5 px-4 py-2.5 text-xs text-green-400">
      <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />
      Changes saved successfully.
    </div>
  );
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile>({
    name: "Jane Smith",
    email: "jane.smith@fraudshield.io",
    role: "Senior Fraud Analyst",
    organization: "FraudShield Inc.",
    phone: "+1 (555) 000-1234",
    timezone: "America/New_York",
    department: "Fraud Intelligence",
    employeeId: "FS-10042",
  });

  const [passwords, setPasswords] = useState({
    current: "",
    next: "",
    confirm: "",
  });
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNext, setShowNext] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const [notifications, setNotifications] = useState({
    highRiskAlerts: true,
    caseAssignments: true,
    agentCompletions: true,
    weeklyDigest: false,
    systemAnnouncements: true,
    emailAlerts: true,
    smsAlerts: false,
  });

  const [preferences, setPreferences] = useState({
    darkMode: true,
    compactView: false,
    twoFactor: false,
    sessionTimeout: true,
  });

  const [profileSaved, setProfileSaved] = useState(false);
  const [passwordSaved, setPasswordSaved] = useState(false);
  const [notifSaved, setNotifSaved] = useState(false);
  const [profileLoading, setProfileLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [notifLoading, setNotifLoading] = useState(false);
  const [passwordError, setPasswordError] = useState("");
  const [activeTab, setActiveTab] = useState("personal");

  // Load profile from localStorage if available
  useEffect(() => {
    const stored = localStorage.getItem("user_profile");
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setProfile((p) => ({
          ...p,
          name: parsed.name || p.name,
          email: parsed.email || p.email,
          role: parsed.role || p.role,
        }));
      } catch {}
    }
  }, []);

  const initials = profile.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  async function saveProfile(e: React.FormEvent) {
    e.preventDefault();
    setProfileLoading(true);
    await new Promise((r) => setTimeout(r, 1000));
    localStorage.setItem("user_profile", JSON.stringify({ name: profile.name, email: profile.email, role: profile.role }));
    setProfileLoading(false);
    setProfileSaved(true);
    setTimeout(() => setProfileSaved(false), 3000);
  }

  async function savePassword(e: React.FormEvent) {
    e.preventDefault();
    setPasswordError("");
    if (!passwords.current) { setPasswordError("Current password is required."); return; }
    if (passwords.next.length < 8) { setPasswordError("New password must be at least 8 characters."); return; }
    if (passwords.next !== passwords.confirm) { setPasswordError("Passwords do not match."); return; }
    setPasswordLoading(true);
    await new Promise((r) => setTimeout(r, 1100));
    setPasswordLoading(false);
    setPasswords({ current: "", next: "", confirm: "" });
    setPasswordSaved(true);
    setTimeout(() => setPasswordSaved(false), 3000);
  }

  async function saveNotifications(e: React.FormEvent) {
    e.preventDefault();
    setNotifLoading(true);
    await new Promise((r) => setTimeout(r, 800));
    setNotifLoading(false);
    setNotifSaved(true);
    setTimeout(() => setNotifSaved(false), 3000);
  }

  return (
    <div className="min-h-screen space-y-6 p-6">
      {/* Page header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Profile</h1>
          <p className="text-sm text-muted-foreground">
            Manage your account details, security, and preferences.
          </p>
        </div>
        <Badge variant="secondary" className="gap-1.5 text-xs">
          <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-green-400" />
          Active Session
        </Badge>
      </div>

      {/* Identity card */}
      <div className="gradient-border rounded-xl bg-card p-6">
        <div className="flex flex-col items-start gap-5 sm:flex-row sm:items-center">
          <div className="relative">
            <Avatar className="h-20 w-20 text-lg">
              <AvatarFallback className="bg-primary/10 text-primary text-xl font-semibold">
                {initials}
              </AvatarFallback>
            </Avatar>
            <button
              className="absolute -bottom-1 -right-1 flex h-7 w-7 items-center justify-center rounded-full border border-border bg-card text-muted-foreground shadow-sm transition-colors hover:text-foreground"
              aria-label="Change avatar"
            >
              <Camera className="h-3.5 w-3.5" />
            </button>
          </div>
          <div className="flex-1 space-y-1">
            <h2 className="text-xl font-semibold">{profile.name}</h2>
            <p className="text-sm text-muted-foreground">{profile.email}</p>
            <div className="flex flex-wrap gap-2 pt-1">
              <Badge variant="secondary" className="gap-1.5">
                <Shield className="h-3 w-3" />
                {profile.role}
              </Badge>
              <Badge variant="outline" className="gap-1.5 text-muted-foreground">
                <Building2 className="h-3 w-3" />
                {profile.organization}
              </Badge>
              <Badge variant="outline" className="gap-1.5 text-muted-foreground">
                ID: {profile.employeeId}
              </Badge>
            </div>
          </div>
          <Button variant="outline" size="sm" className="gap-2 text-muted-foreground shrink-0">
            <LogOut className="h-3.5 w-3.5" />
            Sign out
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="bg-card border border-border h-10">
          <TabsTrigger value="personal" className="gap-2 data-[state=active]:bg-accent">
            <User className="h-3.5 w-3.5" />
            Personal Info
          </TabsTrigger>
          <TabsTrigger value="security" className="gap-2 data-[state=active]:bg-accent">
            <Lock className="h-3.5 w-3.5" />
            Security
          </TabsTrigger>
          <TabsTrigger value="notifications" className="gap-2 data-[state=active]:bg-accent">
            <Bell className="h-3.5 w-3.5" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="preferences" className="gap-2 data-[state=active]:bg-accent">
            <Moon className="h-3.5 w-3.5" />
            Preferences
          </TabsTrigger>
        </TabsList>

        {/* ── Personal Info ── */}
        <TabsContent value="personal">
          <form onSubmit={saveProfile} className="rounded-xl border border-border bg-card p-6 space-y-6">
            <div>
              <h3 className="font-semibold text-sm">Personal Information</h3>
              <p className="text-xs text-muted-foreground mt-0.5">Update your name, contact details, and work information.</p>
            </div>
            <Separator />

            <SaveBanner visible={profileSaved} />

            <div className="grid gap-5 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="name"
                    className="pl-9"
                    value={profile.name}
                    onChange={(e) => setProfile((p) => ({ ...p, name: e.target.value }))}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    className="pl-9"
                    value={profile.email}
                    onChange={(e) => setProfile((p) => ({ ...p, email: e.target.value }))}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Phone Number</Label>
                <div className="relative">
                  <Smartphone className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="phone"
                    className="pl-9"
                    value={profile.phone}
                    onChange={(e) => setProfile((p) => ({ ...p, phone: e.target.value }))}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="timezone">Timezone</Label>
                <div className="relative">
                  <Globe className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground pointer-events-none z-10" />
                  <select
                    id="timezone"
                    value={profile.timezone}
                    onChange={(e) => setProfile((p) => ({ ...p, timezone: e.target.value }))}
                    className="flex h-9 w-full rounded-md border border-input bg-transparent pl-9 pr-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  >
                    {TIMEZONES.map((tz) => (
                      <option key={tz} value={tz} className="bg-popover">
                        {tz}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="org">Organization</Label>
                <div className="relative">
                  <Building2 className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="org"
                    className="pl-9"
                    value={profile.organization}
                    onChange={(e) => setProfile((p) => ({ ...p, organization: e.target.value }))}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="dept">Department</Label>
                <div className="relative">
                  <Shield className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="dept"
                    className="pl-9"
                    value={profile.department}
                    onChange={(e) => setProfile((p) => ({ ...p, department: e.target.value }))}
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end">
              <Button type="submit" className="gap-2" disabled={profileLoading}>
                <Save className="h-4 w-4" />
                {profileLoading ? "Saving..." : "Save Changes"}
              </Button>
            </div>
          </form>
        </TabsContent>

        {/* ── Security ── */}
        <TabsContent value="security">
          <div className="space-y-4">
            {/* Change password */}
            <form onSubmit={savePassword} className="rounded-xl border border-border bg-card p-6 space-y-5">
              <div>
                <h3 className="font-semibold text-sm">Change Password</h3>
                <p className="text-xs text-muted-foreground mt-0.5">Use a strong, unique password you don&apos;t use elsewhere.</p>
              </div>
              <Separator />

              <SaveBanner visible={passwordSaved} />

              {passwordError && (
                <div className="rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-2.5 text-xs text-red-400">
                  {passwordError}
                </div>
              )}

              <div className="space-y-2 max-w-sm">
                <Label htmlFor="currentPw">Current Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="currentPw"
                    type={showCurrent ? "text" : "password"}
                    placeholder="••••••••••••"
                    className="pl-9 pr-9"
                    value={passwords.current}
                    onChange={(e) => setPasswords((p) => ({ ...p, current: e.target.value }))}
                  />
                  <button type="button" onClick={() => setShowCurrent(!showCurrent)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" aria-label="Toggle">
                    {showCurrent ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 max-w-sm sm:max-w-none">
                <div className="space-y-2">
                  <Label htmlFor="newPw">New Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="newPw"
                      type={showNext ? "text" : "password"}
                      placeholder="••••••••••••"
                      className="pl-9 pr-9"
                      value={passwords.next}
                      onChange={(e) => setPasswords((p) => ({ ...p, next: e.target.value }))}
                    />
                    <button type="button" onClick={() => setShowNext(!showNext)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" aria-label="Toggle">
                      {showNext ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmPw">Confirm New Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="confirmPw"
                      type={showConfirm ? "text" : "password"}
                      placeholder="••••••••••••"
                      className="pl-9 pr-9"
                      value={passwords.confirm}
                      onChange={(e) => setPasswords((p) => ({ ...p, confirm: e.target.value }))}
                    />
                    <button type="button" onClick={() => setShowConfirm(!showConfirm)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" aria-label="Toggle">
                      {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  {passwords.confirm && passwords.next !== passwords.confirm && (
                    <p className="text-xs text-red-400">Passwords do not match</p>
                  )}
                </div>
              </div>

              <div className="flex justify-end">
                <Button type="submit" className="gap-2" disabled={passwordLoading}>
                  <Lock className="h-4 w-4" />
                  {passwordLoading ? "Updating..." : "Update Password"}
                </Button>
              </div>
            </form>

            {/* Security settings */}
            <div className="rounded-xl border border-border bg-card p-6 space-y-5">
              <div>
                <h3 className="font-semibold text-sm">Security Settings</h3>
                <p className="text-xs text-muted-foreground mt-0.5">Control access and authentication options.</p>
              </div>
              <Separator />
              <div className="space-y-4">
                {[
                  {
                    key: "twoFactor" as const,
                    icon: Shield,
                    label: "Two-Factor Authentication",
                    desc: "Require a verification code on each sign-in.",
                  },
                  {
                    key: "sessionTimeout" as const,
                    icon: Lock,
                    label: "Automatic Session Timeout",
                    desc: "Sign out automatically after 30 minutes of inactivity.",
                  },
                ].map(({ key, icon: Icon, label, desc }) => (
                  <div key={key} className="flex items-center justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5 flex h-8 w-8 items-center justify-center rounded-lg bg-accent">
                        <Icon className="h-4 w-4 text-muted-foreground" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">{label}</p>
                        <p className="text-xs text-muted-foreground">{desc}</p>
                      </div>
                    </div>
                    <Switch
                      checked={preferences[key]}
                      onCheckedChange={(v) => setPreferences((p) => ({ ...p, [key]: v }))}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </TabsContent>

        {/* ── Notifications ── */}
        <TabsContent value="notifications">
          <form onSubmit={saveNotifications} className="rounded-xl border border-border bg-card p-6 space-y-6">
            <div>
              <h3 className="font-semibold text-sm">Notification Preferences</h3>
              <p className="text-xs text-muted-foreground mt-0.5">Choose what alerts and updates you receive.</p>
            </div>
            <Separator />

            <SaveBanner visible={notifSaved} />

            {/* Alert types */}
            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">Alert Types</p>
              <div className="space-y-4">
                {[
                  { key: "highRiskAlerts" as const, label: "High-Risk Fraud Alerts", desc: "Immediate notification for critical risk scores." },
                  { key: "caseAssignments" as const, label: "Case Assignments", desc: "When an investigation is assigned to you." },
                  { key: "agentCompletions" as const, label: "Agent Pipeline Completions", desc: "When an AI agent finishes a fraud investigation run." },
                  { key: "weeklyDigest" as const, label: "Weekly Intelligence Digest", desc: "A summary of platform activity every Monday." },
                  { key: "systemAnnouncements" as const, label: "System Announcements", desc: "Platform updates and maintenance notices." },
                ].map(({ key, label, desc }) => (
                  <div key={key} className="flex items-center justify-between gap-4">
                    <div>
                      <p className="text-sm font-medium">{label}</p>
                      <p className="text-xs text-muted-foreground">{desc}</p>
                    </div>
                    <Switch
                      checked={notifications[key]}
                      onCheckedChange={(v) => setNotifications((n) => ({ ...n, [key]: v }))}
                    />
                  </div>
                ))}
              </div>
            </div>

            <Separator />

            {/* Channels */}
            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">Delivery Channels</p>
              <div className="space-y-4">
                {[
                  { key: "emailAlerts" as const, icon: Mail, label: "Email Notifications", desc: "Send alerts to your registered email." },
                  { key: "smsAlerts" as const, icon: Smartphone, label: "SMS Notifications", desc: "Send critical alerts via text message." },
                ].map(({ key, icon: Icon, label, desc }) => (
                  <div key={key} className="flex items-center justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5 flex h-8 w-8 items-center justify-center rounded-lg bg-accent">
                        <Icon className="h-4 w-4 text-muted-foreground" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">{label}</p>
                        <p className="text-xs text-muted-foreground">{desc}</p>
                      </div>
                    </div>
                    <Switch
                      checked={notifications[key]}
                      onCheckedChange={(v) => setNotifications((n) => ({ ...n, [key]: v }))}
                    />
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end">
              <Button type="submit" className="gap-2" disabled={notifLoading}>
                <Save className="h-4 w-4" />
                {notifLoading ? "Saving..." : "Save Preferences"}
              </Button>
            </div>
          </form>
        </TabsContent>

        {/* ── Preferences ── */}
        <TabsContent value="preferences">
          <div className="rounded-xl border border-border bg-card p-6 space-y-6">
            <div>
              <h3 className="font-semibold text-sm">Display Preferences</h3>
              <p className="text-xs text-muted-foreground mt-0.5">Customize the platform appearance and layout.</p>
            </div>
            <Separator />
            <div className="space-y-5">
              {[
                {
                  key: "darkMode" as const,
                  icon: Moon,
                  label: "Dark Mode",
                  desc: "Use the dark color scheme (currently active by default).",
                },
                {
                  key: "compactView" as const,
                  icon: Globe,
                  label: "Compact Table View",
                  desc: "Reduce row padding in transaction and alert tables.",
                },
              ].map(({ key, icon: Icon, label, desc }) => (
                <div key={key} className="flex items-center justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 flex h-8 w-8 items-center justify-center rounded-lg bg-accent">
                      <Icon className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">{label}</p>
                      <p className="text-xs text-muted-foreground">{desc}</p>
                    </div>
                  </div>
                  <Switch
                    checked={preferences[key]}
                    onCheckedChange={(v) => setPreferences((p) => ({ ...p, [key]: v }))}
                  />
                </div>
              ))}
            </div>

            <Separator />

            <div>
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">Account</p>
              <div className="rounded-lg border border-destructive/20 bg-destructive/5 p-4 space-y-3">
                <div>
                  <p className="text-sm font-medium text-destructive">Danger Zone</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    These actions are permanent and cannot be undone.
                  </p>
                </div>
                <div className="flex flex-col gap-2 sm:flex-row">
                  <Button variant="outline" size="sm" className="border-destructive/30 text-destructive hover:bg-destructive/10 gap-2">
                    <LogOut className="h-3.5 w-3.5" />
                    Sign out all devices
                  </Button>
                  <Button variant="outline" size="sm" className="border-destructive/30 text-destructive hover:bg-destructive/10">
                    Delete account
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
