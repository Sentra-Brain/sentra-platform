import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { ChatProvider } from '../context/ChatContext';
import { Sidebar } from '../components';
import GlobalTopBar from '../components/GlobalTopBar';

const AppShell: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    setSidebarCollapsed(prev => !prev);
  };

  return (
    <ChatProvider>
      <div className="app-root" style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
        <GlobalTopBar 
          sidebarCollapsed={sidebarCollapsed} 
          onToggleSidebar={toggleSidebar} 
        />
        <Sidebar collapsed={sidebarCollapsed} onToggle={toggleSidebar} />
        <div
          className="main-content"
          style={{ 
            flex: 1, 
            display: 'flex', 
            flexDirection: 'column', 
            minWidth: 0,
            overflow: 'hidden',
            marginTop: '56px' // Account for global top bar height
            }}
          >
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
    </ChatProvider>
  );
};

export default AppShell;