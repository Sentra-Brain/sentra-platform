import axios from 'axios'
import { store } from '../store'
import { logout, loginSuccess } from '../features/auth/authSlice'
import { authService } from './authService'
import { toast } from 'react-toastify'
import { tokenStorage } from '../utils/tokenStorage'

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

    return Promise.reject(error)
  }
)

export default apiClient