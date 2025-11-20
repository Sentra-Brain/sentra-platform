// src/models/apiError.ts

export interface SentraApiError {
  status: 'error'
  statusCode: number
  error: {
    code: string
    message: string
    details?: string
    suggestion?: string
    timestamp?: string
    path?: string
    requestId?: string
  }
  requestId?: string
  documentation_url?: string
}
