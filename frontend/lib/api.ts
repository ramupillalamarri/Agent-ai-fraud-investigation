import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from "axios";
import { getAccessToken, getRefreshToken, storeTokens, clearAuth, getApiBaseUrl, isDevMode } from "./auth";
import type { Token, LoginCredentials, RegisterData, User } from "@/types/auth";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Create configured axios instance
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

/**
 * Track if a token refresh is in progress
 */
let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

/**
 * Subscribe to token refresh
 */
function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback);
}

/**
 * Notify all subscribers about new token
 */
function onTokenRefreshed(token: string) {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
}

/**
 * Process queue if refresh fails
 */
function onRefreshFailed() {
  refreshSubscribers = [];
}

/**
 * API error response interface
 */
interface ApiErrorResponse {
  detail?: string;
  message?: string;
}

/**
 * Refresh access token using refresh token
 */
async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    clearAuth();
    return null;
  }

  try {
    const response = await axios.post<Token>(
      `${API_BASE_URL}/api/v1/auth/refresh`,
      { refresh_token: refreshToken },
      { headers: { "Content-Type": "application/json" } }
    );
    
    const { access_token, refresh_token } = response.data;
    storeTokens({ access_token, refresh_token, token_type: "bearer" });
    return access_token;
  } catch (error) {
    clearAuth();
    return null;
  }
}

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken() || (isDevMode() ? "dev-bypass-token" : null);
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle token refresh
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError<ApiErrorResponse>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isDevMode()) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // Wait for refresh to complete
        return new Promise((resolve, reject) => {
          subscribeTokenRefresh((token: string) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            resolve(apiClient(originalRequest));
          });
          onRefreshFailed();
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newToken = await refreshAccessToken();
        isRefreshing = false;

        if (newToken) {
          onTokenRefreshed(newToken);
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
          }
          return apiClient(originalRequest);
        } else {
          window.location.href = "/login";
          return Promise.reject(error);
        }
      } catch (refreshError) {
        isRefreshing = false;
        onRefreshFailed();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Authentication API calls
 */
export const authApi = {
  /**
   * Login with email and password
   */
  login: async (credentials: LoginCredentials): Promise<Token> => {
    const response = await apiClient.post<Token>("/api/v1/auth/login", credentials);
    return response.data;
  },

  /**
   * Login with Google OAuth token
   */
  loginWithGoogle: async (idToken: string): Promise<Token> => {
    const response = await apiClient.post<Token>("/api/v1/auth/google", {
      id_token: idToken,
    });
    return response.data;
  },

  /**
   * Register a new user
   */
  register: async (data: RegisterData): Promise<User> => {
    const response = await apiClient.post<User>("/api/v1/auth/register", data);
    return response.data;
  },

  /**
   * Refresh access token
   */
  refresh: async (refreshToken: string): Promise<Token> => {
    const response = await apiClient.post<Token>("/api/v1/auth/refresh", {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  /**
   * Logout and revoke refresh token
   */
  logout: async (refreshToken: string): Promise<void> => {
    try {
      await apiClient.post("/api/v1/auth/logout", {
        refresh_token: refreshToken,
      });
    } finally {
      clearAuth();
    }
  },

  /**
   * Get current user profile
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>("/api/v1/auth/me");
    return response.data;
  },
};

export { apiClient };
export default apiClient;
