// src/lib/httpClient.ts
// This file defines the HTTP client for making API requests
// to the Sentra Brain API
import axios from 'axios';
import type { ApiErrorResponse } from './errorTypes';
import { notifyError } from './notify';

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

// Token runtime in memory
let runtimeToken: string | null = null;

export function setAuthToken(token: string | null) {
  runtimeToken = token;
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
  (error) => {
    const data = error?.response?.data as ApiErrorResponse | undefined;

    const detail = data?.detail?.error;

    const mapped: SentraError = {
      status: data?.detail?.statusCode || error?.response?.status || 500,
      code: detail?.code || 'UNKNOWN_ERROR',
      message: detail?.message || 'Unexpected error',
      suggestion: detail?.suggestion,
      path: detail?.path,
      requestId: detail?.requestId,
    };

    if (
      mapped.status === 401 &&
      ['INVALID_TOKEN', 'EXPIRED_TOKEN', 'TOKEN_REVOKED'].includes(mapped.code)
    ) {
      // Handle unauthorized access, e.g., redirect to login
      notifyError(`Unauthorized access: ${mapped.message}`);
      // Log the error for debugging
      console.error('[HTTP Client] Unauthorized access', mapped);
      // Optionally, you can clear the token here
      runtimeToken = null;
      localStorage.removeItem('jwt');
      sessionStorage.removeItem('jwt');
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
