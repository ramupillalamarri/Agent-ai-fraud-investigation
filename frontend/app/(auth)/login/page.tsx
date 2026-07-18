"use client";

import { useState, useEffect, Suspense, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { ShieldCheck, AlertTriangle, Loader2 } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { isDevMode } from "@/lib/auth";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { loginWithGoogle, isAuthenticated } = useAuth();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [registered, setRegistered] = useState(false);
  
  const googleInitialized = useRef(false);

  useEffect(() => {
    if (isAuthenticated || isDevMode()) {
      window.location.href = "/dashboard";
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (searchParams.get("registered") === "1") {
      setRegistered(true);
      router.replace("/login");
    }
  }, [searchParams, router]);

  const loginWithGoogleRef = useRef(loginWithGoogle);
  useEffect(() => {
    loginWithGoogleRef.current = loginWithGoogle;
  }, [loginWithGoogle]);

  useEffect(() => {
    const handleCallback = async (response: any) => {
      console.log("Google OAuth credential response received:", response);
      if (!response || !response.credential) {
        setError("Google sign-in failed: No credential received from Google.");
        return;
      }
      setLoading(true);
      setError("");
      try {
        await loginWithGoogleRef.current(response.credential);
        window.location.href = "/dashboard";
      } catch (err: any) {
        console.error("Google sign-in error:", err);
        const detail = err?.response?.data?.detail || err?.message || "Authentication error";
        setError(`Google sign-in failed: ${detail}`);
        setLoading(false);
      }
    };

    const initializeGoogleSignIn = () => {
      if (typeof window !== "undefined" && (window as any).google && !googleInitialized.current) {
        const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "24491737338-7d1vso3ekkavkhbksji6qmub5nms1gd2.apps.googleusercontent.com";
        (window as any).google.accounts.id.initialize({
          client_id: clientId,
          callback: handleCallback,
          auto_select: false,
        });
        googleInitialized.current = true;

        const container = document.getElementById("google-signin-btn");
        if (container) {
          container.innerHTML = "";
          (window as any).google.accounts.id.renderButton(container, {
            theme: "outline",
            size: "large",
            width: 384,
          });
        }
      }
    };

    const timer = setInterval(() => {
      if (typeof window !== "undefined" && (window as any).google) {
        initializeGoogleSignIn();
        clearInterval(timer);
      }
    }, 300);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="relative flex min-h-screen w-full overflow-hidden bg-background">
      {/* Background grid pattern */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(hsl(var(--border)) 1px, transparent 1px),
            linear-gradient(to right, hsl(var(--border)) 1px, transparent 1px)`,
          backgroundSize: "40px 40px",
        }}
      />

      {/* Left panel — branding */}
      <div className="relative hidden w-1/2 flex-col justify-between border-r border-border bg-sidebar p-12 lg:flex">
        {/* Gradient orb */}
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
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-primary" />
              Agentic AI Platform
            </div>
            <h1 className="text-4xl font-bold tracking-tight text-foreground">
              Autonomous Fraud
              <br />
              <span className="text-primary">Intelligence</span>
            </h1>
            <p className="max-w-xs text-sm leading-relaxed text-muted-foreground">
              Enterprise-grade AI-powered retail fraud investigation platform. Real-time detection,
              autonomous agent workflows, and deep forensic analytics.
            </p>
          </div>

          <div className="space-y-3">
            {[
              "Multi-agent fraud investigation pipelines",
              "Real-time transaction risk scoring",
              "Automated case management & audit trails",
            ].map((feature) => (
              <div key={feature} className="flex items-center gap-2.5 text-sm text-muted-foreground">
                <div className="h-1 w-1 rounded-full bg-primary" />
                {feature}
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10">
          <p className="text-xs text-muted-foreground/60">
            © {new Date().getFullYear()} FraudShield Inc. Enterprise Edition.
          </p>
        </div>
      </div>

      {/* Right panel — login form */}
      <div className="flex w-full items-center justify-center p-6 lg:w-1/2 lg:p-12">
        <div className="w-full max-w-sm space-y-8">
          {/* Mobile logo */}
          <div className="flex items-center gap-2.5 lg:hidden">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <ShieldCheck className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="text-lg font-semibold tracking-tight">FraudShield</span>
          </div>

          {/* Header */}
          <div className="space-y-1.5">
            <h2 className="text-2xl font-bold tracking-tight">Welcome back</h2>
            <p className="text-sm text-muted-foreground">
              Sign in using your corporate Google account to access the dashboard.
            </p>
          </div>

          {/* Success message for registered users */}
          {registered && (
            <div className="rounded-lg border border-green-500/20 bg-green-500/5 px-4 py-2.5 text-xs text-green-400">
              Account registered successfully. Please sign in below.
            </div>
          )}

          {/* Security notice */}
          <div className="flex items-start gap-3 rounded-lg border border-amber-500/20 bg-amber-500/5 px-4 py-3">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-500" />
            <p className="text-xs leading-relaxed text-amber-200/70">
              This system is for authorized personnel only. All access is logged and monitored.
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-2.5 text-xs text-red-400">
              {error}
            </div>
          )}

          {/* Google OAuth Login Button */}
          <div className="w-full flex justify-center py-4 border border-border/40 rounded-xl bg-sidebar/50 p-6 backdrop-blur-sm shadow-sm transition-all hover:border-border/80">
            <div className="space-y-4 w-full">
              <p className="text-xs text-center text-muted-foreground font-medium uppercase tracking-wider">
                Enterprise Authentication
              </p>
              <div className="flex justify-center w-full">
                <div id="google-signin-btn" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function LoginFormFallback() {
  return (
    <div className="relative flex min-h-screen w-full overflow-hidden bg-background">
      <div className="absolute inset-0 opacity-[0.03]" />
      <div className="relative hidden w-1/2 flex-col justify-between border-r border-border bg-sidebar p-12 lg:flex" />
      <div className="flex w-full items-center justify-center p-6 lg:w-1/2 lg:p-12">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<LoginFormFallback />}>
      <LoginForm />
    </Suspense>
  );
}
