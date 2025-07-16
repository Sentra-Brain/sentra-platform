
import React, { useState } from 'react';
import { ChatProvider } from './context/ChatContext';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import ChatArea from './components/ChatArea';
import MessageInput from './components/MessageInput';
import SettingsModal from './components/SettingsModal';
import './index.css';
import './App.css';


const App: React.FC = () => {
  const [settingsOpen, setSettingsOpen] = useState(false);

  return (
    <ChatProvider>
      <div className="app-root dark-mode">
        <Sidebar />
        <div className="main-content">
          <TopBar onSettings={() => setSettingsOpen(true)} />
          <ChatArea />
          <MessageInput />
        </div>
        <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
      </div>
    </ChatProvider>
  );
};

export default App;
