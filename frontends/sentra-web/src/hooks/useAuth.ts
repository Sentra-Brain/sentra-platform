import { useAppDispatch } from "../store/hooks";
import { loginSuccess, logout } from "../features/auth/authSlice";
import { authService } from "../services/authService";
import { parseJWT, isTokenExpired } from "../utils/tokenUtils";
import { toast } from "react-toastify";

export function useAuth() {
  const dispatch = useAppDispatch();

  const login = async (email: string, password: string, remember: boolean) => {
    try {
      const { access_token, refresh_token } = await authService.login(
        email,
        password
      );

      const payload = parseJWT(access_token);
      if (!payload) throw new Error("Invalid token");

      const roles = payload.roles?.split(",") ?? [];

      dispatch(loginSuccess({ token: access_token, roles }));

      if (remember) {
        localStorage.setItem("token", access_token);
        localStorage.setItem("refreshToken", refresh_token);
      }

      // toast.success('Login successful')
      return true;
    } catch (error) {
      console.error("Login failed:", error);
      toast.error("Invalid credentials");
      return false;
    }
  };

  const logoutUser = () => {
    dispatch(logout());
    localStorage.removeItem("token");
    localStorage.removeItem("refreshToken");
  };

  const restoreSession = () => {
    const token = localStorage.getItem("token");

    if (!token || isTokenExpired(token)) {
      dispatch(logout());
      return false;
    }

    const payload = parseJWT(token);
    if (!payload) {
      dispatch(logout());
      return false;
    }

    const roles = payload.roles?.split(",") ?? [];
    dispatch(loginSuccess({ token, roles }));
    return true;
  };

  return {
    login,
    logout: logoutUser,
    restoreSession,
  };
}
