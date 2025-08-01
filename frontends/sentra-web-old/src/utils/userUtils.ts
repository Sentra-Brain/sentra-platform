// src/utils/userUtils.ts
// Utility functions for safe user operations

/**
 * Safely gets a user display name by ID with fallback
 * Returns a readable name or falls back to ID
 */
export const getSafeUserDisplayName = (userId?: string): string => {
  if (!userId) {
    return 'Unknown User';
  }
  
  // If it looks like a UUID, return a more user-friendly fallback
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  if (uuidRegex.test(userId)) {
    return 'Unknown User';
  }
  
  // Otherwise return the ID as-is (might be a username or email)
  return userId;
};

/**
 * Safely truncates a user display name for UI display
 */
export const truncateUserName = (name: string, maxLength: number = 20): string => {
  if (name.length <= maxLength) {
    return name;
  }
  return `${name.substring(0, maxLength - 3)}...`;
};