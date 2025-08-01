// src/components/Sidebar.tsx
import React, { useState } from 'react';
import { useChat } from '../hooks/useChat';
import { MessageSquare, BookOpen, Edit3, Wrench, Settings, PanelLeftClose, PanelLeftOpen, Plus, MoreVertical } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import UserMenu from './UserMenu';
import './Sidebar.css';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const {
    conversations,
    currentConversation,
    selectConversation,
    createConversation,
  } = useChat();
  const [conversationMenuOpen, setConversationMenuOpen] = useState<string | null>(null);
  const location = useLocation();

  const navigationItems = [
    { path: '/chat', label: 'Chat', icon: MessageSquare },
    { path: '/knowledge', label: 'Knowledge', icon: BookOpen },
    { path: '/prompts', label: 'Prompts', icon: Edit3 },
    { path: '/skills', label: 'Skills', icon: Wrench },
    { path: '/settings', label: 'Settings', icon: Settings },
  ];

  const handleNewConversation = () => {
    createConversation({ content: '' });
  };

  const handleConversationMenuClick = (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setConversationMenuOpen(conversationMenuOpen === conversationId ? null : conversationId);
  };

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-top-row">
        <div className="sidebar-logo">
          <img src="/sentra_brain_logo_64.png" alt="Sentra Brain Logo" />
        </div>
        {!collapsed && (
          <button
            className="sidebar-toggle-internal"
            onClick={onToggle}
            title="Collapse sidebar"
            aria-label="Collapse sidebar"
          >
            <PanelLeftClose size={16} />
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
                className="new-conv-btn secondary"
                onClick={handleNewConversation}
                aria-label="Start new conversation"
              >
                <Plus size={16} />
                <span>New Conversation</span>
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
                  <span className="conversation-title">
                    {conv.title || 'Untitled'}
                  </span>
                  <button
                    className="conversation-menu-btn"
                    onClick={(e) => handleConversationMenuClick(conv.id, e)}
                    title="Conversation options"
                    aria-label="Conversation options"
                  >
                    <MoreVertical size={14} />
                  </button>
                  
                  {conversationMenuOpen === conv.id && (
                    <div className="conversation-dropdown">
                      <button onClick={() => {
                        console.log('Rename conversation:', conv.id);
                        setConversationMenuOpen(null);
                      }}>
                        Rename
                      </button>
                      <button onClick={() => {
                        console.log('Delete conversation:', conv.id);
                        setConversationMenuOpen(null);
                      }} className="danger">
                        Delete
                      </button>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </>
        )}
      </div>

      {/* Expand button when collapsed */}
      {collapsed && (
        <div className="sidebar-expand-section">
          <button
            className="sidebar-expand-btn"
            onClick={onToggle}
            title="Expand sidebar"
            aria-label="Expand sidebar"
          >
            <PanelLeftOpen size={16} />
          </button>
        </div>
      )}

      <div className="sidebar-footer">
        <UserMenu collapsed={collapsed} />
      </div>
    </aside>
  );
};

export default Sidebar;
