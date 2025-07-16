// ...existing code...
const navItems = [
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Users', path: '/users' },
  { name: 'Settings', path: '/settings' },
];

import { NavLink } from 'react-router-dom';

const Sidebar: React.FC = () => (
  <aside className="sidebar">
    <div className="sidebar-title" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginBottom: '2rem' }}>
      <img src="/sentra_brain_logo_64.png" alt="Sentra Brain Logo" style={{ width: 48, height: 48 }} />
    </div>
    <ul className="sidebar-nav">
      {navItems.map(item => (
        <li key={item.path}>
          <NavLink
            to={item.path}
            className={({ isActive }: { isActive: boolean }) =>
              isActive ? 'active' : ''
            }
          >
            {item.name}
          </NavLink>
        </li>
      ))}
    </ul>
  </aside>
);

export default Sidebar;
