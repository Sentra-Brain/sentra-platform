// src/components/MessageInput.tsx
import React, { useState, useRef } from 'react';
import { useChat } from '../hooks/useChat';
import { ArrowUp } from 'lucide-react';
import './MessageInput.css';


const MessageInput: React.FC = () => {
  const {
    currentConversation,
    isStreaming,
    sendMessage,
    stopMessage,
  } = useChat();

  const [value, setValue] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if (!value.trim() || !currentConversation || isStreaming) return;
    sendMessage(value.trim());
    setValue('');
  };

  const handleStop = () => {
    if (isStreaming) {
      stopMessage();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Placeholder for file upload logic
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
        disabled={!currentConversation || isStreaming}
      />

      <input type="file" ref={fileInputRef} hidden onChange={handleFileUpload} />

      {isStreaming ? (
        <button className="stop-btn" onClick={handleStop} title="Stop">
          <span role="img" aria-label="stop">
            ⏹
          </span>
        </button>
      ) : (
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
      )}
    </div>
  );
};

export default MessageInput;
