import { useState, useEffect, useCallback } from "react";
import { investigationApi, InvestigationFilterParams } from "../lib/api/investigation";

export function useInvestigations(initialParams: InvestigationFilterParams = {}) {
  const [investigations, setInvestigations] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [params, setParams] = useState<InvestigationFilterParams>(initialParams);

  const fetchInvestigations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await investigationApi.list(params);
      setInvestigations(data.investigations || []);
      setTotal(data.total || 0);
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || "Failed to load investigations.");
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    fetchInvestigations();
  }, [fetchInvestigations]);

  const updateFilters = (newParams: Partial<InvestigationFilterParams>) => {
    setParams(prev => ({ ...prev, ...newParams, page: newParams.page ?? 1 }));
  };

  return {
    investigations,
    total,
    loading,
    error,
    params,
    updateFilters,
    refetch: fetchInvestigations
  };
}
