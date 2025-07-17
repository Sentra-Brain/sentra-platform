import React, { useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import axios from 'axios';

// Set axios base URL for all API requests
axios.defaults.baseURL = import.meta.env.VITE_SENTRA_API_URL || 'http://127.0.0.1:8100';
console.log('[AuthContext] axios baseURL:', axios.defaults.baseURL);
import { AuthContext } from './AuthContextInstance';

export interface User {
  id: string;
  username: string
  email: string;
  // Add other user fields as needed
}

export interface AuthContextType {
  user: User | null;
  setUser: React.Dispatch<React.SetStateAction<User | null>>;
  login: (email: string, password: string, remember?: boolean) => Promise<boolean>;
  logout: () => void;
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);

  // Helper to get token from storage
  const getToken = () => {
    return (
      localStorage.getItem('jwt') ||
      sessionStorage.getItem('jwt') ||
      null
    );
  };

  // Load user on mount
  useEffect(() => {
    const token = getToken();
    console.log('[AuthContext] useEffect: token', token);
    if (!token) {
      setUser(null);
      return;
    }
    axios
      .get<User>('/users/me', {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true,
      })
      .then((response) => {
        console.log('[AuthContext] /users/me success', response.data);
        setUser(response.data);
      })
      .catch((err) => {
        console.log('[AuthContext] /users/me error', err);
        setUser(null);
      });
  }, []);

  const login = async (email: string, password: string, remember = true) => {
    try {
      console.log('[AuthContext] login: authenticating', email);
      // Authenticate and get JWT
      const params = new URLSearchParams();
      params.append('grant_type', 'password');
      params.append('username', email);
      params.append('password', password);
      params.append('scope', '');
      params.append('client_id', '');
      params.append('client_secret', '');
      const authRes = await axios.post<{ access_token: string }>(
        '/auth/token',
        params,
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
      );
      const token = authRes.data.access_token;
      console.log('[AuthContext] login: received token', token);
      if (remember) {
        localStorage.setItem('jwt', token);
        sessionStorage.removeItem('jwt');
      } else {
        sessionStorage.setItem('jwt', token);
        localStorage.removeItem('jwt');
      }
      // Fetch user info
      const userRes = await axios.get<User>('/users/me', {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true,
      });
      console.log('[AuthContext] login: /users/me', userRes.data);
      setUser(userRes.data);
      return true;
    } catch (err) {
      console.log('[AuthContext] login error', err);
      setUser(null);
      return false;
    }
  };

  const logout = () => {
    console.log('[AuthContext] logout');
    localStorage.removeItem('jwt');
    sessionStorage.removeItem('jwt');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, setUser, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};


