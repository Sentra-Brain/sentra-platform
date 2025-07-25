// src/services/authService.ts
import axios from 'axios';

axios.defaults.baseURL = import.meta.env.VITE_SENTRA_API_URL || 'http://127.0.0.1:8100';

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshResponse {
  access_token: string;
  token_type: string;
}

export const authService = {
  async login(email: string, password: string): Promise<LoginResponse> {
    const params = new URLSearchParams();
    params.append('grant_type', 'password');
    params.append('username', email);
    params.append('password', password);

    const res = await axios.post<LoginResponse>('/auth/token', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    return res.data;
  },

  async refresh(refreshToken: string): Promise<RefreshResponse> {
    const res = await axios.post<RefreshResponse>('/auth/refresh', { refresh_token: refreshToken }, {
      headers: { 'Content-Type': 'application/json' },
    });

    return res.data;
  }
};
