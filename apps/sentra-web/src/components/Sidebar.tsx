// src/components/Sidebar.tsx
import React, { useState } from 'react';
import { useChat } from '../hooks/useChat';
import { ChevronLeft, ChevronRight, MessageSquare, BookOpen, Edit3, Wrench, Settings } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import UserMenu from './UserMenu';
import './Sidebar.css';

const Sidebar: React.FC = () => {
  const {
    conversations,
    currentConversation,
    selectConversation,
    createConversation,
  } = useChat();
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  const navigationItems = [
    { path: '/chat', label: 'Chat', icon: MessageSquare },
    { path: '/knowledge', label: 'Knowledge', icon: BookOpen },
    { path: '/prompts', label: 'Prompts', icon: Edit3 },
    { path: '/skills', label: 'Skills', icon: Wrench },
    { path: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-top-row">
        {!collapsed && (
          <div className="sidebar-logo">
            <img src="/sentra_brain_logo_64.png" alt="Sentra Brain Logo" />
          </div>
        )}
        <button
          className="sidebar-toggle"
          onClick={() => setCollapsed((c) => !c)}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      {!collapsed && (
        <div id="sidebar-content" className="sidebar-content">
          {/* Navigation Menu */}
          <div className="sidebar-navigation">
            <nav>
              <ul className="navigation-list">
                {navigationItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path || 
                    (item.path === '/chat' && location.pathname.startsWith('/c/'));
                  
                  return (
                    <li key={item.path}>
                      <Link
                        to={item.path}
                        className={`navigation-item ${isActive ? 'active' : ''}`}
                      >
                        <Icon size={16} />
                        <span>{item.label}</span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </nav>
          </div>

          {/* Chat Section - only show on chat routes */}
          {(location.pathname === '/chat' || location.pathname.startsWith('/c/')) && (
            <>
              <div className="sidebar-header">
                <button
                  className="new-conv-btn"
                  onClick={() => createConversation({ content: 'Hi!' })}
                >
                  + New Chat
                </button>
              </div>
              <ul className="conversation-list">
                {conversations.map((conv) => (
                  <li
                    key={conv.id}
                    className={`conversation-item ${
                      currentConversation?.id === conv.id ? 'active' : ''
                    }`}
                    onClick={() => selectConversation(conv.id)}
                  >
                    {conv.title || 'Untitled'}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}

      <div className="sidebar-footer">
        <UserMenu />
      </div>
    </aside>
  );
};

export default Sidebar;
