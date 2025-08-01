// src/services/apiClient.ts
import axios from 'axios'
import { store } from '../store'
import { logout } from '../features/auth/authSlice'
import { toast } from 'react-toastify'

// Base Axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8100',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: inject JWT token
apiClient.interceptors.request.use((config) => {
  const state = store.getState()
  const token = state.auth.token || localStorage.getItem('token')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

// Response interceptor: handle 401
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      toast.error('Session expired. Please login again.')
      store.dispatch(logout())
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Export helpers
export const get = apiClient.get
export const post = apiClient.post
export const put = apiClient.put
export const del = apiClient.delete
export default apiClient
