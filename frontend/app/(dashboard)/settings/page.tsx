"use client";

import { useState } from "react";
import {
  Save,
  User,
  Shield,
  Bell,
  Bot,
  Users,
  Plug,
  ChevronRight,
  Plus,
  Trash2,
  CheckCircle2,
  RefreshCw,
  AlertTriangle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const TEAM_MEMBERS = [
  { name: "Alex Morgan", email: "alex.morgan@company.com", role: "Admin", status: "active", initials: "AM", lastActive: "Online now" },
  { name: "Sarah Chen", email: "sarah.chen@company.com", role: "Investigator", status: "active", initials: "SC", lastActive: "2 min ago" },
  { name: "Marcus Reid", email: "marcus.reid@company.com", role: "Investigator", status: "active", initials: "MR", lastActive: "1 hr ago" },
  { name: "Priya Nair", email: "priya.nair@company.com", role: "Analyst", status: "active", initials: "PN", lastActive: "3 hr ago" },
  { name: "James Wilson", email: "james.wilson@company.com", role: "Analyst", status: "inactive", initials: "JW", lastActive: "2 days ago" },
  { name: "Emily Torres", email: "emily.torres@company.com", role: "Viewer", status: "pending", initials: "ET", lastActive: "Invite pending" },
];

const INTEGRATIONS = [
  { name: "Stripe Radar", description: "Transaction data & payment signals", status: "connected", icon: "💳", lastSync: "2 min ago" },
  { name: "Plaid", description: "Bank account verification & ACH data", status: "connected", icon: "🏦", lastSync: "15 min ago" },
  { name: "OFAC Sanctions List", description: "Real-time sanctions screening", status: "connected", icon: "🛡️", lastSync: "1 hr ago" },
  { name: "Slack", description: "Alert notifications to channels", status: "connected", icon: "💬", lastSync: "Real-time" },
  { name: "Splunk SIEM", description: "Security event log forwarding", status: "disconnected", icon: "📊", lastSync: "—" },
  { name: "Salesforce CRM", description: "Customer data enrichment", status: "disconnected", icon: "☁️", lastSync: "—" },
];

type SettingsState = {
  platformName: string;
  timezone: string;
  language: string;
  currency: string;
  dateFormat: string;
  sessionTimeout: string;
  twoFactorEnabled: boolean;
  ssoEnabled: boolean;
  ipAllowlist: string;
  auditLogging: boolean;
  passwordExpiry: string;
  emailAlerts: boolean;
  slackAlerts: boolean;
  webhookAlerts: boolean;
  alertCritical: boolean;
  alertHigh: boolean;
  alertMedium: boolean;
  alertLow: boolean;
  dailyDigest: boolean;
  model: string;
  confidenceThreshold: number;
  maxAgents: number;
  autoEscalate: boolean;
  autoBlock: boolean;
  trainingMode: string;
  explainability: boolean;
};

function FormRow({
  label,
  description,
  children,
}: {
  label: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-3 py-4 sm:flex-row sm:items-start sm:justify-between">
      <div className="min-w-0 max-w-sm">
        <p className="text-sm font-medium">{label}</p>
        {description && <p className="mt-0.5 text-xs text-muted-foreground leading-relaxed">{description}</p>}
      </div>
      <div className="sm:w-64">{children}</div>
    </div>
  );
}

function SwitchRow({
  label,
  description,
  checked,
  onCheckedChange,
}: {
  label: string;
  description?: string;
  checked: boolean;
  onCheckedChange: (v: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between gap-4 py-3">
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium">{label}</p>
        {description && <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>}
      </div>
      <Switch checked={checked} onCheckedChange={onCheckedChange} />
    </div>
  );
}

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("general");
  const [saved, setSaved] = useState(false);
  const [settings, setSettings] = useState<SettingsState>({
    platformName: "FraudShield Enterprise",
    timezone: "America/New_York",
    language: "en",
    currency: "USD",
    dateFormat: "MM/DD/YYYY",
    sessionTimeout: "30",
    twoFactorEnabled: true,
    ssoEnabled: false,
    ipAllowlist: "0.0.0.0/0",
    auditLogging: true,
    passwordExpiry: "90",
    emailAlerts: true,
    slackAlerts: true,
    webhookAlerts: false,
    alertCritical: true,
    alertHigh: true,
    alertMedium: false,
    alertLow: false,
    dailyDigest: true,
    model: "gpt-4o",
    confidenceThreshold: 82,
    maxAgents: 10,
    autoEscalate: true,
    autoBlock: false,
    trainingMode: "continuous",
    explainability: true,
  });

  function set<K extends keyof SettingsState>(key: K, value: SettingsState[K]) {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  }

  function handleSave() {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  }

  const TABS = [
    { value: "general", label: "General", icon: User },
    { value: "security", label: "Security", icon: Shield },
    { value: "notifications", label: "Notifications", icon: Bell },
    { value: "ai", label: "AI Config", icon: Bot },
    { value: "team", label: "Team", icon: Users },
    { value: "integrations", label: "Integrations", icon: Plug },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
          <p className="mt-1 text-sm text-muted-foreground">Configure your FraudShield platform</p>
        </div>
        <Button size="sm" className="gap-1.5" onClick={handleSave}>
          {saved ? <CheckCircle2 className="h-3.5 w-3.5" /> : <Save className="h-3.5 w-3.5" />}
          {saved ? "Saved!" : "Save changes"}
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        {/* Vertical layout for desktop, horizontal scroll for mobile */}
        <div className="flex flex-col gap-6 lg:flex-row lg:gap-8">
          {/* Sidebar nav */}
          <aside className="lg:w-48">
            <nav className="flex flex-row gap-1 overflow-x-auto lg:flex-col">
              {TABS.map((tab) => (
                <button
                  key={tab.value}
                  type="button"
                  onClick={() => setActiveTab(tab.value)}
                  className={cn(
                    "flex items-center gap-2.5 whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    activeTab === tab.value
                      ? "bg-accent text-foreground"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted/50",
                  )}
                >
                  <tab.icon className="h-4 w-4 shrink-0" />
                  {tab.label}
                  {activeTab === tab.value && (
                    <ChevronRight className="ml-auto hidden h-3.5 w-3.5 lg:block" />
                  )}
                </button>
              ))}
            </nav>
          </aside>

          {/* Content */}
          <div className="min-w-0 flex-1">
            {/* General */}
            <TabsContent value="general">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">General Settings</CardTitle>
                  <CardDescription>Configure platform identity and regional preferences</CardDescription>
                </CardHeader>
                <CardContent className="divide-y divide-border/60">
                  <FormRow label="Platform Name" description="Displayed in the sidebar and reports">
                    <Input
                      value={settings.platformName}
                      onChange={(e) => set("platformName", e.target.value)}
                      className="h-8 text-sm"
                    />
                  </FormRow>
                  <FormRow label="Timezone" description="Used for timestamps and scheduled reports">
                    <select
                      value={settings.timezone}
                      onChange={(e) => set("timezone", e.target.value)}
                      className="h-8 w-full rounded-md border border-input bg-background px-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                    >
                      <option value="America/New_York">Eastern (UTC-5)</option>
                      <option value="America/Chicago">Central (UTC-6)</option>
                      <option value="America/Los_Angeles">Pacific (UTC-8)</option>
                      <option value="UTC">UTC</option>
                      <option value="Europe/London">London (UTC+0)</option>
                    </select>
                  </FormRow>
                  <FormRow label="Display Language">
                    <select
                      value={settings.language}
                      onChange={(e) => set("language", e.target.value)}
                      className="h-8 w-full rounded-md border border-input bg-background px-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                    >
                      <option value="en">English</option>
                      <option value="es">Español</option>
                      <option value="fr">Français</option>
                      <option value="de">Deutsch</option>
                    </select>
                  </FormRow>
                  <FormRow label="Default Currency">
                    <select
                      value={settings.currency}
                      onChange={(e) => set("currency", e.target.value)}
                      className="h-8 w-full rounded-md border border-input bg-background px-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                    >
                      <option value="USD">USD — US Dollar</option>
                      <option value="EUR">EUR — Euro</option>
                      <option value="GBP">GBP — British Pound</option>
                    </select>
                  </FormRow>
                  <FormRow label="Date Format">
                    <select
                      value={settings.dateFormat}
                      onChange={(e) => set("dateFormat", e.target.value)}
                      className="h-8 w-full rounded-md border border-input bg-background px-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                    >
                      <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                      <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                      <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                    </select>
                  </FormRow>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Security */}
            <TabsContent value="security">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Security & Access</CardTitle>
                  <CardDescription>Authentication, session management, and audit controls</CardDescription>
                </CardHeader>
                <CardContent className="divide-y divide-border/60">
                  <SwitchRow
                    label="Two-Factor Authentication (2FA)"
                    description="Require TOTP or hardware key for all users"
                    checked={settings.twoFactorEnabled}
                    onCheckedChange={(v) => set("twoFactorEnabled", v)}
                  />
                  <SwitchRow
                    label="Single Sign-On (SSO)"
                    description="Enable SAML 2.0 / OIDC integration"
                    checked={settings.ssoEnabled}
                    onCheckedChange={(v) => set("ssoEnabled", v)}
                  />
                  <SwitchRow
                    label="Audit Logging"
                    description="Log all user actions and data access events"
                    checked={settings.auditLogging}
                    onCheckedChange={(v) => set("auditLogging", v)}
                  />
                  <FormRow
                    label="Session Timeout"
                    description="Auto-logout after inactivity (minutes)"
                  >
                    <Input
                      type="number"
                      value={settings.sessionTimeout}
                      onChange={(e) => set("sessionTimeout", e.target.value)}
                      className="h-8 text-sm"
                      min="5"
                      max="480"
                    />
                  </FormRow>
                  <FormRow
                    label="Password Expiry"
                    description="Force password reset every N days (0 = never)"
                  >
                    <Input
                      type="number"
                      value={settings.passwordExpiry}
                      onChange={(e) => set("passwordExpiry", e.target.value)}
                      className="h-8 text-sm"
                      min="0"
                    />
                  </FormRow>
                  <FormRow
                    label="IP Allowlist"
                    description="CIDR ranges allowed to access the platform (one per line)"
                  >
                    <Textarea
                      value={settings.ipAllowlist}
                      onChange={(e) => set("ipAllowlist", e.target.value)}
                      className="text-sm font-mono"
                      rows={3}
                    />
                  </FormRow>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Notifications */}
            <TabsContent value="notifications">
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Notification Channels</CardTitle>
                    <CardDescription>Where to send platform alerts</CardDescription>
                  </CardHeader>
                  <CardContent className="divide-y divide-border/60">
                    <SwitchRow
                      label="Email Alerts"
                      description="Send alerts to team member email addresses"
                      checked={settings.emailAlerts}
                      onCheckedChange={(v) => set("emailAlerts", v)}
                    />
                    <SwitchRow
                      label="Slack Integration"
                      description="Post alerts to #fraud-alerts channel"
                      checked={settings.slackAlerts}
                      onCheckedChange={(v) => set("slackAlerts", v)}
                    />
                    <SwitchRow
                      label="Webhook (HTTP POST)"
                      description="Forward events to your custom endpoint"
                      checked={settings.webhookAlerts}
                      onCheckedChange={(v) => set("webhookAlerts", v)}
                    />
                    {settings.webhookAlerts && (
                      <FormRow label="Webhook URL" description="POST target for alert payloads">
                        <Input placeholder="https://your-server.com/webhook" className="h-8 text-sm" />
                      </FormRow>
                    )}
                    <SwitchRow
                      label="Daily Digest Email"
                      description="Receive a morning summary of the prior day's activity"
                      checked={settings.dailyDigest}
                      onCheckedChange={(v) => set("dailyDigest", v)}
                    />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Alert Thresholds</CardTitle>
                    <CardDescription>Which severity levels trigger notifications</CardDescription>
                  </CardHeader>
                  <CardContent className="divide-y divide-border/60">
                    <SwitchRow label="Critical Severity" checked={settings.alertCritical} onCheckedChange={(v) => set("alertCritical", v)} />
                    <SwitchRow label="High Severity" checked={settings.alertHigh} onCheckedChange={(v) => set("alertHigh", v)} />
                    <SwitchRow label="Medium Severity" checked={settings.alertMedium} onCheckedChange={(v) => set("alertMedium", v)} />
                    <SwitchRow label="Low Severity" checked={settings.alertLow} onCheckedChange={(v) => set("alertLow", v)} />
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* AI Config */}
            <TabsContent value="ai">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">AI & Model Configuration</CardTitle>
                  <CardDescription>Tune the detection engine and agentic pipeline behavior</CardDescription>
                </CardHeader>
                <CardContent className="divide-y divide-border/60">
                  <FormRow label="Detection Model" description="LLM powering case analysis and reasoning">
                    <select
                      value={settings.model}
                      onChange={(e) => set("model", e.target.value)}
                      className="h-8 w-full rounded-md border border-input bg-background px-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                    >
                      <option value="gpt-4o">GPT-4o (Recommended)</option>
                      <option value="gpt-4-turbo">GPT-4 Turbo</option>
                      <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                      <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                    </select>
                  </FormRow>
                  <FormRow
                    label="Confidence Threshold"
                    description={`Minimum confidence score to flag a transaction (currently ${settings.confidenceThreshold}%)`}
                  >
                    <input
                      type="range"
                      min="50"
                      max="99"
                      value={settings.confidenceThreshold}
                      onChange={(e) => set("confidenceThreshold", parseInt(e.target.value))}
                      className="h-8 w-full accent-primary"
                    />
                  </FormRow>
                  <FormRow
                    label="Max Concurrent Agents"
                    description="Maximum AI agents running simultaneously"
                  >
                    <Input
                      type="number"
                      value={settings.maxAgents}
                      onChange={(e) => set("maxAgents", parseInt(e.target.value))}
                      className="h-8 text-sm"
                      min="1"
                      max="50"
                    />
                  </FormRow>
                  <FormRow label="Training Mode" description="How the model learns from investigator feedback">
                    <select
                      value={settings.trainingMode}
                      onChange={(e) => set("trainingMode", e.target.value)}
                      className="h-8 w-full rounded-md border border-input bg-background px-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                    >
                      <option value="continuous">Continuous (recommended)</option>
                      <option value="weekly">Weekly batch</option>
                      <option value="manual">Manual only</option>
                    </select>
                  </FormRow>
                  <SwitchRow
                    label="Auto-Escalate High Confidence"
                    description="Automatically escalate cases where confidence ≥ 95%"
                    checked={settings.autoEscalate}
                    onCheckedChange={(v) => set("autoEscalate", v)}
                  />
                  <SwitchRow
                    label="Auto-Block Critical Transactions"
                    description="Block transactions with risk score ≥ 95 without human review"
                    checked={settings.autoBlock}
                    onCheckedChange={(v) => set("autoBlock", v)}
                  />
                  <SwitchRow
                    label="Explainability Mode"
                    description="Include AI reasoning chains in case reports"
                    checked={settings.explainability}
                    onCheckedChange={(v) => set("explainability", v)}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            {/* Team */}
            <TabsContent value="team">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <div>
                    <CardTitle className="text-base">Team Members</CardTitle>
                    <CardDescription>{TEAM_MEMBERS.length} members · 4 active</CardDescription>
                  </div>
                  <Button size="sm" className="gap-1.5">
                    <Plus className="h-3.5 w-3.5" />
                    Invite member
                  </Button>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="divide-y divide-border/60">
                    {TEAM_MEMBERS.map((member) => (
                      <div key={member.email} className="flex items-center gap-4 px-6 py-3">
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/15 text-xs font-bold text-primary">
                          {member.initials}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium">{member.name}</p>
                          <p className="text-xs text-muted-foreground">{member.email}</p>
                        </div>
                        <div className="flex items-center gap-3">
                          <Badge
                            variant="outline"
                            className={cn(
                              "text-[10px]",
                              member.status === "active" && "border-emerald-500/30 text-emerald-400",
                              member.status === "inactive" && "border-slate-500/30 text-slate-400",
                              member.status === "pending" && "border-amber-500/30 text-amber-400",
                            )}
                          >
                            {member.status}
                          </Badge>
                          <select
                            defaultValue={member.role}
                            className="h-7 rounded-md border border-input bg-background px-2 text-xs text-foreground focus:outline-none"
                          >
                            <option>Admin</option>
                            <option>Investigator</option>
                            <option>Analyst</option>
                            <option>Viewer</option>
                          </select>
                          <span className="hidden text-[11px] text-muted-foreground sm:block whitespace-nowrap">
                            {member.lastActive}
                          </span>
                          <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-destructive">
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Integrations */}
            <TabsContent value="integrations">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Connected Integrations</CardTitle>
                  <CardDescription>Data sources and third-party services</CardDescription>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="divide-y divide-border/60">
                    {INTEGRATIONS.map((integration) => (
                      <div key={integration.name} className="flex items-center gap-4 px-6 py-4">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-border bg-muted/50 text-xl">
                          {integration.icon}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium">{integration.name}</p>
                          <p className="text-xs text-muted-foreground">{integration.description}</p>
                        </div>
                        <div className="flex items-center gap-3">
                          {integration.status === "connected" ? (
                            <>
                              <div className="hidden flex-col items-end sm:flex">
                                <span className="flex items-center gap-1 text-[11px] text-emerald-400">
                                  <CheckCircle2 className="h-3 w-3" />
                                  Connected
                                </span>
                                <span className="text-[10px] text-muted-foreground">
                                  Last sync: {integration.lastSync}
                                </span>
                              </div>
                              <Button variant="outline" size="sm" className="h-7 gap-1 text-xs">
                                <RefreshCw className="h-3 w-3" />
                                Sync
                              </Button>
                            </>
                          ) : (
                            <>
                              <div className="hidden flex-col items-end sm:flex">
                                <span className="flex items-center gap-1 text-[11px] text-muted-foreground">
                                  <AlertTriangle className="h-3 w-3" />
                                  Not connected
                                </span>
                              </div>
                              <Button size="sm" className="h-7 gap-1 text-xs">
                                <Plug className="h-3 w-3" />
                                Connect
                              </Button>
                            </>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </div>
        </div>
      </Tabs>
    </div>
  );
}
