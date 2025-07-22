// src/pages/Chat.tsx
// This file defines the main chat interface of the application
import React from 'react';
import ChatArea from '../components/ChatArea';
import MessageInput from '../components/MessageInput';
import Sidebar from '../components/Sidebar';
import TopBar from '../components/TopBar';

const Chat: React.FC = () => {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0">
        <TopBar />
        <div className="flex-1 flex flex-col p-4 overflow-auto">
          <ChatArea />
        </div>
        <div className="p-4">
          <MessageInput />
        </div>
      </div>
    </div>
  );
};

export default Chat;
