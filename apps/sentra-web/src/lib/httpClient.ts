// src/lib/httpClient.ts
import axios from 'axios';

export type SentraError = {
  status: number;
  code: string;
  message: string;
  suggestion?: string;
  path?: string;
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

// Inyección de token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) {
    config.headers.set?.('Authorization', `Bearer ${token}`);
  }

  return config;
});

// Mapeo de errores
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const r = error?.response;
    const d = r?.data ?? {};

    const err: SentraError = {
      status: r?.status ?? 500,
      code: typeof d.code === 'string' ? d.code : 'UNKNOWN_ERROR',
      message: typeof d.message === 'string' ? d.message : 'Unexpected error',
      suggestion: typeof d.suggestion === 'string' ? d.suggestion : undefined,
      path: typeof d.path === 'string' ? d.path : r?.config?.url,
    };

    return Promise.reject(err);
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
