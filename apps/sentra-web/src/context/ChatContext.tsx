import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

export type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
};

export type Conversation = {
  id: string;
  name: string;
  messages: Message[];
  createdAt: number;
};

export type ChatContextType = {
  conversations: Conversation[];
  currentConversationId: string | null;
  setCurrentConversationId: (id: string) => void;
  addMessage: (msg: Omit<Message, 'id' | 'timestamp'>) => void;
  newConversation: () => void;
  updateConversationName: (id: string, name: string) => void;
};

const ChatContext = createContext<ChatContextType | undefined>(undefined);

const CHAT_KEY = 'sentra_brain_conversations';

function loadConversations(): Conversation[] {
  try {
    const data = localStorage.getItem(CHAT_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

function saveConversations(conversations: Conversation[]) {
  localStorage.setItem(CHAT_KEY, JSON.stringify(conversations));
}

export const ChatProvider = ({ children }: { children: ReactNode }) => {
  const [conversations, setConversations] = useState<Conversation[]>(loadConversations());
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(conversations[0]?.id || null);

  useEffect(() => {
    saveConversations(conversations);
  }, [conversations]);

  const addMessage = (msg: Omit<Message, 'id' | 'timestamp'>) => {
    setConversations(prev => prev.map(conv =>
      conv.id === currentConversationId
        ? { ...conv, messages: [...conv.messages, { ...msg, id: crypto.randomUUID(), timestamp: Date.now() }] }
        : conv
    ));
  };

  const newConversation = () => {
    const id = crypto.randomUUID();
    const conv: Conversation = {
      id,
      name: 'New Conversation',
      messages: [],
      createdAt: Date.now(),
    };
    setConversations(prev => [conv, ...prev]);
    setCurrentConversationId(id);
  };

  const updateConversationName = (id: string, name: string) => {
    setConversations(prev => prev.map(conv => conv.id === id ? { ...conv, name } : conv));
  };

  return (
    <ChatContext.Provider value={{ conversations, currentConversationId, setCurrentConversationId, addMessage, newConversation, updateConversationName }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error('useChat must be used within ChatProvider');
  return ctx;
};
