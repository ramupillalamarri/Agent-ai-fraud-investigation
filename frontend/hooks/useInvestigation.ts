import { useState, useEffect, useCallback } from "react";
import { investigationApi } from "../lib/api/investigation";
import { executeApiRequest, clearApiCache } from "../lib/api-manager";

export function useInvestigation(id: string | null) {
  const [investigation, setInvestigation] = useState<any>(null);
  const [report, setReport] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDetails = useCallback(async (options?: { forceRefetch?: boolean }) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const ttl = options?.forceRefetch ? 0 : 30000; // 30s cache TTL unless forced
      
      const [invData, reportData, timelineData] = await Promise.all([
        executeApiRequest(
          (cfg) => investigationApi.getById(id, cfg),
          `inv-${id}`,
          { ttl }
        ),
        executeApiRequest(
          (cfg) => investigationApi.getReport(id, cfg),
          `inv-report-${id}`,
          { ttl }
        ),
        executeApiRequest(
          (cfg) => investigationApi.getTimeline(id, cfg),
          `inv-timeline-${id}`,
          { ttl }
        ),
      ]);
      setInvestigation(invData);
      setReport(reportData);
      setTimeline(timelineData.timeline || []);
    } catch (e: any) {
      if (e.name === "AbortError" || e.message === "canceled" || e.code === "ERR_CANCELED") {
        // Ignore aborted requests
        return;
      }
      setError(e.response?.data?.detail || e.message || "Failed to load investigation details.");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchDetails();
  }, [fetchDetails]);

  const deleteDossier = async () => {
    if (!id) return;
    try {
      await investigationApi.delete(id);
      clearApiCache(`inv-${id}`);
      clearApiCache(`inv-report-${id}`);
      clearApiCache(`inv-timeline-${id}`);
      clearApiCache("inv-list");
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || e.message || "Deletion failed.");
    }
  };

  const updateAttributes = async (payload: { status?: string; priority?: string; assigned_to?: string }) => {
    if (!id) return;
    try {
      const updated = await investigationApi.patch(id, payload);
      setInvestigation(updated);
      
      clearApiCache(`inv-${id}`);
      clearApiCache(`inv-report-${id}`);
      clearApiCache(`inv-timeline-${id}`);
      clearApiCache("inv-list");
      
      await fetchDetails({ forceRefetch: true });
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || e.message || "Update failed.");
    }
  };

  return {
    investigation,
    report,
    timeline,
    loading,
    error,
    deleteDossier,
    updateAttributes,
    refetch: () => fetchDetails({ forceRefetch: true })
  };
}
