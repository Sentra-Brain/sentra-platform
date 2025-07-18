// src/services/authService.ts
// This file contains the authentication service that handles login and user retrieval
import axios from 'axios';
import type { User } from '../models/user';

axios.defaults.baseURL = import.meta.env.VITE_SENTRA_API_URL || 'http://127.0.0.1:8100';

export const authService = {
  async login(email: string, password: string) {
    const params = new URLSearchParams();
    params.append('grant_type', 'password');
    params.append('username', email);
    params.append('password', password);

    const res = await axios.post<{ access_token: string }>('/auth/token', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return res.data.access_token;
  },

  async getUser(token: string): Promise<User> {
    const res = await axios.get<User>('/users/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },
};
