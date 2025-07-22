// src/services/publicService.ts
// This file defines the public service for fetching public settings
import { httpClient } from '../lib/httpClient';
import type { PublicSettings } from '../models/publicSettings';

export const publicService = {
  getSettings(): Promise<PublicSettings> {
    return httpClient.get<PublicSettings>('/public/settings');
  },
};
