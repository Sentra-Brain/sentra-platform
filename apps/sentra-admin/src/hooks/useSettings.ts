import { useEffect, useState } from 'react';
import { settingsService } from '../services/settingsService';

export function useSettings(token: string) {
  const [maxUsers, setMaxUsers] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    settingsService.getSettings(token)
      .then(data => setMaxUsers(data.max_users))
      .catch(err => {
        console.error(err);
        setError('Failed to load settings');
      })
      .finally(() => setLoading(false));
  }, [token]);

  const save = async (newMax: number) => {
    await settingsService.updateSettings(token, { max_users: newMax });
    setMaxUsers(newMax);
  };

  return { maxUsers, setMaxUsers, save, loading, error };
}
