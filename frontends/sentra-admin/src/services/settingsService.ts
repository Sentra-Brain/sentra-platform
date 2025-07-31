import axios from 'axios';

const baseURL = import.meta.env.VITE_SENTRA_API_URL || 'http://127.0.0.1:8100';

export const settingsService = {
  async getSettings(token: string) {
    const res = await axios.get(`${baseURL}/admin/settings`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return res.data; // { max_users: number }
  },

  async updateSettings(token: string, payload: { max_users: number }) {
    const res = await axios.put(`${baseURL}/admin/settings`, payload, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return res.data;
  }
};
