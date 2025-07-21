export type ApiErrorPayload = {
  code: string;
  message: string;
  path: string;
  suggestion?: string;
  requestId?: string;
  timestamp?: string;
  details?: unknown;
};

export type ApiErrorDetail = {
  status: 'error';
  statusCode: number;
  error: ApiErrorPayload;
  requestId: string;
  documentation_url?: string;
};

export type ApiErrorResponse = {
  detail: ApiErrorDetail;
};
