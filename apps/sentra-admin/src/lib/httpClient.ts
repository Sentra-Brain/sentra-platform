// src/lib/httpClient.ts
import axios from 'axios';
import type { ApiErrorResponse } from './errorTypes';

export type SentraError = {
  status: number;
  code: string;
  message: string;
  suggestion?: string;
  path?: string;
  requestId?: string;
};

type RequestHeaders = Record<string, string>;

type RequestConfig = {
  headers?: RequestHeaders;
  params?: Record<string, unknown>;
};

// Setup del cliente
const client = axios.create({
  baseURL: import.meta.env.VITE_SENTRA_API_URL || 'http://127.0.0.1:8100',
  timeout: 10000,
});

let runtimeToken: string | null = null;
let refreshTokenFunction: (() => Promise<boolean>) | null = null;

export function setAuthToken(token: string | null) {
  runtimeToken = token;
}

export function setRefreshTokenFunction(refreshFn: (() => Promise<boolean>) | null) {
  refreshTokenFunction = refreshFn;
}

client.interceptors.request.use((config) => {
  const token = runtimeToken ?? localStorage.getItem('jwt') ?? sessionStorage.getItem('jwt');
  if (token && config.headers) {
    config.headers.set?.('Authorization', `Bearer ${token}`);
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const data = error?.response?.data as ApiErrorResponse | undefined;
    const originalRequest = error.config;

    const detail = data?.detail?.error;

    const mapped: SentraError = {
      status: data?.detail?.statusCode || error?.response?.status || 500,
      code: detail?.code || 'UNKNOWN_ERROR',
      message: detail?.message || 'Unexpected error',
      suggestion: detail?.suggestion,
      path: detail?.path,
      requestId: detail?.requestId,
    };

    // Handle 401 errors with automatic token refresh
    if (
      mapped.status === 401 &&
      ['INVALID_TOKEN', 'EXPIRED_TOKEN', 'TOKEN_REVOKED'].includes(mapped.code) &&
      refreshTokenFunction &&
      !originalRequest._retried
    ) {
      console.log('[HTTP Client] Attempting token refresh due to 401 error');
      originalRequest._retried = true;

      try {
        const refreshed = await refreshTokenFunction();
        if (refreshed) {
          console.log('[HTTP Client] Token refreshed successfully, retrying request');
          // Update the authorization header with the new token
          const newToken = runtimeToken ?? localStorage.getItem('jwt') ?? sessionStorage.getItem('jwt');
          if (newToken && originalRequest.headers) {
            originalRequest.headers.set('Authorization', `Bearer ${newToken}`);
          }
          // Retry the original request
          return client(originalRequest);
        }
      } catch (refreshError) {
        console.error('[HTTP Client] Token refresh failed', refreshError);
      }
    }

    if (
      mapped.status === 401 &&
      ['INVALID_TOKEN', 'EXPIRED_TOKEN', 'TOKEN_REVOKED'].includes(mapped.code)
    ) {
      console.error('[HTTP Client] Unauthorized access', mapped);
      runtimeToken = null;
      localStorage.removeItem('jwt');
      sessionStorage.removeItem('jwt');
      localStorage.removeItem('refresh_token');
      sessionStorage.removeItem('refresh_token');
    } else {
      console.error('[HTTP Client] Error response', mapped);
    }

    return Promise.reject(mapped);
  }
);

export const httpClient = {
  get<TResponse>(url: string, config?: RequestConfig): Promise<TResponse> {
    return client.get(url, config).then((r) => r.data as TResponse);
  },

  post<TResponse, TRequest = unknown>(
    url: string,
    data?: TRequest,
    config?: RequestConfig
  ): Promise<TResponse> {
    return client.post(url, data, config).then((r) => r.data as TResponse);
  },

  put<TResponse, TRequest = unknown>(
    url: string,
    data?: TRequest,
    config?: RequestConfig
  ): Promise<TResponse> {
    return client.put(url, data, config).then((r) => r.data as TResponse);
  },

  del<TResponse>(url: string, config?: RequestConfig): Promise<TResponse> {
    return client.delete(url, config).then((r) => r.data as TResponse);
  },
};
