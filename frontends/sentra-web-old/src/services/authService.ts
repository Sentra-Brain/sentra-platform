import axios from 'axios';

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
  login(email: string, password: string): Promise<LoginResponse> {
    const body = new URLSearchParams();
    body.append('grant_type', 'password');
    body.append('username', email);
    body.append('password', password);

    // Bypass httpClient to avoid token interception in this concrete case
    // since this is a direct login request.
    return axios
      .post<LoginResponse>('/auth/token', body, {
        baseURL: import.meta.env.VITE_SENTRA_API_URL || 'http://127.0.0.1:8100',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      .then((res) => res.data);
  },

  refresh(refreshToken: string): Promise<RefreshResponse> {
    // Bypass httpClient to avoid token interception for refresh requests
    return axios
      .post<RefreshResponse>('/auth/refresh', { refresh_token: refreshToken }, {
        baseURL: import.meta.env.VITE_SENTRA_API_URL || 'http://127.0.0.1:8100',
        headers: { 'Content-Type': 'application/json' },
      })
      .then((res) => res.data);
  },
};
