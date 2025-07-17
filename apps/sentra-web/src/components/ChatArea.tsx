import React from 'react';
import { useChat } from '../context/ChatContext';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './ChatArea.css';

const SERVER_INFO = {
  model: 'tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
  build: 'b5897-bdca3837',
};

const ServerInfoCard = () => (
  <div className="server-info-card">
    <strong>Server Info</strong>
    <div>Model: {SERVER_INFO.model}</div>
    <div>Build: {SERVER_INFO.build}</div>
  </div>
);

const ChatArea: React.FC = () => {
  const { conversations, currentConversationId } = useChat();
  const messages = conversations.find(c => c.id === currentConversationId)?.messages || [];

  return (
    <main className="chat-area">
      <ServerInfoCard />
      <div className="messages">
        {messages.map(msg => (
          <div key={msg.id} className={`message-bubble ${msg.role}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
          </div>
        ))}
      </div>
    </main>
  );
};

export default ChatArea;
