// src/services/userService.ts
import apiClient from '@shared/api/apiClient'
import type { User } from './types/user'
import type { SignupRequest } from './types/signupRequest'
import type { SignupResponse } from './types/signupResponse'


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
