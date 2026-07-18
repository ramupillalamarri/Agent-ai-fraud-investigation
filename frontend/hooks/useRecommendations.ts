import { useState, useEffect, useCallback } from "react";
import { investigationApi } from "../lib/api/investigation";
import { executeApiRequest } from "../lib/api-manager";

export function useRecommendations(id: string | null) {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = useCallback(async (options?: { forceRefetch?: boolean }) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const ttl = options?.forceRefetch ? 0 : 30000; // 30s cache TTL
      const response = await executeApiRequest(
        (cfg) => investigationApi.getRecommendations(id, cfg),
        `inv-recommendations-${id}`,
        { ttl }
      );
      setRecommendations(response.recommendations || []);
    } catch (e: any) {
      if (e.name === "AbortError" || e.message === "canceled" || e.code === "ERR_CANCELED") return;
      setError(e.response?.data?.detail || e.message || "Failed to load recommendations.");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  return { recommendations, loading, error, refetch: () => fetchRecommendations({ forceRefetch: true }) };
}
