'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { api, AuthenticationError } from '@/lib/api';
import type { User, UserSession } from '@/types/user';

interface AuthContextType extends UserSession {
  signin: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string) => Promise<void>;
  signout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      console.log('[AUTH] Checking authentication...');
      const user = await api.auth.me();
      console.log('[AUTH] User authenticated:', user);
      setUser(user);
    } catch (error) {
      // Not authenticated or session expired
      console.log('[AUTH] Authentication check failed:', error);
      setUser(null);
    } finally {
      console.log('[AUTH] Setting isLoading to false');
      setIsLoading(false);
    }
  };

  // [Task]: AUTH-FIX-002
  // [From]: Cross-origin cookie issue - update state without returning user
  const signin = async (email: string, password: string) => {
    console.log('[AUTH] Signing in...');
    const user = await api.auth.signin({ email, password });
    console.log('[AUTH] Signin successful, user:', user);
    // Update user state immediately after successful signin
    // The backend has set the httpOnly cookie, and we have the user data
    setUser(user);
    console.log('[AUTH] User state updated');
  };

  const signup = async (email: string, password: string, name: string) => {
    console.log('[AUTH] Signing up...');
    const user = await api.auth.signup({ email, password, name });
    console.log('[AUTH] Signup successful, user:', user);
    // Update user state immediately after successful signup
    // The backend has set the httpOnly cookie, and we have the user data
    setUser(user);
    console.log('[AUTH] User state updated');
  };

  const signout = async () => {
    await api.auth.signout();
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const user = await api.auth.me();
      setUser(user);
    } catch (error) {
      setUser(null);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    signin,
    signup,
    signout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
