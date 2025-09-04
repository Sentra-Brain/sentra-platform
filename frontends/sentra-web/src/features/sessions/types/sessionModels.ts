// src/models/conversationModels.ts
// This file defines the models for conversation-related data structures
export type SessionListItem = {
  id: string;
  title: string;
  created_at: string;
};

export type MessageRole = 'user' | 'assistant' | 'system';

export type ChatMessage = {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: number;
  is_system_prompt?: boolean; // Optional flag for system prompt messages
};

export type SessionDetails = {
  id: string;
  title: string;
  description?: string;
  initial_prompt?: string;
  messages: Array<ChatMessage>;
};

export type CreateSessionRequest = {
  initial_prompt: string;
};

export type CreateSessionResponse = {
  id: string;
  title: string;
  created_at: string;
};

export type UpdateSessionRequest = {
  title?: string;
  description?: string;
  initial_prompt?: string;
};

export type UpdateSessionResponse = {
  session_id: string;
  title?: string | null;
  description?: string | null;
};

export type DeleteSessionResponse = {
  success: boolean;
};
