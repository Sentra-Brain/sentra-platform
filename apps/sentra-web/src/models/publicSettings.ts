// src/models/publicSettings.ts
// This file defines the PublicSettings model used for application-wide settings
export type PublicSettings = {
  workspace_name: string;
  max_users: number;
  available_slots: number;
};