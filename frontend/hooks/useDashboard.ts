import { useState, useEffect, useCallback } from "react";
import { dashboardApi } from "../lib/api/dashboard";

export function useDashboard() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await dashboardApi.getSummary();
      setMetrics(data);
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || "Failed to load dashboard metrics.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  return {
    metrics,
    loading,
    error,
    refetch: fetchSummary
  };
}
