// src/components/MessageInput.tsx
import React, { useState, useRef } from 'react';
import { useChat } from '../hooks/useChat';
import { ArrowUp } from 'lucide-react';
import './MessageInput.css';

const MessageInput: React.FC = () => {
  const { currentConversation, updateConversation } = useChat();
  const [value, setValue] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = async () => {
    if (!value.trim() || !currentConversation) return;

    // Here you'd normally call the backend to send a message
    // For now, just simulate adding a user message
    // This could later call: conversationService.addMessage(conversation_id, { ... })
    console.warn('TODO: integrate message sending API');

    // Temporary mock logic (to simulate frontend-only messaging):
    await updateConversation(currentConversation.id, {
      messages: [...(currentConversation.messages || []), { sender: 'user', content: value }],
    });

    setValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    // File upload logic placeholder
    e.target.value = '';
  };

  return (
    <div className="message-input-bar">
      <button
        className="file-upload-btn"
        onClick={() => fileInputRef.current?.click()}
        title="Upload file"
      >
        <ArrowUp size={18} />
      </button>

      <textarea
        className="message-input"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={
          currentConversation ? 'Type a message...' : 'Select or create a conversation first...'
        }
        rows={1}
        disabled={!currentConversation}
      />

      <input type="file" ref={fileInputRef} hidden onChange={handleFileUpload} />

      <button
        className="send-btn"
        onClick={handleSend}
        title="Send"
        disabled={!value.trim() || !currentConversation}
      >
        <span role="img" aria-label="send">
          ➤
        </span>
      </button>
    </div>
  );
};

export default MessageInput;
