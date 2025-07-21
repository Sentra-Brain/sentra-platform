// src/services/userService.ts
import axios from 'axios';
import type { User } from '../models/user';

axios.defaults.baseURL = import.meta.env.VITE_SENTRA_API_URL || 'http://127.0.0.1:8100';

export const userService = {
  async getCurrentUser(token: string): Promise<User> {
    const res = await axios.get<User>('/users/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },
};
