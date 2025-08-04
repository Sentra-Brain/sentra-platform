// src/models/knowledgeModels.ts
// TypeScript models for Knowledge Management API

import type { UserRef } from "@features/user/types/user";

// Const enums matching the backend (using const assertions for better TypeScript support)
export const KnowledgeSourceType = {
  UPLOAD: 'upload',
  FOLDER: 'folder',
  EXTERNAL_API: 'external_api',
  MANUAL: 'manual',
  MCP_TOOL: 'mcp_tool',
} as const;

export type KnowledgeSourceType = (typeof KnowledgeSourceType)[keyof typeof KnowledgeSourceType];

export const KnowledgeSourceVisibility = {
  PRIVATE: 'private',
  SHARED: 'shared',
  ORG_WIDE: 'org-wide',
} as const;

export type KnowledgeSourceVisibility = (typeof KnowledgeSourceVisibility)[keyof typeof KnowledgeSourceVisibility];

export const KnowledgeSourceStatus = {
  ACTIVE: 'active',
  DISABLED: 'disabled',
  ERROR: 'error',
} as const;

export type KnowledgeSourceStatus = (typeof KnowledgeSourceStatus)[keyof typeof KnowledgeSourceStatus];

export const DocumentFileType = {
  PDF: 'pdf',
  DOCX: 'docx',
  TXT: 'txt',
  MD: 'md',
} as const;

export type DocumentFileType = (typeof DocumentFileType)[keyof typeof DocumentFileType];

export const DocumentStatus = {
  QUEUED: 'queued',
  PROCESSING: 'processing',
  INDEXED: 'indexed',
  FAILED: 'failed',
  TO_BE_REMOVED: 'to_be_removed',
} as const;

export type DocumentStatus = (typeof DocumentStatus)[keyof typeof DocumentStatus];

// Knowledge Source interfaces
export interface KnowledgeSource {
  id: string;
  name: string;
  type: KnowledgeSourceType;
  path?: string;
  description?: string;
  created_by: UserRef;
  created_at: string;
  visibility: KnowledgeSourceVisibility;
  auto_index: boolean;
  status: KnowledgeSourceStatus;
}

export interface CreateKnowledgeSourceRequest {
  name: string;
  type: KnowledgeSourceType;
  path?: string;
  description?: string;
  visibility: KnowledgeSourceVisibility;
  auto_index: boolean;
}

export interface KnowledgeSourceListResponse {
  sources: KnowledgeSource[];
  total: number;
}

// Document interfaces
export interface KnowledgeDocument {
  id: string;
  filename: string;
  display_name: string;
  description?: string;
  filetype: DocumentFileType;
  path: string;
  created_by: UserRef;
  created_at: string;
  status: DocumentStatus;
  status_message?: string;
  error?: string;
  knowledge_source_id: string;
  chunks_count?: number;
}

export interface DocumentUploadRequest {
  display_name: string;
  description?: string;
}

export interface DocumentListResponse {
  documents: KnowledgeDocument[];
  total: number;
}

// Tree node interface for UI
export interface KnowledgeTreeNode {
  id: string;
  name: string;
  type: 'visibility-group' | 'knowledge-source' | 'document';
  visibility?: KnowledgeSourceVisibility;
  knowledgeSource?: KnowledgeSource;
  document?: KnowledgeDocument;
  children?: KnowledgeTreeNode[];
  expanded?: boolean;
  documentCount?: number;
}