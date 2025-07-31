// Token utilities for parsing and validating JWT tokens

export interface JWTPayload {
  sub: string;
  roles: string;
  exp: number;
  type?: string;
}

export function parseJWT(token: string): JWTPayload | null {
  try {
    const payload = token.split('.')[1];
    if (!payload) return null;
    
    const decoded = atob(payload);
    return JSON.parse(decoded) as JWTPayload;
  } catch (error) {
    console.error('Failed to parse JWT:', error);
    return null;
  }
}

export function isTokenExpired(token: string, bufferMinutes = 2): boolean {
  const payload = parseJWT(token);
  if (!payload) return true;
  
  const now = Math.floor(Date.now() / 1000);
  const buffer = bufferMinutes * 60; // Convert minutes to seconds
  
  return payload.exp <= (now + buffer);
}

export function getTokenExpiryTime(token: string): Date | null {
  const payload = parseJWT(token);
  if (!payload) return null;
  
  return new Date(payload.exp * 1000);
}