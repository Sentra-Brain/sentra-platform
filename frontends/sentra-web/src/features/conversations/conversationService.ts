// src/services/conversationService.ts


import apiClient from '@shared/api/apiClient'
import type {
  ConversationListItem,
  ConversationDetails,
  CreateConversationRequest,
  CreateConversationResponse,
  UpdateConversationRequest,
  UpdateConversationResponse,
  DeleteConversationResponse,
} from './types/conversationModels'

export const conversationService = {
  list(): Promise<ConversationListItem[]> {
    return apiClient.get('/conversations/').then(res => res.data)
  },

  create(data: CreateConversationRequest): Promise<CreateConversationResponse> {
    return apiClient.post('/conversations/', data).then(res => res.data)
  },

  get(id: string): Promise<ConversationDetails> {
    return apiClient.get(`/conversations/${id}`).then(res => res.data)
  },

  update(id: string, data: UpdateConversationRequest): Promise<UpdateConversationResponse> {
    return apiClient.put(`/conversations/${id}`, data).then(res => res.data)
  },

  remove(id: string): Promise<DeleteConversationResponse> {
    return apiClient.delete(`/conversations/${id}`).then(res => res.data)
  },
}
