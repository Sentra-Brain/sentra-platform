import React from 'react';
import { ChatArea, MessageInput } from '../components';

const ChatPage: React.FC = () => {
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

export default ChatPage;