// src/components/ChatArea.tsx
import React, { useEffect, useRef } from 'react';
import { useChat } from '../hooks/useChat';
import { useAuth } from '../context/useAuth';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './ChatArea.css';

const ChatArea: React.FC = () => {
  const { currentConversation, waitingForAnswer } = useChat();
  const { user } = useAuth();

  const messages = currentConversation?.messages || [];

  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentConversation?.messages.length]);

  // Get the user's first name for personalization
  const getFirstName = () => {
    if (user?.full_name) {
      return user.full_name.split(' ')[0];
    }
    if (user?.username) {
      return user.username.charAt(0).toUpperCase() + user.username.slice(1);
    }
    return 'there';
  };

  return (
    <main className="chat-area">
      {currentConversation ? (
        <div className="messages">
          {messages.map((msg) => (
            <div
              key={msg.id || `${msg.role}-${msg.timestamp}`}
              className={`message-bubble ${msg.role}`}
            >
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
            </div>
          ))}
          {waitingForAnswer && <div className="waiting-bubble">Waiting...</div>}
          <div ref={endOfMessagesRef} />
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-state-content">
            <h2>Welcome back, {getFirstName()}.</h2>
            <p>Ask anything to start a new conversation.</p>
          </div>
        </div>
      )}
    </main>
  );
};

export default ChatArea;
