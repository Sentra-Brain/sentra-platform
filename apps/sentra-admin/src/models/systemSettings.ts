// src/models/systemSettings.ts
// This file defines the SystemSettings model used across the application
export interface SystemSettings {
  id: number;
  workspace_name: string;
  license_type: string;
  maintenance_mode: boolean;
  default_language: string;
  log_retention_days: number;
  max_users: number;
}