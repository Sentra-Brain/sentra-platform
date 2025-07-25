import React from 'react';
import { Outlet } from 'react-router-dom';
import { ChatProvider } from '../context/ChatContext';
import { KnowledgeProvider } from '../context/KnowledgeContext';
import { Sidebar, TopBar } from '../components';

const AppShell: React.FC = () => {
  return (
    <ChatProvider>
      <KnowledgeProvider>
        <div className="app-root" style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
          <Sidebar />
          <div
            className="main-content"
            style={{ 
              flex: 1, 
              display: 'flex', 
              flexDirection: 'column', 
              minWidth: 0,
              overflow: 'hidden'
            }}
          >
            <TopBar />
            <div style={{ 
              flex: 1, 
              display: 'flex', 
              flexDirection: 'column', 
              minHeight: 0,
              overflow: 'hidden'
            }}>
              <Outlet />
            </div>
          </div>
        </div>
      </KnowledgeProvider>
    </ChatProvider>
  );
};

export default AppShell;