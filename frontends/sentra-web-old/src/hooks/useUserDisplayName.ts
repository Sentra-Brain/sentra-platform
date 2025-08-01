// src/hooks/useUserDisplayName.ts
// Hook to get user display names by ID with caching
import { useState, useEffect, useCallback } from 'react';
import { userService } from '../services/userService';
import type { User } from '../models/user';
import { getSafeUserDisplayName } from '../utils/userUtils';

const userCache = new Map<string, User>();

export const useUserDisplayName = (userId?: string) => {
  const [displayName, setDisplayName] = useState<string | undefined>();
  const [loading, setLoading] = useState(false);

  const getUserDisplayName = useCallback((user: User): string => {
    return user.full_name || user.username || user.email;
  }, []);

  useEffect(() => {
    if (!userId) {
      setDisplayName(undefined);
      return;
    }

    // Check cache first
    const cachedUser = userCache.get(userId);
    if (cachedUser) {
      setDisplayName(getUserDisplayName(cachedUser));
      return;
    }

    // Load from API
    setLoading(true);
    userService.getUserById(userId)
      .then(user => {
        userCache.set(userId, user);
        setDisplayName(getUserDisplayName(user));
      })
      .catch(error => {
        console.error('Failed to load user:', error);
        setDisplayName(getSafeUserDisplayName(userId)); // Safe fallback
      })
      .finally(() => setLoading(false));
  }, [userId, getUserDisplayName]);

  return { displayName, loading };
};

// Utility function to get display name synchronously if already cached
export const getCachedUserDisplayName = (userId: string): string | undefined => {
  const cachedUser = userCache.get(userId);
  if (cachedUser) {
    return cachedUser.full_name || cachedUser.username || cachedUser.email;
  }
  return undefined;
};