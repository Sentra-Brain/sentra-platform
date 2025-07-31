// src/services/userService.ts
import type { User } from '../models/user';

const BASE_URL = import.meta.env.VITE_SENTRA_API_URL || 'http://127.0.0.1:8100';

export const userService = {
  async getCurrentUser(token: string): Promise<User> {
    // For initial token validation, we still need to use the direct approach
    // because httpClient might trigger refresh loops during initialization
    const response = await fetch(`${BASE_URL}/users/me`, {
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      method: 'GET'
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch user');
    }
    
    return response.json();
  },
};
