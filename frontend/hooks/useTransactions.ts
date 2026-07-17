import { useState, useEffect, useCallback } from "react";
import { transactionApi } from "../lib/api/transaction";

export function useTransactions(initialParams: any = {}) {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [params, setParams] = useState<any>(initialParams);

  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await transactionApi.list(params);
      setTransactions(data.transactions || []);
      setTotal(data.total || 0);
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || "Failed to load transactions.");
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  const updateFilters = (newParams: any) => {
    setParams((prev: any) => ({ ...prev, ...newParams, page: newParams.page ?? 1 }));
  };

  return {
    transactions,
    total,
    loading,
    error,
    params,
    updateFilters,
    refetch: fetchTransactions
  };
}
