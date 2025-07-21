import axios from 'axios';
import type { User } from '../models/user';
import type { SignupResponse } from '../models/signupResponse';

axios.defaults.baseURL = import.meta.env.VITE_SENTRA_API_URL || 'http://127.0.0.1:8100';

export const userService = {
  async getCurrentUser(token: string): Promise<User> {
    const res = await axios.get<User>('/users/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },

  async signup(data: {
    username: string;
    email: string;
    full_name: string;
    password: string;
  }): Promise<SignupResponse> {
    const res = await axios.post<SignupResponse>('/users/signup', data);
    return res.data;
  },
};
