"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api";
import {
  storeTokens,
  storeUserProfile,
  clearAuth,
  getAccessToken,
  getRefreshToken,
  getUserProfile,
} from "@/lib/auth";
import type { AuthState, UserProfile, LoginCredentials, RegisterData } from "@/types/auth";

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    user: null,
    accessToken: null,
    refreshToken: null,
    isLoading: true,
    isAuthenticated: false,
  });

  /**
   * Check authentication status on mount
   */
  const checkAuth = useCallback(() => {
    const accessToken = getAccessToken();
    const refreshToken = getRefreshToken();
    const userProfile = getUserProfile();

    if (accessToken && refreshToken) {
      setState({
        user: userProfile,
        accessToken,
        refreshToken,
        isLoading: false,
        isAuthenticated: true,
      });
    } else {
      setState({
        user: null,
        accessToken: null,
        refreshToken: null,
        isLoading: false,
        isAuthenticated: false,
      });
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  /**
   * Login user
   */
  const login = useCallback(async (credentials: LoginCredentials) => {
    setState((prev) => ({ ...prev, isLoading: true }));
    
    try {
      const tokens = await authApi.login(credentials);
      storeTokens(tokens);

      // Fetch user profile
      const user = await authApi.getCurrentUser();
      
      const userProfile: UserProfile = {
        id: user.id,
        email: user.email,
        full_name: user.full_name,
        is_active: user.is_active,
        roles: user.roles.map((r) => r.name),
      };
      
      storeUserProfile(userProfile);

      setState({
        user: userProfile,
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token,
        isLoading: false,
        isAuthenticated: true,
      });
    } catch (error) {
      setState((prev) => ({ ...prev, isLoading: false }));
      throw error;
    }
  }, []);

  /**
   * Register new user
   */
  const register = useCallback(async (data: RegisterData) => {
    setState((prev) => ({ ...prev, isLoading: true }));
    
    try {
      await authApi.register(data);
      setState((prev) => ({ ...prev, isLoading: false }));
    } catch (error) {
      setState((prev) => ({ ...prev, isLoading: false }));
      throw error;
    }
  }, []);

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    const refreshToken = getRefreshToken();
    
    try {
      if (refreshToken) {
        await authApi.logout(refreshToken);
      }
    } finally {
      clearAuth();
      setState({
        user: null,
        accessToken: null,
        refreshToken: null,
        isLoading: false,
        isAuthenticated: false,
      });
      router.push("/login");
    }
  }, [router]);

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to use auth context
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
