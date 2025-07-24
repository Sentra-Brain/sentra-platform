// src/components/Sidebar.tsx
import React, { useState } from 'react';
import { useChat } from '../hooks/useChat';
import { ChevronLeft, MessageSquare, BookOpen, Edit3, Wrench, Settings } from 'lucide-react';
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
        <div className="sidebar-logo">
          <img src="/sentra_brain_logo_64.png" alt="Sentra Brain Logo" />
          {!collapsed && <span className="logo-tooltip">Open sidebar</span>}
        </div>
        {!collapsed && (
          <button
            className="sidebar-toggle"
            onClick={() => setCollapsed((c) => !c)}
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            <ChevronLeft size={18} />
          </button>
        )}
      </div>

      <div id="sidebar-content" className="sidebar-content">
        {/* Navigation Menu - Always visible */}
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
                      title={collapsed ? item.label : ''}
                    >
                      <Icon size={16} />
                      {!collapsed && <span>{item.label}</span>}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>
        </div>

        {/* Chat Section - only show on chat routes and when expanded */}
        {!collapsed && (location.pathname === '/chat' || location.pathname.startsWith('/c/')) && (
          <>
            <div className="sidebar-header">
              <button
                className="new-conv-btn"
                onClick={() => createConversation({ content: 'Hello, I need help with something.' })}
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

      {/* Hover area for expansion when collapsed */}
      {collapsed && (
        <div 
          className="sidebar-hover-expand"
          onMouseEnter={() => setCollapsed(false)}
        />
      )}

      <div className="sidebar-footer">
        <UserMenu collapsed={collapsed} />
      </div>
    </aside>
  );
};

export default Sidebar;
