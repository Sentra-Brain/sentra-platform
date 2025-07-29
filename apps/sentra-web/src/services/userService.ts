// src/services/userService.ts
import { httpClient } from '../lib/httpClient';
import type { User } from '../models/user';
import type { SignupResponse } from '../models/signupResponse';
import type { SignupRequest } from '../models/signupRequest';

export const userService = {
  // getCurrentUser(): Promise<User> {
  //   return httpClient.get<User>('/users/me');
  // },

  getCurrentUser(token: string): Promise<User> {
    return httpClient.get<User>('/users/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  getUserById(userId: string): Promise<User> {
    return httpClient.get<User>(`/users/${userId}`);
  },

  signup(data: SignupRequest): Promise<SignupResponse> {
    return httpClient.post<SignupResponse, SignupRequest>('/users/signup', data);
  },
};
