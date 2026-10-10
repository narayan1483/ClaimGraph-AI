/**
 * ClaimGraph AI — Authentication Context & Provider.
 *
 * Manages JWT session state, user identity, and login/logout lifecycles.
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { authService } from '@/services/auth';
import type { LoginCredentials, RegisterPayload, UserDetail } from '@/types';

interface AuthContextType {
  user: UserDetail | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const DEFAULT_EXPLORER_USER: UserDetail = {
  id: 'usr-default-lead-investigator',
  email: 'investigator@claimgraph.ai',
  full_name: 'Narayan Prasad Maurya',
  role: 'INVESTIGATOR',
  is_active: true,
  is_verified: true,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserDetail | null>(DEFAULT_EXPLORER_USER);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize session from stored token
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setUser(DEFAULT_EXPLORER_USER);
        setIsLoading(false);
        return;
      }
      try {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
      } catch {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(DEFAULT_EXPLORER_USER);
      } finally {
        setIsLoading(false);
      }
    };
    initAuth();
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    setIsLoading(true);
    setError(null);
    try {
      const tokenData = await authService.login(credentials);
      localStorage.setItem('access_token', tokenData.access_token);
      localStorage.setItem('refresh_token', tokenData.refresh_token);
      
      if (tokenData.user) {
        setUser(tokenData.user);
      } else {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
      }
    } catch (err: unknown) {
      console.error('Auth login failure:', err);
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { error?: { message?: string } } } }).response?.data
              ?.error?.message || 'Authentication failed. Please check credentials.'
          : 'Authentication failed. Server unreachable.';
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    setIsLoading(true);
    setError(null);
    try {
      const tokenData = await authService.register(payload);
      localStorage.setItem('access_token', tokenData.access_token);
      localStorage.setItem('refresh_token', tokenData.refresh_token);

      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { error?: { message?: string } } } }).response?.data
              ?.error?.message || 'Registration failed.'
          : 'Registration failed. Server unreachable.';
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(DEFAULT_EXPLORER_USER);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        error,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
