export function decodeJwt(token: string): Record<string, unknown> | null {
  try {
    const base64 = token.split('.')[1];
    const padded = base64.padEnd(base64.length + (4 - base64.length % 4) % 4, '=');
    const json = atob(padded.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(json);
  } catch (e) {
    console.error('[decodeJwt] Invalid token:', e);
    return null;
  }
}