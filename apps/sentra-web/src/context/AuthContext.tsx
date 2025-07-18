import { useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { authService } from '../services/authService';
import { userService } from '../services/userService';
import { AuthContext } from './AuthContextInstance';
import type { User } from '../models/user';

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

    userService.getCurrentUser(token)
      .then(setUser)
      .catch(err => {
        console.error('[AuthContext] getCurrentUser error', err);
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

      const user = await userService.getCurrentUser(token);
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
