// src/context/AuthContext.tsx
import { useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { authService } from '../services/authService';
import { userService } from '../services/userService';
import { AuthContext } from './AuthContextInstance';
import type { User } from '../models/user';
import { decodeJwt } from '../utils/jwt';

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

    userService
      .getCurrentUser(token)
      .then(setUser)
      .catch((err) => {
        console.error('[AuthContext] getCurrentUser error', err);
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = async (email: string, password: string, remember = true) => {
    try {
      const token = await authService.login(email, password);

      // Decode JWT to check role first
      const decoded = decodeJwt(token);
      const rawRoles = decoded?.roles;
      const roles: string[] = typeof rawRoles === 'string'
        ? rawRoles.split(',').map(r => r.trim())
        : [];
      
      if (!roles.includes('superadmin')) {
        throw new Error('Only superadmins can access this panel');
      }

      if (remember) {
        localStorage.setItem('jwt', token);
        sessionStorage.removeItem('jwt');
      } else {
        sessionStorage.setItem('jwt', token);
        localStorage.removeItem('jwt');
      }

      const user = await userService.getCurrentUser(token);
      if (!user.roles?.includes('superadmin')) {
        console.warn('[AuthContext] Access denied: not superadmin');
        throw new Error('Only superadmins can access this panel');
      }
      setUser(user);

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
