// src/services/authService.ts

import axios from 'axios'

const API_BASE = import.meta.env.VITE_SENTRA_API_URL || 'http://127.0.0.1:8100'

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface RefreshResponse {
  access_token: string
  token_type: string
}

export const authService = {
  login(email: string, password: string): Promise<LoginResponse> {
    const body = new URLSearchParams()
    body.append('grant_type', 'password')
    body.append('username', email)
    body.append('password', password)

    return axios
      .post<LoginResponse>(`${API_BASE}/auth/token`, body, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })
      .then((res) => res.data)
  },

  refresh(refreshToken: string): Promise<RefreshResponse> {
    return axios
      .post<RefreshResponse>(`${API_BASE}/auth/refresh`, { refresh_token: refreshToken }, {
        headers: {
          'Content-Type': 'application/json',
        },
      })
      .then((res) => res.data)
  },
}
