import apiClient from "../api";

export interface InvestigationFilterParams {
  status?: string;
  priority?: string;
  min_risk_score?: number;
  max_risk_score?: number;
  min_fraud_prob?: number;
  max_fraud_prob?: number;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_desc?: boolean;
}

export const investigationApi = {
  /**
   * Run a real-time investigation for a transaction payload
   */
  run: async (payload: any) => {
    const response = await apiClient.post("/api/v1/investigations/run", payload);
    return response.data;
  },
  
  /**
   * Retrieve complete investigation dossier details
   */
  getById: async (id: string) => {
    const response = await apiClient.get(`/api/v1/investigations/${id}`);
    return response.data;
  },
  
  /**
   * Retrieve paginated and filtered investigations list
   */
  list: async (params: InvestigationFilterParams = {}) => {
    const response = await apiClient.get("/api/v1/investigations", { params });
    return response.data;
  },
  
  /**
   * Retrieve timeline log events for an investigation
   */
  getTimeline: async (id: string) => {
    const response = await apiClient.get(`/api/v1/investigations/${id}/timeline`);
    return response.data;
  },
  
  /**
   * Retrieve compiled investigation report details
   */
  getReport: async (id: string) => {
    const response = await apiClient.get(`/api/v1/investigations/${id}/report`);
    return response.data;
  },
  
  /**
   * Soft deletes an investigation dossier
   */
  delete: async (id: string) => {
    const response = await apiClient.delete(`/api/v1/investigations/${id}`);
    return response.data;
  }
};
