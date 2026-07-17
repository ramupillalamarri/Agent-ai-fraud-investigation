"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ShieldCheck,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const PASSWORD_RULES = [
  { label: "At least 8 characters", test: (p: string) => p.length >= 8 },
  { label: "One uppercase letter", test: (p: string) => /[A-Z]/.test(p) },
  { label: "One number", test: (p: string) => /[0-9]/.test(p) },
  { label: "One special character", test: (p: string) => /[^A-Za-z0-9]/.test(p) },
];

export default function ResetPasswordPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const passwordStrength = PASSWORD_RULES.filter((r) => r.test(password)).length;

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");

    if (!password || !confirmPassword) {
      setError("Please fill in both fields.");
      return;
    }
    if (PASSWORD_RULES.some((r) => !r.test(password))) {
      setError("Password does not meet all requirements.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    // Mock API — simulate password reset
    await new Promise((r) => setTimeout(r, 1300));
    setLoading(false);
    setSuccess(true);

    setTimeout(() => router.push("/login"), 2500);
  }

  return (
    <div className="relative flex min-h-screen w-full overflow-hidden bg-background">
      {/* Background grid */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(hsl(var(--border)) 1px, transparent 1px),
            linear-gradient(to right, hsl(var(--border)) 1px, transparent 1px)`,
          backgroundSize: "40px 40px",
        }}
      />

      {/* Left branding panel */}
      <div className="relative hidden w-1/2 flex-col justify-between border-r border-border bg-sidebar p-12 lg:flex">
        <div className="absolute left-0 top-0 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/10 blur-[120px]" />

        <div className="relative z-10">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <ShieldCheck className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="text-lg font-semibold tracking-tight text-foreground">FraudShield</span>
          </Link>
        </div>

        <div className="relative z-10 space-y-6">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
              <span className="h-1.5 w-1.5 rounded-full bg-primary" />
              Password Reset
            </div>
            <h1 className="text-4xl font-bold tracking-tight text-foreground">
              Set a
              <br />
              <span className="text-primary">New Password</span>
            </h1>
            <p className="max-w-xs text-sm leading-relaxed text-muted-foreground">
              Choose a strong, unique password to secure your enterprise account.
            </p>
          </div>

          <div className="rounded-xl border border-border bg-card p-5 space-y-3">
            <p className="text-xs font-medium text-foreground">Password requirements</p>
            <div className="space-y-2">
              {PASSWORD_RULES.map((rule) => (
                <div
                  key={rule.label}
                  className={`flex items-center gap-2.5 text-xs transition-colors ${
                    rule.test(password) ? "text-green-400" : "text-muted-foreground"
                  }`}
                >
                  <div
                    className={`h-1.5 w-1.5 rounded-full transition-colors ${
                      rule.test(password) ? "bg-green-400" : "bg-muted-foreground/40"
                    }`}
                  />
                  {rule.label}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="relative z-10">
          <p className="text-xs text-muted-foreground/60">
            © {new Date().getFullYear()} FraudShield Inc. Enterprise Edition.
          </p>
        </div>
      </div>

      {/* Right — form */}
      <div className="flex w-full items-center justify-center p-6 lg:w-1/2 lg:p-12">
        <div className="w-full max-w-sm space-y-8">
          {/* Mobile logo */}
          <div className="flex items-center gap-2.5 lg:hidden">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <ShieldCheck className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="text-lg font-semibold tracking-tight">FraudShield</span>
          </div>

          {success ? (
            <div className="space-y-6 text-center">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-500/10 ring-1 ring-green-500/20">
                <CheckCircle2 className="h-8 w-8 text-green-400" />
              </div>
              <div className="space-y-2">
                <h2 className="text-2xl font-bold tracking-tight">Password updated</h2>
                <p className="text-sm text-muted-foreground">
                  Your password has been reset. Redirecting you to sign in…
                </p>
              </div>
              <div className="h-1 w-full overflow-hidden rounded-full bg-border">
                <div className="h-full animate-[progress_2.5s_linear_forwards] rounded-full bg-primary" />
              </div>
            </div>
          ) : (
            <>
              <div className="space-y-1.5">
                <h2 className="text-2xl font-bold tracking-tight">Reset your password</h2>
                <p className="text-sm text-muted-foreground">
                  Enter and confirm your new password below.
                </p>
              </div>

              <form className="space-y-5" onSubmit={handleSubmit}>
                {error && (
                  <div className="rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-2.5 text-xs text-red-400">
                    {error}
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="password">New Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••••••"
                      className="pl-9 pr-9"
                      autoComplete="new-password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      disabled={loading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
                      aria-label="Toggle password visibility"
                      disabled={loading}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>

                  {/* Strength bar */}
                  {password && (
                    <div className="flex gap-1 pt-1">
                      {[1, 2, 3, 4].map((i) => (
                        <div
                          key={i}
                          className="h-1 flex-1 rounded-full transition-colors"
                          style={{
                            backgroundColor:
                              i <= passwordStrength
                                ? passwordStrength <= 1
                                  ? "hsl(var(--destructive))"
                                  : passwordStrength === 2
                                  ? "#f59e0b"
                                  : passwordStrength === 3
                                  ? "#3b82f6"
                                  : "#22c55e"
                                : "hsl(var(--border))",
                          }}
                        />
                      ))}
                    </div>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm New Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="confirmPassword"
                      type={showConfirm ? "text" : "password"}
                      placeholder="••••••••••••"
                      className="pl-9 pr-9"
                      autoComplete="new-password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      disabled={loading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirm(!showConfirm)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
                      aria-label="Toggle confirm password visibility"
                      disabled={loading}
                    >
                      {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  {confirmPassword && password !== confirmPassword && (
                    <p className="text-xs text-red-400">Passwords do not match</p>
                  )}
                </div>

                {/* Mobile password rules */}
                <div className="grid grid-cols-2 gap-1 lg:hidden">
                  {PASSWORD_RULES.map((rule) => (
                    <p
                      key={rule.label}
                      className={`flex items-center gap-1.5 text-xs transition-colors ${
                        rule.test(password) ? "text-green-400" : "text-muted-foreground"
                      }`}
                    >
                      <span
                        className={`h-1 w-1 rounded-full ${
                          rule.test(password) ? "bg-green-400" : "bg-muted-foreground"
                        }`}
                      />
                      {rule.label}
                    </p>
                  ))}
                </div>

                <Button
                  type="submit"
                  className="w-full gap-2 font-medium"
                  size="lg"
                  disabled={loading}
                >
                  {loading ? "Updating password..." : "Update Password"}
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </form>

              <Link href="/login">
                <Button variant="ghost" className="w-full gap-2 text-muted-foreground">
                  <ArrowLeft className="h-4 w-4" />
                  Back to sign in
                </Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
