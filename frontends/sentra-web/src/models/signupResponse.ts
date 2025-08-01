import type { User } from './user';

export interface SignupResponse {
  user: User;
  message: string;
}
