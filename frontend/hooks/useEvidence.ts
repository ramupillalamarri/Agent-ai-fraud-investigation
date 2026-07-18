import { useState, useEffect, useCallback } from "react";
import { investigationApi } from "../lib/api/investigation";
import { executeApiRequest } from "../lib/api-manager";

export function useEvidence(id: string | null) {
  const [evidence, setEvidence] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEvidence = useCallback(async (options?: { forceRefetch?: boolean }) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const ttl = options?.forceRefetch ? 0 : 30000; // 30s cache TTL
      const response = await executeApiRequest(
        (cfg) => investigationApi.getEvidence(id, cfg),
        `inv-evidence-${id}`,
        { ttl }
      );
      setEvidence(response.evidence || []);
    } catch (e: any) {
      if (e.name === "AbortError" || e.message === "canceled" || e.code === "ERR_CANCELED") return;
      setError(e.response?.data?.detail || e.message || "Failed to load evidence.");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchEvidence();
  }, [fetchEvidence]);

  return { evidence, loading, error, refetch: () => fetchEvidence({ forceRefetch: true }) };
}
