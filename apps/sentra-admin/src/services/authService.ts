import axios from 'axios';

axios.defaults.baseURL = import.meta.env.VITE_SENTRA_API_URL || 'http://127.0.0.1:8100';

export const authService = {
  async login(email: string, password: string): Promise<string> {
    const params = new URLSearchParams();
    params.append('grant_type', 'password');
    params.append('username', email);
    params.append('password', password);

    const res = await axios.post<{ access_token: string }>('/auth/token', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    return res.data.access_token;
  }
};
