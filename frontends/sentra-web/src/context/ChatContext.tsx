import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { conversationService } from '../services/conversationService';
import { chatService } from '../services/chatService';
import type {
  ConversationListItem,
  ConversationDetails,
  CreateConversationRequest,
  UpdateConversationRequest,
} from '../models/conversationModels';
import { ChatContext } from './ChatContextInstance';
import { notifyError } from '../lib/notify';

export type ChatContextType = {
  conversations: ConversationListItem[];
  currentConversation: ConversationDetails | null;
  isStreaming: boolean;
  waitingForAnswer: boolean;
  loadConversations: () => Promise<void>;
  selectConversation: (id: string) => Promise<void>;
  loadConversationById: (id: string) => Promise<void>;
  createConversation: (data: CreateConversationRequest) => Promise<void>;
  updateConversation: (id: string, data: UpdateConversationRequest) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  sendMessage: (text: string) => Promise<void>;
  stopMessage: () => void;
  clearCurrentConversation: () => void;
};

export const ChatProvider = ({ children }: { children: React.ReactNode }) => {
  const [conversations, setConversations] = useState<ConversationListItem[]>([]);
  const [currentConversation, setCurrentConversation] = useState<ConversationDetails | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [waitingForAnswer, setWaitingForAnswer] = useState(false);
  const controllerRef = useRef<() => void | null>(null);
  const navigate = useNavigate();

  const loadConversations = async () => {
    try {
      const list = await conversationService.list();
      setConversations(list);
    } catch (error) {
      console.error('[ChatContext] Failed to load conversations', error);
      setConversations([]);
    }
  };

  const selectConversation = async (id: string) => {
    const details = await conversationService.get(id);
    setCurrentConversation(details);
    // Navigate to the conversation URL
    navigate(`/c/${id}`);
  };

  const loadConversationById = async (id: string) => {
    try {
      const details = await conversationService.get(id);
      setCurrentConversation(details);
    } catch (error) {
      console.error('[ChatContext] Failed to load conversation', error);
      setCurrentConversation(null);
      // Navigate back to chat if conversation doesn't exist
      navigate('/chat');
    }
  };

  const clearCurrentConversation = () => {
    setCurrentConversation(null);
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
      // Navigate back to chat home when deleting current conversation
      navigate('/chat');
    }
  };

  const sendMessage = async (text: string) => {
    if (!text.trim() || isStreaming) return;

    // If no conversation is selected, create one first
    if (!currentConversation) {
      await createConversation({ content: text.trim() });
      return; // The message will be sent as part of conversation creation
    }

    const userMessage = {
      id: crypto.randomUUID(),
      timestamp: Date.now(),
      role: 'user',
      content: text,
    };

    setCurrentConversation(prev => {
      if (!prev) return null;
      return { ...prev, messages: [...prev.messages, userMessage] };
    });

    setWaitingForAnswer(true);
    setIsStreaming(true);
    let assistantStarted = false;

    controllerRef.current = chatService.sendMessageStream(
      { conversation_id: currentConversation.id, content: text },
      (delta) => {
        if (!assistantStarted && !delta.final) {
          // Start the assistant message if not already started
          setWaitingForAnswer(false);
          startAssistantMessage();
          assistantStarted = true;
        }

        if (!delta.final) {
          appendToLastAssistantMessage(delta.content);
        } else {
          setIsStreaming(false);
          controllerRef.current = null;
        }
      },
      (err) => {
        appendToLastAssistantMessage('\n[Error generating response]');
        setIsStreaming(false);
        setWaitingForAnswer(false);
        console.error('[ChatProvider] sendMessage error', err);
        notifyError(err);
        controllerRef.current = null;
      }
    );
  };

  const stopMessage = () => {
    controllerRef.current?.();
    controllerRef.current = null;
    setIsStreaming(false);
  };

  const startAssistantMessage = () => {
    setCurrentConversation(prev => {
      if (!prev) return null;
      return {
        ...prev,
        messages: [
          ...prev.messages,
          {
            id: crypto.randomUUID(),
            timestamp: Date.now(),
            role: 'assistant',
            content: '',
          },
        ],
      };
    });
  };

  const appendToLastAssistantMessage = (delta: string) => {
    setCurrentConversation(prev => {
      if (!prev) return null;
      const messages = [...prev.messages];
      const lastIndex = messages.length - 1;
      if (lastIndex < 0 || messages[lastIndex].role !== 'assistant') return prev;

      messages[lastIndex] = {
        ...messages[lastIndex],
        content: messages[lastIndex].content + delta,
      };

      return { ...prev, messages };
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
        isStreaming,
        waitingForAnswer,
        loadConversations,
        selectConversation,
        loadConversationById,
        createConversation,
        updateConversation,
        deleteConversation,
        sendMessage,
        stopMessage,
        clearCurrentConversation,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};
