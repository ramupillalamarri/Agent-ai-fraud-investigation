"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Cpu,
  Activity,
  Zap,
  TrendingUp,
  BarChart3,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAgents } from "@/hooks/useAgents";
import { LoadingSpinner, ErrorCard } from "@/components/shared/feedback";

export default function AgentsPage() {
  const router = useRouter();
  const { agents, loading, error, refetch } = useAgents();
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <LoadingSpinner message="Scanning agent registry..." />
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

  const activeCount = agents.filter((a) => a.enabled).length;
  const currentAgent = agents.find((a) => a.id === selectedAgentId) || agents[0];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-800">AI Agents Registry</h1>
          <p className="mt-1 text-sm text-slate-500">Manage framework pipelines and agent priorities</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            Refresh Status
          </Button>
          <Button size="sm" onClick={() => router.push("/dashboard")}>
            Dashboard
          </Button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { label: "Registered Agents", value: `${activeCount} / ${agents.length}`, icon: Cpu, color: "text-emerald-500", bg: "bg-emerald-50" },
          { label: "Active Pipelines", value: "3 Active", icon: BarChart3, color: "text-blue-500", bg: "bg-blue-50" },
          { label: "Framework Integration", value: "Connected", icon: TrendingUp, color: "text-indigo-500", bg: "bg-indigo-50" },
          { label: "API Latency Status", value: "Optimal", icon: Zap, color: "text-amber-500", bg: "bg-amber-50" },
        ].map((stat) => (
          <Card key={stat.label} className="overflow-hidden border border-slate-100 shadow-sm bg-white rounded-xl">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <span className="text-xs font-semibold text-slate-500">{stat.label}</span>
              <div className={`p-2 rounded-lg ${stat.bg}`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-800">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Grid Layout */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Agent Cards */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest">Available Framework Agents</h3>
          {agents.map((agent) => (
            <div 
              key={agent.id} 
              onClick={() => setSelectedAgentId(agent.id)}
              className={`p-5 rounded-xl border transition-all cursor-pointer ${
                (selectedAgentId === agent.id || (!selectedAgentId && agents[0]?.id === agent.id))
                  ? "bg-indigo-50/20 border-indigo-200 shadow-sm" 
                  : "bg-white border-slate-100 hover:border-slate-200 shadow-sm hover:shadow"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-indigo-50 text-indigo-700 rounded-lg">
                    <Cpu className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-800">{agent.name}</h4>
                    <span className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
                      Type: {agent.type}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-bold">
                    Priority: {agent.priority}
                  </span>
                  <span className="h-2 w-2 rounded-full bg-emerald-500" />
                  <span className="text-[10px] font-bold text-slate-500">Enabled</span>
                </div>
              </div>
              <p className="text-xs text-slate-500 mt-3 leading-relaxed">
                {agent.description}
              </p>
            </div>
          ))}
        </div>

        {/* Pipeline Details panel */}
        {currentAgent && (
          <Card className="bg-white border border-slate-100 shadow-sm rounded-xl p-5 space-y-4">
            <div>
              <h3 className="text-sm font-bold text-slate-800">{currentAgent.name}</h3>
              <p className="text-xs text-slate-400 mt-1">Registry identifier: {currentAgent.id}</p>
            </div>
            
            <div className="space-y-2 pt-2 border-t border-slate-100">
              <div className="flex justify-between text-xs py-1">
                <span className="text-slate-500 font-medium">Framework Priority</span>
                <span className="font-bold text-slate-700">{currentAgent.priority}</span>
              </div>
              <div className="flex justify-between text-xs py-1">
                <span className="text-slate-500 font-medium">Pipeline Placement</span>
                <span className="font-bold text-indigo-600">
                  {currentAgent.priority === 10 ? "First Priority" : currentAgent.priority === 20 ? "Second Priority" : "Third Priority"}
                </span>
              </div>
              <div className="flex justify-between text-xs py-1">
                <span className="text-slate-500 font-medium">System Status</span>
                <span className="font-bold text-emerald-600">Optimal</span>
              </div>
            </div>

            <div className="pt-2">
              <h4 className="text-xs font-bold text-slate-700 mb-2">Capabilities Scan</h4>
              <p className="text-xs text-slate-500 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100">
                This agent is automatically loaded during the orchestrator execution loop. It validates risk indicators asynchronously and returns structured evidence and recommendations.
              </p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
