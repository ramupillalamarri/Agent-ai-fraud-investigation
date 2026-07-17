"use client";

import { useState } from "react";
import Link from "next/link";
import { ShieldCheck, Mail, ArrowRight, ArrowLeft, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!email) {
      setError("Please enter your email address.");
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError("Please enter a valid email address.");
      return;
    }

    setLoading(true);
    setError("");

    // Mock API — simulate sending reset email
    await new Promise((r) => setTimeout(r, 1200));

    setLoading(false);
    setSent(true);
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
              Account Recovery
            </div>
            <h1 className="text-4xl font-bold tracking-tight text-foreground">
              Regain
              <br />
              <span className="text-primary">Secure Access</span>
            </h1>
            <p className="max-w-xs text-sm leading-relaxed text-muted-foreground">
              We&apos;ll send a secure, time-limited reset link to your registered corporate email.
            </p>
          </div>

          <div className="rounded-xl border border-border bg-card p-5 space-y-3">
            <p className="text-xs font-medium text-foreground">Security reminder</p>
            <ul className="space-y-2">
              {[
                "Links expire after 30 minutes",
                "Each link is single-use only",
                "All reset attempts are logged",
              ].map((item) => (
                <li key={item} className="flex items-center gap-2.5 text-xs text-muted-foreground">
                  <div className="h-1 w-1 rounded-full bg-primary" />
                  {item}
                </li>
              ))}
            </ul>
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

          {sent ? (
            /* Success state */
            <div className="space-y-6 text-center">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 ring-1 ring-primary/20">
                <CheckCircle2 className="h-8 w-8 text-primary" />
              </div>
              <div className="space-y-2">
                <h2 className="text-2xl font-bold tracking-tight">Check your inbox</h2>
                <p className="text-sm text-muted-foreground">
                  We sent a password reset link to{" "}
                  <span className="font-medium text-foreground">{email}</span>.
                </p>
              </div>
              <div className="rounded-lg border border-border bg-card px-5 py-4 text-left space-y-2">
                <p className="text-xs font-medium text-foreground">Didn&apos;t receive the email?</p>
                <ul className="space-y-1.5 text-xs text-muted-foreground">
                  <li>• Check your spam or junk folder</li>
                  <li>• Make sure you used your corporate email</li>
                  <li>• Allow up to 2 minutes for delivery</li>
                </ul>
              </div>
              <div className="space-y-3">
                <Button
                  variant="outline"
                  className="w-full gap-2"
                  onClick={() => { setSent(false); setEmail(""); }}
                >
                  Try a different email
                </Button>
                <Link href="/login">
                  <Button variant="ghost" className="w-full gap-2 text-muted-foreground">
                    <ArrowLeft className="h-4 w-4" />
                    Back to sign in
                  </Button>
                </Link>
              </div>
            </div>
          ) : (
            /* Form state */
            <>
              <div className="space-y-1.5">
                <h2 className="text-2xl font-bold tracking-tight">Forgot your password?</h2>
                <p className="text-sm text-muted-foreground">
                  Enter your corporate email and we&apos;ll send a reset link.
                </p>
              </div>

              <form className="space-y-5" onSubmit={handleSubmit}>
                {error && (
                  <div className="rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-2.5 text-xs text-red-400">
                    {error}
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="email">Corporate Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="you@company.com"
                      className="pl-9"
                      autoComplete="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      disabled={loading}
                    />
                  </div>
                </div>

                <Button
                  type="submit"
                  className="w-full gap-2 font-medium"
                  size="lg"
                  disabled={loading}
                >
                  {loading ? "Sending reset link..." : "Send Reset Link"}
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </form>

              <Link href="/login">
                <Button
                  variant="ghost"
                  className="w-full gap-2 text-muted-foreground"
                >
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
