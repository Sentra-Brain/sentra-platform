import { useAuth } from '../context/useAuth';
import { useState, useEffect, useRef } from 'react';
import { LogOut, Settings, LayoutDashboard, UserCircle } from 'lucide-react';
import './UserMenu.css';

interface UserMenuProps {
  collapsed?: boolean;
}

export default function UserMenu({ collapsed = false }: UserMenuProps) {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }

    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [open]);

  if (!user) return null;

  const handleLogout = () => {
    logout();
    setOpen(false);
  };

  return (
    <div className={`user-menu ${collapsed ? 'collapsed' : ''}`} ref={menuRef}>
      <button 
        className="user-menu-trigger" 
        onClick={() => setOpen(!open)}
        title={collapsed ? user.full_name || user.email : ''}
      >
        <UserCircle size={24} />
        {!collapsed && <span className="user-name">{user.full_name || user.email}</span>}
      </button>

      {open && (
        <div className="user-menu-dropdown">
          <div className="user-info">
            <div className="user-avatar">
              <UserCircle size={32} />
            </div>
            <div className="user-details">
              <div className="user-full-name">{user.full_name || 'User'}</div>
              <div className="user-email">{user.email}</div>
            </div>
          </div>
          <div className="menu-separator"></div>
          <button className="menu-item">
            <LayoutDashboard size={16} /> Manage Sentra
          </button>
          <button className="menu-item">
            <Settings size={16} /> Settings
          </button>
          <div className="menu-separator"></div>
          <button className="menu-item" onClick={handleLogout}>
            <LogOut size={16} /> Log out
          </button>
        </div>
      )}
    </div>
  );
}
