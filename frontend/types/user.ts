// User type definitions
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface UserSession {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface SignupRequest {
  email: string;
  password: string;
  name: string;
}

export interface SigninRequest {
  email: string;
  password: string;
}

export interface AuthResponse extends User {
  // Backend returns user object directly, not wrapped
}
