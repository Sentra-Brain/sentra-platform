import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ChatArea, MessageInput } from '../components';
import { useChat } from '../hooks/useChat';

const ChatPage: React.FC = () => {
  const { conversationId } = useParams();
  const { currentConversation, loadConversationById, clearCurrentConversation } = useChat();

  useEffect(() => {
    if (conversationId) {
      // Load conversation from URL parameter
      if (!currentConversation || currentConversation.id !== conversationId) {
        loadConversationById(conversationId);
      }
    } else {
      // Clear current conversation when on chat home
      if (currentConversation) {
        clearCurrentConversation();
      }
    }
  }, [conversationId, currentConversation, loadConversationById, clearCurrentConversation]);

  return (
    <>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        <ChatArea />
      </div>
      <MessageInput />
      <div className="p-4 text-sm text-center text-slate-400">
        Sentra can make mistakes. Check important info.
      </div>
    </>
  );
};

export default ChatPage;