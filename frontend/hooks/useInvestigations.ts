import { useState, useEffect, useCallback } from "react";
import { investigationApi, InvestigationFilterParams } from "../lib/api/investigation";
import { executeApiRequest } from "../lib/api-manager";

export function useInvestigations(initialParams: InvestigationFilterParams = {}) {
  const [investigations, setInvestigations] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [params, setParams] = useState<InvestigationFilterParams>(initialParams);

  const fetchInvestigations = useCallback(async (options?: { forceRefetch?: boolean }) => {
    setLoading(true);
    setError(null);
    try {
      const ttl = options?.forceRefetch ? 0 : 15000; // 15s cache TTL
      const cacheKey = `inv-list-${JSON.stringify(params)}`;
      
      const data = await executeApiRequest(
        (cfg) => investigationApi.list(params, cfg),
        cacheKey,
        { ttl }
      );
      setInvestigations(data.investigations || []);
      setTotal(data.total || 0);
    } catch (e: any) {
      if (e.name === "AbortError" || e.message === "canceled" || e.code === "ERR_CANCELED") return;
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
    refetch: () => fetchInvestigations({ forceRefetch: true })
  };
}
