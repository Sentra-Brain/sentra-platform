// src/hooks/useSettings.ts
import { useEffect, useState } from 'react';
import { settingsService } from '../services/settingsService';
import type { SystemSettings } from '../models/systemSettings';

export function useSettings(token: string) {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;

    settingsService.getSettings(token)
      .then(setSettings)
      .catch(err => {
        console.error(err);
        setError('Failed to load settings');
      })
      .finally(() => setLoading(false));
  }, [token]);

  const save = async (updated: SystemSettings) => {
    const saved = await settingsService.updateSettings(token, updated);
    setSettings(saved);
  };

  return { settings, setSettings, save, loading, error };
}
