// src/services/publicService.ts
import { httpClient } from '../lib/httpClient';
import type { PublicSettings } from '../models/publicSettings';

export const publicService = {
  getSettings(): Promise<PublicSettings> {
    return httpClient.get<PublicSettings>('/public/settings');
  },
};
