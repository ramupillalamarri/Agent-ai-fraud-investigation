import { useState, useEffect, useCallback } from "react";
import { investigationApi } from "../lib/api/investigation";
import { executeApiRequest } from "../lib/api-manager";

export function useTimeline(id: string | null) {
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTimeline = useCallback(async (options?: { forceRefetch?: boolean }) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const ttl = options?.forceRefetch ? 0 : 30000; // 30s cache TTL
      const response = await executeApiRequest(
        (cfg) => investigationApi.getTimeline(id, cfg),
        `inv-timeline-${id}`,
        { ttl }
      );
      setTimeline(response.timeline || []);
    } catch (e: any) {
      if (e.name === "AbortError" || e.message === "canceled" || e.code === "ERR_CANCELED") return;
      setError(e.response?.data?.detail || e.message || "Failed to load timeline events.");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchTimeline();
  }, [fetchTimeline]);

  return { timeline, loading, error, refetch: () => fetchTimeline({ forceRefetch: true }) };
}
