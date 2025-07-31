// frontends/sentra-web/src/models/user.ts
// This file defines the User model used across the application
export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  disabled: boolean;
  roles: string[];
}