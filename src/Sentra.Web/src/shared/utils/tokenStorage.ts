const ACCESS_KEY = 'token'
const REFRESH_KEY = 'refreshToken'

export const tokenStorage = {
  setTokens(accessToken: string, refreshToken: string, persistent: boolean) {
    const storage = persistent ? localStorage : sessionStorage
    storage.setItem(ACCESS_KEY, accessToken)
    storage.setItem(REFRESH_KEY, refreshToken)
  },

  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_KEY) || sessionStorage.getItem(ACCESS_KEY)
  },

  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_KEY) || sessionStorage.getItem(REFRESH_KEY)
  },

  clear() {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
    sessionStorage.removeItem(ACCESS_KEY)
    sessionStorage.removeItem(REFRESH_KEY)
  },

  isPersistent(): boolean {
    return !!localStorage.getItem(REFRESH_KEY)
  },
}
