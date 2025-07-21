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


client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
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
