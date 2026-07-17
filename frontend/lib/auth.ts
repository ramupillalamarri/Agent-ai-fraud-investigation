import type { UserProfile, Token } from "@/types/auth";

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const USER_PROFILE_KEY = "user_profile";

/**
 * Store authentication tokens in localStorage
 */
export function storeTokens(tokens: Token): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

/**
 * Retrieve the access token from localStorage
 */
export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

/**
 * Retrieve the refresh token from localStorage
 */
export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Store user profile in localStorage
 */
export function storeUserProfile(user: UserProfile): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(USER_PROFILE_KEY, JSON.stringify(user));
}

/**
 * Retrieve user profile from localStorage
 */
export function getUserProfile(): UserProfile | null {
  if (typeof window === "undefined") return null;
  const profile = localStorage.getItem(USER_PROFILE_KEY);
  if (!profile) return null;
  try {
    return JSON.parse(profile) as UserProfile;
  } catch {
    return null;
  }
}

/**
 * Clear all authentication data from localStorage
 */
export function clearAuth(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_PROFILE_KEY);
}

/**
 * Check if user is authenticated (has valid tokens)
 */
export function isAuthenticated(): boolean {
  return !!getAccessToken() && !!getRefreshToken();
}

/**
 * Get API base URL based on environment
 */
export function getApiBaseUrl(): string {
  if (typeof window === "undefined") return "";
  
  // In production, use relative path for same-origin API calls
  if (process.env.NODE_ENV === "production") {
    return "";
  }
  
  // In development, use the backend server
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}
