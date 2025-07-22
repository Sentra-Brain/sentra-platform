// src/models/conversationModels.ts
// This file defines the models for conversation-related data structures
export type ConversationListItem = {
  id: string;
  title: string;
  created_at: string;
};

export type ConversationDetails = {
  id: string;
  title: string;
  description?: string;
  initial_prompt?: string;
  messages: Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
  }>;
};

export type CreateConversationRequest = {
  title?: string;
  description?: string;
  initial_prompt?: string;
  content: string;
};

export type CreateConversationResponse = {
  id: string;
};

export type UpdateConversationRequest = {
  title?: string;
  description?: string;
  initial_prompt?: string;
};

export type UpdateConversationResponse = {
  success: boolean;
};

export type DeleteConversationResponse = {
  success: boolean;
};
