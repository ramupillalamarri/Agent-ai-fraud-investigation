import { useState, useEffect, useCallback } from "react";
import { userApi } from "../lib/api/user";
import { executeApiRequest } from "../lib/api-manager";

export function useUsers(initialParams: any = {}) {
  const [users, setUsers] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [params, setParams] = useState<any>(initialParams);

  const fetchUsers = useCallback(async (options?: { forceRefetch?: boolean }) => {
    setLoading(true);
    setError(null);
    try {
      const ttl = options?.forceRefetch ? 0 : 10000; // 10s cache
      const cacheKey = `user-list-${JSON.stringify(params)}`;
      
      const data = await executeApiRequest(
        (cfg) => userApi.list({ ...params, limit: params.limit || 100, skip: params.skip || 0 }, cfg),
        cacheKey,
        { ttl }
      );
      setUsers(data.users || []);
      setTotal(data.total || 0);
    } catch (e: any) {
      if (e.name === "AbortError" || e.message === "canceled" || e.code === "ERR_CANCELED") return;
      setError(e.response?.data?.detail || e.message || "Failed to load users.");
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const updateFilters = (newParams: any) => {
    setParams((prev: any) => ({ ...prev, ...newParams }));
  };

  return {
    users,
    total,
    loading,
    error,
    params,
    updateFilters,
    refetch: () => fetchUsers({ forceRefetch: true })
  };
}
