// src/services/userService.ts
import apiClient from './apiClient'
import type { User } from '../models/user'
import type { SignupResponse } from '../models/signupResponse'
import type { SignupRequest } from '../models/signupRequest'

export const userService = {
  // Gets the current user from the API
  getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/users/me').then(res => res.data)
  },

  getUserById(userId: string): Promise<User> {
    return apiClient.get<User>(`/users/${userId}`).then(res => res.data)
  },

  signup(data: SignupRequest): Promise<SignupResponse> {
    return apiClient.post<SignupResponse>('/users/signup', data).then(res => res.data)
  },
}
