// src/components/MessageInput.tsx
import React, { useState, useRef } from 'react';
import { useChat } from '../hooks/useChat';
import { ArrowUp } from 'lucide-react';
import './MessageInput.css';
import { chatService } from '../services/chatService';

const MessageInput: React.FC = () => {
  const { currentConversation, appendUserMessage, appendEmptyAssistantMessage, appendToLastAssistantMessage } = useChat();
  const [value, setValue] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = async () => {
    if (!value.trim() || !currentConversation) return;

    const userInput = value.trim();
    setValue('');

    // Paso 1: Añadir mensaje de usuario
    appendUserMessage(userInput);

    // Paso 2: Añadir mensaje de assistant vacío
    appendEmptyAssistantMessage();

    // Paso 3: Consumir el stream y actualizar la respuesta
    chatService.sendMessageStream(
      {
        conversation_id: currentConversation.id,
        content: userInput,
      },
      (delta) => {
        if (!delta.final) {
          appendToLastAssistantMessage(delta.content);
        }
      },
      (err) => {
        console.error('Streaming error:', err);
        appendToLastAssistantMessage('\n[Error generando respuesta]');
      }
    );
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
