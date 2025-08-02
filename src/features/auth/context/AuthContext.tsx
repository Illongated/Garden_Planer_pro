import React, { createContext, useState, useEffect, useMemo } from 'react';
import { useAuthStore } from '../store/auth.store';
import api from '@/lib/api';
import { User, LoginCredentials, SignUpCredentials } from '@/types';
import LoadingSpinner from '@/components/loading-spinner';

interface AuthContextType {
  user: User | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  signup: (credentials: SignUpCredentials) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const { status, setStatus, setToken, accessToken, logout: logoutFromStore } = useAuthStore();

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        // Try to refresh the token on initial load
        const { data } = await api.post('/auth/refresh');
        setToken(data.access_token);

        const { data: userData } = await api.get('/auth/me');
        setUser(userData);
        setStatus('authenticated');
      } catch (error) {
        setStatus('unauthenticated');
        setToken(null);
        setUser(null);
      }
    };
    checkAuthStatus();
  }, [setToken, setStatus]);

  const login = async (credentials: LoginCredentials) => {
    const { data } = await api.post('/auth/login', credentials);
    setToken(data.access_token);

    const { data: userData } = await api.get('/auth/me');
    setUser(userData);
    setStatus('authenticated');
  };

  const signup = async (credentials: SignUpCredentials) => {
    await api.post('/auth/register', credentials);
    // After signup, the user still needs to verify their email,
    // so we don't log them in directly.
    // We can redirect them to a page that says "check your email".
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error("Logout failed", error);
    } finally {
      logoutFromStore();
      setUser(null);
    }
  };

  const isLoading = status === 'loading';
  const isAuthenticated = status === 'authenticated';

  const value = useMemo(() => ({
    user,
    login,
    signup,
    logout,
    isLoading,
    isAuthenticated,
  }), [user, isLoading, isAuthenticated]);

  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <LoadingSpinner className="h-10 w-10" />
      </div>
    );
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
