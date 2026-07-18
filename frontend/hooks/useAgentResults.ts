import { useState, useEffect, useCallback } from "react";
import { investigationApi } from "../lib/api/investigation";
import { executeApiRequest } from "../lib/api-manager";

export function useAgentResults(id: string | null) {
  const [agentResults, setAgentResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAgentResults = useCallback(async (options?: { forceRefetch?: boolean }) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const ttl = options?.forceRefetch ? 0 : 30000; // 30s cache TTL
      const response = await executeApiRequest(
        (cfg) => investigationApi.getAgentResults(id, cfg),
        `inv-agent-results-${id}`,
        { ttl }
      );
      setAgentResults(response.agent_results || []);
    } catch (e: any) {
      if (e.name === "AbortError" || e.message === "canceled" || e.code === "ERR_CANCELED") return;
      setError(e.response?.data?.detail || e.message || "Failed to load agent results.");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchAgentResults();
  }, [fetchAgentResults]);

  return { agentResults, loading, error, refetch: () => fetchAgentResults({ forceRefetch: true }) };
}
