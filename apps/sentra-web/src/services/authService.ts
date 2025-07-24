import axios from 'axios';

export const authService = {
  login(email: string, password: string): Promise<string> {
    const body = new URLSearchParams();
    body.append('grant_type', 'password');
    body.append('username', email);
    body.append('password', password);

    // Bypass httpClient to avoid token interception in this concrete case
    // since this is a direct login request.
    return axios
      .post('/auth/token', body, {
        baseURL: import.meta.env.VITE_SENTRA_API_URL || 'http://127.0.0.1:8100',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      .then((res) => res.data.access_token);
  },
};
