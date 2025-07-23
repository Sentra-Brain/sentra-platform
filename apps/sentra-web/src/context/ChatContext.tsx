import React, { useState, useEffect } from 'react';
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
  appendUserMessage: (text: string) => void;
  appendEmptyAssistantMessage: () => void;
  appendToLastAssistantMessage: (delta: string) => void;
  replaceLastAssistantMessage: (fullContent: string) => void;
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

  const appendUserMessage = (text: string) => {
    if (!currentConversation) return;

    setCurrentConversation({
      ...currentConversation,
      messages: [
        ...currentConversation.messages,
        {
          id: crypto.randomUUID(),
          timestamp: Date.now(),
          role: 'user',
          content: text,
        },
      ],
    });
  };

  const appendEmptyAssistantMessage = () => {
    if (!currentConversation) return;

    setCurrentConversation({
      ...currentConversation,
      messages: [
        ...currentConversation.messages,
        {
          id: crypto.randomUUID(),
          timestamp: Date.now(),
          role: 'assistant',
          content: '',
        },
      ],
    });
  };

  const appendToLastAssistantMessage = (delta: string) => {
    if (!currentConversation) return;

    const messages = [...currentConversation.messages];
    const lastIndex = messages.length - 1;

    if (lastIndex < 0 || messages[lastIndex].role !== 'assistant') return;

    messages[lastIndex] = {
      ...messages[lastIndex],
      content: messages[lastIndex].content + delta,
    };

    setCurrentConversation({
      ...currentConversation,
      messages,
    });
  };

  const replaceLastAssistantMessage = (fullContent: string) => {
    if (!currentConversation) return;

    const messages = [...currentConversation.messages];
    const lastIndex = messages.length - 1;

    if (lastIndex < 0 || messages[lastIndex].role !== 'assistant') return;

    messages[lastIndex] = {
      ...messages[lastIndex],
      content: fullContent,
    };

    setCurrentConversation({
      ...currentConversation,
      messages,
    });
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
        appendUserMessage,
        appendEmptyAssistantMessage,
        appendToLastAssistantMessage,
        replaceLastAssistantMessage,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};
