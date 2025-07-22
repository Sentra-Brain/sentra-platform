import React, {  useState, useEffect } from 'react';
import { conversationService } from '../services/conversationService';
import type {
  ConversationListItem,
  ConversationDetails,
  CreateConversationRequest,
  UpdateConversationRequest,
} from '../models/conversationModels';
import { ChatContext } from './ChatContextInstance';

export type ChatContextType = {
  conversations: ConversationListItem[];
  currentConversation: ConversationDetails | null;
  loadConversations: () => Promise<void>;
  selectConversation: (id: string) => Promise<void>;
  createConversation: (data: CreateConversationRequest) => Promise<void>;
  updateConversation: (id: string, data: UpdateConversationRequest) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
};

export const ChatProvider = ({ children }: { children: React.ReactNode }) => {
  const [conversations, setConversations] = useState<ConversationListItem[]>([]);
  const [currentConversation, setCurrentConversation] = useState<ConversationDetails | null>(null);

  const loadConversations = async () => {
    const list = await conversationService.list();
    setConversations(list);
  };

  const selectConversation = async (id: string) => {
    const details = await conversationService.get(id);
    setCurrentConversation(details);
  };

  const createConversation = async (data: CreateConversationRequest) => {
    const { id: conversation_id } = await conversationService.create(data);
    await loadConversations();
    await selectConversation(conversation_id);
  };

  const updateConversation = async (id: string, data: UpdateConversationRequest) => {
    await conversationService.update(id, data);
    await loadConversations();
    if (currentConversation?.id === id) {
      await selectConversation(id);
    }
  };

  const deleteConversation = async (id: string) => {
    await conversationService.remove(id);
    await loadConversations();
    if (currentConversation?.id === id) {
      setCurrentConversation(null);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  return (
    <ChatContext.Provider
      value={{
        conversations,
        currentConversation,
        loadConversations,
        selectConversation,
        createConversation,
        updateConversation,
        deleteConversation,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};
