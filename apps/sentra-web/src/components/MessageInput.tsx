import React, { useState, useRef } from 'react';
import { useChat } from '../context/ChatContext';
import './MessageInput.css';

const MessageInput: React.FC = () => {
  const { addMessage } = useChat();
  const [value, setValue] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if (value.trim()) {
      addMessage({ role: 'user', content: value });
      setValue('');
    }
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
      <textarea
        className="message-input"
        value={value}
        onChange={e => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a message..."
        rows={1}
      />
      <button className="file-upload-btn" onClick={() => fileInputRef.current?.click()} title="Upload file">
        <span role="img" aria-label="upload">📎</span>
      </button>
      <input
        type="file"
        ref={fileInputRef}
        style={{ display: 'none' }}
        onChange={handleFileUpload}
      />
      <button className="send-btn" onClick={handleSend} title="Send">
        <span role="img" aria-label="send">➤</span>
      </button>
    </div>
  );
};

export default MessageInput;
