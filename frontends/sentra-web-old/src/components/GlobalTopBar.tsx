import React, { useState } from 'react';
import { Menu, Search, UserCircle } from 'lucide-react';
import { useAuth } from '../context/useAuth';
import { useLocation } from 'react-router-dom';
import './GlobalTopBar.css';

interface GlobalTopBarProps {
  sidebarCollapsed: boolean;
  onToggleSidebar: () => void;
}

const GlobalTopBar: React.FC<GlobalTopBarProps> = ({ 
  sidebarCollapsed, 
  onToggleSidebar 
}) => {
  const { user } = useAuth();
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState('');

  // Generate breadcrumb based on current route
  const getBreadcrumb = () => {
    const path = location.pathname;
    if (path.startsWith('/chat') || path.startsWith('/c/')) {
      return 'Sentra / Chat';
    } else if (path.startsWith('/knowledge')) {
      return 'Sentra / Knowledge';
    } else if (path.startsWith('/prompts')) {
      return 'Sentra / Prompts';
    } else if (path.startsWith('/skills')) {
      return 'Sentra / Skills';
    } else if (path.startsWith('/settings')) {
      return 'Sentra / Settings';
    }
    return 'Sentra';
  };

  return (
    <header className="global-topbar">
      <div className="global-topbar-left">
        <button
          className="sidebar-toggle-btn"
          onClick={onToggleSidebar}
          title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <Menu size={20} />
        </button>
        
        <div className="logo-section">
          <img 
            src="/sentra_brain_logo_64.png" 
            alt="Sentra Brain Logo" 
            className="topbar-logo"
          />
        </div>
        
        <nav className="breadcrumb" aria-label="Breadcrumb">
          <span className="breadcrumb-text">{getBreadcrumb()}</span>
        </nav>
      </div>

      <div className="global-topbar-center">
        <div className="search-container">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
            aria-label="Global search"
          />
        </div>
      </div>

      <div className="global-topbar-right">
        <div className="user-section">
          {user && (
            <div className="user-avatar-container" title={user.full_name || user.email}>
              <UserCircle size={24} className="user-avatar" />
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default GlobalTopBar;