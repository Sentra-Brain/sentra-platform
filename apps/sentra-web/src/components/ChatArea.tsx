// src/components/ChatArea.tsx
import React, { useEffect, useRef } from 'react';
import { useChat } from '../hooks/useChat';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './ChatArea.css';

const ChatArea: React.FC = () => {
  const { currentConversation, waitingForAnswer } = useChat();

  const messages = currentConversation?.messages || [];

  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentConversation?.messages.length]);

  return (
    <main className="chat-area">
      {currentConversation ? (
        <div className="messages">
          {messages.map((msg) => (
            <div key={msg.timestamp.toString()} className={`message-bubble ${msg.role}`}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
            </div>
          ))}
          {waitingForAnswer && <div className="waiting-bubble">Waiting...</div>}
          <div ref={endOfMessagesRef} />
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-state-content">
            <h2>Welcome to Sentra Brain</h2>
            <p>Start a new conversation to begin chatting with AI.</p>
          </div>
        </div>
      )}
    </main>
  );
};

export default ChatArea;
