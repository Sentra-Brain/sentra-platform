// src/components/Sidebar.tsx
import React, { useState } from 'react';
import { useChat } from '../hooks/useChat';
import { ChevronLeft, ChevronRight } from 'lucide-react';
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
                key={conv.conversation_id}
                className={`conversation-item ${
                  currentConversation?.conversation_id === conv.conversation_id ? 'active' : ''
                }`}
                onClick={() => selectConversation(conv.conversation_id)}
              >
                {conv.title || 'Untitled'}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="sidebar-footer">
        <UserMenu />
      </div>
    </aside>
  );
};

export default Sidebar;
