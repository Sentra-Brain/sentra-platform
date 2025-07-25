import type { User } from "../models/user";

export interface AuthContextType {
  user: User | null;
  setUser: React.Dispatch<React.SetStateAction<User | null>>;
  login: (email: string, password: string, remember?: boolean) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
  refreshAccessToken: () => Promise<boolean>;
  getValidAccessToken: () => Promise<string | null>;
}