
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
      <div className="app-root dark-mode" style={{ display: 'flex', height: '100vh', width: '100vw' }}>
        <Sidebar />
        <div className="main-content" style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          <TopBar onSettings={() => setSettingsOpen(true)} />
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
            <ChatArea />
          </div>
          <MessageInput />
        </div>
        <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
      </div>
    </ChatProvider>
  );
};

export default App;
