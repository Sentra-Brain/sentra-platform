import React, { useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { AuthContext } from './AuthContextInstance';
import { authService } from '../services/authService';
import type { User } from '../models/user';

export interface AuthContextType {
  user: User | null;
  setUser: React.Dispatch<React.SetStateAction<User | null>>;
  login: (email: string, password: string, remember?: boolean) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const getToken = () => localStorage.getItem('jwt') || sessionStorage.getItem('jwt') || null;

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    authService.getUser(token)
      .then(setUser)
      .catch((err) => {
        console.error('[AuthContext] getUser error', err);
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = async (email: string, password: string, remember = true) => {
    try {
      const token = await authService.login(email, password);
      if (remember) {
        localStorage.setItem('jwt', token);
        sessionStorage.removeItem('jwt');
      } else {
        sessionStorage.setItem('jwt', token);
        localStorage.removeItem('jwt');
      }

      const userData = await authService.getUser(token);
      setUser(userData);
      return true;
    } catch (err) {
      console.error('[AuthContext] login error', err);
      setUser(null);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('jwt');
    sessionStorage.removeItem('jwt');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, setUser, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
