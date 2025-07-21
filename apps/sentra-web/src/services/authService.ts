// src/services/authService.ts
import { httpClient } from '../lib/httpClient';

type AuthTokenResponse = {
  access_token: string;
};

export const authService = {
  login(email: string, password: string): Promise<string> {
    const body = new URLSearchParams();
    body.append('grant_type', 'password');
    body.append('username', email);
    body.append('password', password);

    return httpClient
      .post<AuthTokenResponse>('/auth/token', body, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })
      .then((res) => res.access_token);
  },
};
