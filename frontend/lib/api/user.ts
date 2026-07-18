import apiClient from "../api";

export interface UserAdminCreate {
  email: string;
  full_name: string;
  password?: string;
  role_names: string[];
}

export interface UserAdminUpdate {
  full_name?: string;
  password?: string;
  is_active?: boolean;
  role_names?: string[];
}

export const userApi = {
  /**
   * Retrieve paginated and filtered users list
   */
  list: async (params: any = {}, config?: any) => {
    const response = await apiClient.get("/api/v1/users/", { ...config, params });
    return response.data;
  },
  
  /**
   * Retrieve user profile details by ID
   */
  getById: async (id: string, config?: any) => {
    const response = await apiClient.get(`/api/v1/users/${id}`, config);
    return response.data;
  },
  
  /**
   * Create a new investigator user account
   */
  create: async (payload: UserAdminCreate, config?: any) => {
    const response = await apiClient.post("/api/v1/users/", payload, config);
    return response.data;
  },
  
  /**
   * Update details of an existing user account
   */
  update: async (id: string, payload: UserAdminUpdate, config?: any) => {
    const response = await apiClient.put(`/api/v1/users/${id}`, payload, config);
    return response.data;
  },
  
  /**
   * Delete or deactivate a user account by ID
   */
  delete: async (id: string, config?: any) => {
    const response = await apiClient.delete(`/api/v1/users/${id}`, config);
    return response.data;
  }
};
export default userApi;
