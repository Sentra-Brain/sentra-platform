import React, { useState, useRef } from 'react';
import { useChat } from '../context/ChatContext';
import { ArrowUp } from 'lucide-react';
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
        placeholder="Type a message..."
        rows={1}
      />

      <input type="file" ref={fileInputRef} hidden onChange={handleFileUpload} />

      <button className="send-btn" onClick={handleSend} title="Send" disabled={!value.trim()}>
        <span role="img" aria-label="send">
          ➤
        </span>
      </button>
    </div>
  );
};

export default MessageInput;
