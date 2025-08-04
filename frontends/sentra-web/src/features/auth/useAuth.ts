import { useAppDispatch, useAppSelector } from '@store/hooks';
import { loginSuccess, logout, markRehydrated } from './authSlice';
import { authService } from './authService';
import { userService } from '@features/user/userService';
import { parseJWT, isTokenExpired } from '@shared/utils/tokenUtils';
import { toast } from 'react-toastify';
import { tokenStorage } from '@shared/utils/tokenStorage';

export function useAuth() {
  const dispatch = useAppDispatch();
  const user = useAppSelector((state) => state.auth.user);

  const login = async (email: string, password: string, remember: boolean) => {
    try {
      const { access_token, refresh_token } = await authService.login(email, password);

      const payload = parseJWT(access_token);
      if (!payload) throw new Error('Invalid token');

      const roles = payload.roles?.split(',') ?? [];
      const currentUser = await userService.getCurrentUser();

      dispatch(loginSuccess({ token: access_token, roles, user: currentUser }));
      tokenStorage.setTokens(access_token, refresh_token, remember);

      return true;
    } catch (error) {
      console.error('Login failed:', error);
      toast.error('Invalid credentials');
      return false;
    }
  };

  const logoutUser = () => {
    dispatch(logout());
    tokenStorage.clear();
  };

  const restoreSession = async () => {
    const token = tokenStorage.getAccessToken();

    if (!token || isTokenExpired(token)) {
      dispatch(logout());
      dispatch(markRehydrated());
      return false;
    }

    const payload = parseJWT(token);
    if (!payload) {
      dispatch(logout());
      dispatch(markRehydrated());
      return false;
    }

    const roles = payload.roles?.split(',') ?? [];

    try {
      const currentUser = await userService.getCurrentUser();
      dispatch(loginSuccess({ token, roles, user: currentUser }));
      return true;
    } catch (error) {
      console.error('Failed to restore user from token:', error);
      dispatch(logout());
      return false;
    } finally {
      dispatch(markRehydrated());
    }
  };

  return {
    login,
    logout: logoutUser,
    restoreSession,
    user,
  };
}
