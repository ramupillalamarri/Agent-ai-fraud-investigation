import { useState, useEffect, useCallback } from "react";
import { investigationApi } from "../lib/api/investigation";

export function useInvestigation(id: string | null) {
  const [investigation, setInvestigation] = useState<any>(null);
  const [report, setReport] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDetails = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const [invData, reportData, timelineData] = await Promise.all([
        investigationApi.getById(id),
        investigationApi.getReport(id),
        investigationApi.getTimeline(id)
      ]);
      setInvestigation(invData);
      setReport(reportData);
      setTimeline(timelineData.timeline || []);
    } catch (e: any) {
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
      await fetchDetails();
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || e.message || "Deletion failed.");
    }
  };

  return {
    investigation,
    report,
    timeline,
    loading,
    error,
    deleteDossier,
    refetch: fetchDetails
  };
}
