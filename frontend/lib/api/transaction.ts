import { investigationApi } from "./investigation";

export const transactionApi = {
  /**
   * Retrieves transactions by mapping them from active investigation logs
   */
  list: async (params: any = {}) => {
    const { investigations, total } = await investigationApi.list(params);
    
    const transactions = investigations.map((inv: any) => {
      // Safe fallback retrievals of nested transaction metadata
      const tx_data = inv.additional_metadata || {};
      return {
        id: inv.transaction_id,
        investigation_id: inv.id,
        customer_id: tx_data.customer_id || "cust_unknown",
        amount: tx_data.amount || 0.0,
        currency: tx_data.currency || "USD",
        status: inv.status,
        risk_score: inv.risk_score,
        timestamp: inv.started_at
      };
    });
    
    return { transactions, total };
  }
};
