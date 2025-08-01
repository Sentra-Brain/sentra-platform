// src/pages/Chat.tsx
// This file defines an alternative chat interface implementation
// Note: Currently not used in routing - ChatPage.tsx is the active implementation
import React from 'react';
import ChatArea from '../components/ChatArea';
import MessageInput from '../components/MessageInput';

const Chat: React.FC = () => {
  return (
    <>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        <ChatArea />
      </div>
      <MessageInput />
      <div className="p-4 text-sm text-center text-slate-400">
        Sentra can make mistakes. Check important info.
      </div>
    </>
  );
};

export default Chat;
