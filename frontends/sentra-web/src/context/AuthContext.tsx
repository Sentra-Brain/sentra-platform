import { useState, useEffect, useRef, useCallback } from 'react';
import type { ReactNode } from 'react';
import { authService } from '../services/authService';
import { userService } from '../services/userService';
import { AuthContext } from './AuthContextInstance';
import type { User } from '../models/user';
import { setAuthToken, setRefreshTokenFunction } from '../lib/httpClient';
import { isTokenExpired } from '../utils/tokenUtils';
import { requestCache } from '../lib/requestCache';

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const refreshPromiseRef = useRef<Promise<boolean> | null>(null);
  const initializedRef = useRef(false);

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

  // Cached getCurrentUser function that prevents duplicate calls
  const getCurrentUserCached = useCallback(async (token: string): Promise<User> => {
    return requestCache.get(
      `users/me/${token.substring(0, 10)}`, // Use token prefix as cache key
      () => userService.getCurrentUser(token),
      { ttl: 10 * 60 * 1000 } // Cache for 10 minutes
    );
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
    // Only initialize once to prevent duplicate API calls on route changes
    if (initializedRef.current) {
      return;
    }
    
    initializedRef.current = true;
    console.log('[AuthContext] Initializing authentication state');

    const token = getToken();
    
    setAuthToken(token);
    setRefreshTokenFunction(refreshAccessToken);
    
    if (!token) {
      console.log('[AuthContext] No token found, user not authenticated');
      setUser(null);
      setLoading(false);
      return;
    }

    // Fetch user data with caching to prevent duplicate calls
    getCurrentUserCached(token)
      .then(userData => {
        console.log('[AuthContext] User authenticated successfully');
        setUser(userData);
      })
      .catch(err => {
        console.error('[AuthContext] Failed to get current user:', err);
        // Token might be invalid, clear it
        clearTokens();
        setAuthToken(null);
        setUser(null);
        requestCache.invalidate('users/me');
      })
      .finally(() => setLoading(false));
  }, []); // Empty dependencies to run only once

  const login = async (email: string, password: string, remember = true) => {
    try {
      console.log('[AuthContext] Attempting login');
      const response = await authService.login(email, password);

      console.log('[AuthContext] Login successful, storing tokens');
      storeTokens(response.access_token, response.refresh_token, remember);
      setAuthToken(response.access_token);

      // Use cached getCurrentUser to prevent duplicate calls
      const userData = await getCurrentUserCached(response.access_token);
      setUser(userData);
      setLoading(false);

      return true;
    } catch (err) {
      console.error('[AuthContext] Login failed:', err);
      setUser(null);
      setLoading(false);
      return false;
    }
  };

  const logout = () => {
    console.log('[AuthContext] Logging out');
    clearTokens();
    setAuthToken(null);
    setRefreshTokenFunction(null);
    setUser(null);
    // Clear all cached requests on logout
    requestCache.clear();
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