// src/services/publicService.ts
import axios from 'axios';
import type { PublicSettings } from '../models/publicSettings';

axios.defaults.baseURL = import.meta.env.VITE_SENTRA_API_URL || 'http://127.0.0.1:8100';

export const publicService = {
  async getSettings(): Promise<PublicSettings> {
    const res = await axios.get<PublicSettings>('/public/settings');
    return res.data;
  }
};
