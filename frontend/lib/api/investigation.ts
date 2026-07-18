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
  run: async (payload: any, config?: any) => {
    const response = await apiClient.post("/api/v1/investigations/run", payload, config);
    return response.data;
  },
  
  /**
   * Retrieve complete investigation dossier details
   */
  getById: async (id: string, config?: any) => {
    const response = await apiClient.get(`/api/v1/investigations/${id}`, config);
    return response.data;
  },
  
  /**
   * Retrieve paginated and filtered investigations list
   */
  list: async (params: InvestigationFilterParams = {}, config?: any) => {
    const response = await apiClient.get("/api/v1/investigations", { ...config, params });
    return response.data;
  },
  
  /**
   * Retrieve timeline log events for an investigation
   */
  getTimeline: async (id: string, config?: any) => {
    const response = await apiClient.get(`/api/v1/investigations/${id}/timeline`, config);
    return response.data;
  },
  
  /**
   * Retrieve compiled investigation report details
   */
  getReport: async (id: string, config?: any) => {
    const response = await apiClient.get(`/api/v1/investigations/${id}/report`, config);
    return response.data;
  },
  
  /**
   * Soft deletes an investigation dossier
   */
  delete: async (id: string, config?: any) => {
    const response = await apiClient.delete(`/api/v1/investigations/${id}`, config);
    return response.data;
  },
  
  /**
   * Retrieve evidence list for an investigation
   */
  getEvidence: async (id: string, config?: any) => {
    const response = await apiClient.get(`/api/v1/investigations/${id}/evidence`, config);
    return response.data;
  },
  
  /**
   * Retrieve recommendations list for an investigation
   */
  getRecommendations: async (id: string, config?: any) => {
    const response = await apiClient.get(`/api/v1/investigations/${id}/recommendations`, config);
    return response.data;
  },
  
  /**
   * Retrieve individual agent results for an investigation
   */
  getAgentResults: async (id: string, config?: any) => {
    const response = await apiClient.get(`/api/v1/investigations/${id}/agent-results`, config);
    return response.data;
  },
  
  /**
   * Partially updates investigation status, priority, or assignee attributes
   */
  patch: async (id: string, payload: { status?: string; priority?: string; assigned_to?: string }, config?: any) => {
    const response = await apiClient.patch(`/api/v1/investigations/${id}`, payload, config);
    return response.data;
  }
};
