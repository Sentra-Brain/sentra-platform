import { useAuth } from '../context/useAuth';
import { useState } from 'react';
import { LogOut, Settings, LayoutDashboard, UserCircle } from 'lucide-react';
import './UserMenu.css';

export default function UserMenu() {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);

  if (!user) return null;

  return (
    <div className="user-menu">
      <button className="user-menu-trigger" onClick={() => setOpen(!open)}>
        <span title={user.full_name}>
          <UserCircle size={24} />
        </span>{' '}
        {/* <span>{user.full_name || user.email}</span> */}
      </button>

      {open && (
        <div className="user-menu-dropdown">
          <button>
            <LayoutDashboard size={16} /> Manage Sentra
          </button>
          <button>
            <Settings size={16} /> Settings
          </button>
          <button>
            <LogOut size={16} /> Log out
          </button>
        </div>
      )}
    </div>
  );
}
