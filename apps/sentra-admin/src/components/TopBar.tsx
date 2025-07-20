// src/components/TopBar.tsx
import { useAuth } from '../context/useAuth';
import { MoreVertical, LogOut } from 'lucide-react';
import { useState } from 'react';
import './TopBar.css';

export default function TopBar() {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  if (!user) throw new Error('TopBar: user unexpectedly null');

  return (
    <header className="topbar">
      <div className="topbar-left">
        <span className="topbar-title">Sentra Brain – Admin Site</span>
      </div>

      <div className="topbar-right">
        <span className="topbar-user">👤 {user.username}</span>

        <div className="menu-container">
          <button
            className="menu-toggle-btn"
            onClick={() => setMenuOpen(!menuOpen)}
            title="Admin menu"
          >
            <MoreVertical size={20} />
          </button>

          {menuOpen && (
            <div className="topbar-menu">
              <button onClick={logout}>
                <LogOut size={16} /> Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
