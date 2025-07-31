import { useState, useEffect, useRef, useCallback } from 'react';
import type { ReactNode } from 'react';
import { authService } from '../services/authService';
import { userService } from '../services/userService';
import { AuthContext } from './AuthContextInstance';
import type { User } from '../models/user';
import { setAuthToken, setRefreshTokenFunction } from '../lib/httpClient';
import { isTokenExpired } from '../utils/tokenUtils';

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const refreshPromiseRef = useRef<Promise<boolean> | null>(null);

  const getToken = () => localStorage.getItem('jwt') || sessionStorage.getItem('jwt') || null;
  const getRefreshToken = () => localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token') || null;

  const storeTokens = (accessToken: string, refreshToken: string, remember: boolean) => {
    if (remember) {
      localStorage.setItem('jwt', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      sessionStorage.removeItem('jwt');
      sessionStorage.removeItem('refresh_token');
    } else {
      sessionStorage.setItem('jwt', accessToken);
      sessionStorage.setItem('refresh_token', refreshToken);
      localStorage.removeItem('jwt');
      localStorage.removeItem('refresh_token');
    }
  };

  const clearTokens = () => {
    localStorage.removeItem('jwt');
    sessionStorage.removeItem('jwt');
    localStorage.removeItem('refresh_token');
    sessionStorage.removeItem('refresh_token');
  };

  const refreshAccessToken = useCallback(async (): Promise<boolean> => {
    // If there's already a refresh in progress, wait for it
    if (refreshPromiseRef.current) {
      return refreshPromiseRef.current;
    }

    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      console.warn('[AuthContext] No refresh token available');
      // Clear tokens directly to avoid circular dependency
      clearTokens();
      setAuthToken(null);
      setRefreshTokenFunction(null);
      setUser(null);
      return false;
    }

    // Create and store the refresh promise
    refreshPromiseRef.current = (async () => {
      try {
        console.log('[AuthContext] Refreshing access token');
        const response = await authService.refresh(refreshToken);
        
        // Determine if tokens are in localStorage or sessionStorage
        const inLocalStorage = localStorage.getItem('jwt') !== null;
        
        // Store the new access token in the same location as before
        if (inLocalStorage) {
          localStorage.setItem('jwt', response.access_token);
        } else {
          sessionStorage.setItem('jwt', response.access_token);
        }
        
        setAuthToken(response.access_token);
        console.log('[AuthContext] Access token refreshed successfully');
        return true;
      } catch (error) {
        console.error('[AuthContext] Token refresh failed:', error);
        // Clear tokens directly to avoid circular dependency
        clearTokens();
        setAuthToken(null);
        setRefreshTokenFunction(null);
        setUser(null);
        return false;
      } finally {
        refreshPromiseRef.current = null;
      }
    })();

    return refreshPromiseRef.current;
  }, []);

  const getValidAccessToken = async (): Promise<string | null> => {
    const token = getToken();
    if (!token) {
      return null;
    }

    // Check if token is expired or about to expire (within 2 minutes)
    if (isTokenExpired(token, 2)) {
      console.log('[AuthContext] Access token expired, attempting refresh');
      const refreshed = await refreshAccessToken();
      if (!refreshed) {
        return null;
      }
      return getToken();
    }

    return token;
  };

  useEffect(() => {
    const token = getToken();
    
    setAuthToken(token);
    setRefreshTokenFunction(refreshAccessToken);
    
    // Development mode: provide mock user when no backend is available
    if (import.meta.env.DEV && !token) {
      console.log('[AuthContext] Development mode: setting mock user');
      setUser({
        id: 'mock-user-id',
        email: 'demo@sentra.ai',
        full_name: 'Demo User',
        username: 'demo',
        disabled: false
      });
      setLoading(false);
      return;
    }
    
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    userService.getCurrentUser(token)
      .then(setUser)
      .catch(err => {
        console.error('[AuthContext] getCurrentUser error', err);
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, [refreshAccessToken]);

  const login = async (email: string, password: string, remember = true) => {
    try {
      const response = await authService.login(email, password);

      console.log('[AuthContext] login success', response);

      storeTokens(response.access_token, response.refresh_token, remember);
      setAuthToken(response.access_token);

      const user = await userService.getCurrentUser(response.access_token);
      setUser(user);

      return true;
    } catch (err) {
      console.error('[AuthContext] login error', err);
      setUser(null);
      return false;
    }
  };

  const logout = () => {
    clearTokens();
    setAuthToken(null);
    setRefreshTokenFunction(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      setUser, 
      login, 
      logout, 
      loading, 
      refreshAccessToken, 
      getValidAccessToken 
    }}>
      {children}
    </AuthContext.Provider>
  );
};