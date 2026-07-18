import { useState, useEffect, useCallback } from "react";
import { dashboardApi } from "../lib/api/dashboard";
import { executeApiRequest } from "../lib/api-manager";

export function useAnalytics() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = useCallback(async (options?: { forceRefetch?: boolean }) => {
    setLoading(true);
    setError(null);
    try {
      const ttl = options?.forceRefetch ? 0 : 30000; // 30s cache TTL
      const result = await executeApiRequest(
        (cfg) => dashboardApi.getAnalytics(cfg),
        "analytics-summary",
        { ttl }
      );
      setData(result);
    } catch (e: any) {
      if (e.name === "AbortError" || e.message === "canceled" || e.code === "ERR_CANCELED") return;
      setError(e.response?.data?.detail || e.message || "Failed to load analytics.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  return {
    data,
    loading,
    error,
    refetch: () => fetchAnalytics({ forceRefetch: true })
  };
}
