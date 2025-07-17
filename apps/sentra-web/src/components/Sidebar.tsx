
import React, { useState } from 'react';
import { useChat } from '../context/ChatContext';
import './Sidebar.css';

const Sidebar: React.FC = () => {
  const { conversations, currentConversationId, setCurrentConversationId, newConversation } = useChat();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className={`sidebar${collapsed ? ' collapsed' : ''}`}> 
      <div className="sidebar-top-row">
        <button className="sidebar-toggle" onClick={() => setCollapsed(c => !c)} title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}>
          <span>{collapsed ? '→' : '←'}</span>
        </button>
        {!collapsed && (
          <div className="sidebar-title" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginBottom: '2rem' }}>
            <img src="/sentra_brain_logo_64.png" alt="Sentra Brain Logo" style={{ width: 48, height: 48 }} />
          </div>
        )}
      </div>
      <div style={{ display: collapsed ? 'none' : 'block', flex: 1, minHeight: 0 }}>
        <div className="sidebar-header">
          <button className="new-conv-btn" onClick={newConversation}>+ New Chat</button>
        </div>
        <ul className="conversation-list">
          {conversations.map(conv => (
            <li
              key={conv.id}
              className={conv.id === currentConversationId ? 'active' : ''}
              onClick={() => setCurrentConversationId(conv.id)}
            >
              {conv.name}
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
};

export default Sidebar;
