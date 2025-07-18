// src/services/authService.ts
// This user model used across the application
export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  disabled: boolean;
}