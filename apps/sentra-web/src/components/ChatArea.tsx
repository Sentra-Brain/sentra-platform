// src/components/ChatArea.tsx
import React from 'react';
import { useChat } from '../hooks/useChat';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './ChatArea.css';

const ChatArea: React.FC = () => {
  const { currentConversation } = useChat();

  const messages = currentConversation?.messages || [];

  return (
    <main className="chat-area">
      {currentConversation ? (
        <div className="messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`message-bubble ${msg.role}`}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
            </div>
          ))}
        </div>
      ) : (
        <div className="no-conversation-message">
          <p>No conversation selected.</p>
        </div>
      )}
    </main>
  );
};

export default ChatArea;
