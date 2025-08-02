import axios from 'axios'
import { store } from '../../store'
import { logout, loginSuccess } from '../../features/auth/authSlice'
import { authService } from '../../features/auth/authService'
import { toast } from 'react-toastify'
import { tokenStorage } from '@shared/utils/tokenStorage'
import type { SentraApiError } from '../models/apiError'
import { showApiErrorToast } from '../utils/showApiErrorToast'

// Base Axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8100',
  headers: {
    'Content-Type': 'application/json',
  },
})

// === Refresh Token Control ===
let isRefreshing = false
let requestQueue: Array<{
  resolve: (token: string) => void
  reject: (err: unknown) => void
}> = []

const processQueue = (error: unknown, token: string | null) => {
  requestQueue.forEach(({ resolve, reject }) => {
    if (token) resolve(token)
    else reject(error)
  })
  requestQueue = []
}

// === Request Interceptor ===
apiClient.interceptors.request.use((config) => {
  const token = tokenStorage.getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// === Response Interceptor ===
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // === Handle token refresh ==
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = tokenStorage.getRefreshToken()
      if (!refreshToken) {
        store.dispatch(logout())
        window.location.href = '/login'
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          requestQueue.push({
            resolve: (token: string) => {
              originalRequest.headers['Authorization'] = `Bearer ${token}`
              resolve(apiClient(originalRequest))
            },
            reject,
          })
        })
      }

      isRefreshing = true

      try {
        const { access_token } = await authService.refresh(refreshToken)

        tokenStorage.setTokens(
          access_token,
          refreshToken,
          tokenStorage.isPersistent()
        )

        const { user, roles } = store.getState().auth
        store.dispatch(loginSuccess({ token: access_token, roles, user: user! }))
        processQueue(null, access_token)

        originalRequest.headers['Authorization'] = `Bearer ${access_token}`
        return apiClient(originalRequest)
      } catch (err) {
        processQueue(err, null)
        toast.error('Session expired. Please login again.')
        store.dispatch(logout())
        window.location.href = '/login'
        return Promise.reject(err)
      } finally {
        isRefreshing = false
      }
    }
    // === Handle other errors ===
    const { response } = error
    if (response && response.data && response.data.status === 'error') {
      const apiError = response.data as SentraApiError

      const message = apiError.error.message || 'Unexpected error occurred.'
      const requestId = apiError.error.requestId
      
      showApiErrorToast(apiError)

      // Optional: log error details to Sentry or console
      console.error('API Error:', {
        message,
        details: apiError.error.details,
        path: apiError.error.path,
        requestId,
      })
    }

    return Promise.reject(error)
  }
)

export default apiClient