/** JWT token response from the authentication API */
export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

/** User credentials for login */
export interface LoginCredentials {
  email: string;
  password: string;
}

/** User data for registration */
export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
}

/** Role response from the API */
export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
}

/** User response from the API */
export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  roles: Role[];
}

/** Stored user profile in localStorage */
export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  roles: string[];
}

/** Authentication state */
export interface AuthState {
  user: UserProfile | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}
