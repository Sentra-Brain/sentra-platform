// src/services/conversationService.ts
// This file defines the conversation service for managing chat conversations
import { httpClient } from '../lib/httpClient';
import type {
  ConversationListItem,
  ConversationDetails,
  CreateConversationRequest,
  CreateConversationResponse,
  UpdateConversationRequest,
  UpdateConversationResponse,
  DeleteConversationResponse,
} from '../models/conversationModels';

export const conversationService = {
  list(): Promise<ConversationListItem[]> {
    return httpClient.get('/conversations/');
  },

  create(data: CreateConversationRequest): Promise<CreateConversationResponse> {
    return httpClient.post('/conversations/', data);
  },

  get(id: string): Promise<ConversationDetails> {
    return httpClient.get(`/conversations/${id}`);
  },

  update(id: string, data: UpdateConversationRequest): Promise<UpdateConversationResponse> {
    return httpClient.put(`/conversations/${id}`, data);
  },

  remove(id: string): Promise<DeleteConversationResponse> {
    return httpClient.del(`/conversations/${id}`);
  },
};