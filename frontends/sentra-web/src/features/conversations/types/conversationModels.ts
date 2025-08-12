// src/models/conversationModels.ts
// This file defines the models for conversation-related data structures
export type ConversationListItem = {
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

export type ConversationDetails = {
  id: string;
  title: string;
  description?: string;
  initial_prompt?: string;
  messages: Array<ChatMessage>;
};

export type CreateConversationRequest = {
  initial_prompt: string;
};

export type CreateConversationResponse = {
  id: string;
  title: string;
  created_at: string;
};

export type UpdateConversationRequest = {
  title?: string;
  description?: string;
  initial_prompt?: string;
};

export type UpdateConversationResponse = {
  conversation_id: string;
  title?: string | null;
  description?: string | null;
};

export type DeleteConversationResponse = {
  success: boolean;
};
