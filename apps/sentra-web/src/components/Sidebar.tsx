
import React from 'react';
import { useChat } from '../context/ChatContext';
import './Sidebar.css';

const Sidebar: React.FC = () => {
  const { conversations, currentConversationId, setCurrentConversationId, newConversation } = useChat();

  return (
    <aside className="sidebar">
      <div className="sidebar-title" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginBottom: '2rem' }}>
        <img src="/sentra_brain_logo_64.png" alt="Sentra Brain Logo" style={{ width: 48, height: 48 }} />
      </div>
      <div className="sidebar-header">
        <button className="new-conv-btn" onClick={newConversation}>+ New Conversation</button>
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
    </aside>
  );
};

export default Sidebar;
