import React, { useState, useRef } from 'react';
import { useChat } from '../hooks/useChat';
import { Plus, Settings, Mic, Send, X, ChevronDown } from 'lucide-react';
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

  const handleSend = async () => {
    if (!value.trim() || isStreaming) return;
    await sendMessage(value.trim());
    setValue('');
  };

  const handleStop = () => {
    if (isStreaming) stopMessage();
  };

  const handleKeyDown = async (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      await handleSend();
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    // TODO: Implement
    e.target.value = '';
  };

  return (
    <div className="message-input-container">
      <button className="icon-btn" disabled title="Coming soon">
        <Plus size={18} />
      </button>

      <button className="icon-btn" disabled title="Tools (coming soon)">
        <Settings size={18} />
      </button>

      <div className="message-input-wrapper">
        <textarea
          className="message-input"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            currentConversation
              ? 'Type a message...'
              : 'Ask anything to start a new conversation...'
          }
          rows={1}
          disabled={isStreaming}
        />
      </div>

      <input type="file" ref={fileInputRef} hidden onChange={handleFileUpload} />

      <button className="icon-btn" disabled title="Dictate (coming soon)">
        <Mic size={18} />
      </button>

      {isStreaming ? (
        <button className="icon-btn" onClick={handleStop} title="Stop">
          <X size={18} />
        </button>
      ) : (
        <button
          className="icon-btn send"
          onClick={handleSend}
          title="Send"
          disabled={!value.trim() || isStreaming}
        >
          <Send size={18} />
        </button>
      )}

      
        <button
          className="scroll-to-bottom-btn"         
          title="Scroll to bottom"
        >
          <ChevronDown size={20} />
        </button>
      
    </div>
  );
};

export default MessageInput;
