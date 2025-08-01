import { useLocation } from "react-router-dom";
import {
  MessageSquare,
  BookOpen,
  Settings as SettingsIcon,
} from "lucide-react";
import { Link } from "react-router-dom";
import ChatSidebar from "./sidebar/ChatSidebar";
import KnowledgeSidebar from "./sidebar/KnowledgeSidebar";
import SettingsSidebar from "./sidebar/SettingsSidebar";
// import UserMenu from './UserMenu'

interface SidebarLayoutProps {
  collapsed: boolean;
  onToggle: () => void;
}

export default function SidebarLayout({
  collapsed,
  onToggle,
}: SidebarLayoutProps) {
  const { pathname } = useLocation();

  const navItems = [
    { path: "/c", icon: MessageSquare, label: "Chat" },
    { path: "/k", icon: BookOpen, label: "Knowledge" },
    { path: "/s", icon: SettingsIcon, label: "Settings" },
  ];

  const renderContextualSidebar = () => {
    if (pathname.startsWith("/c")) return <ChatSidebar />;
    if (pathname.startsWith("/k")) return <KnowledgeSidebar />;
    if (pathname.startsWith("/s")) return <SettingsSidebar />;
    return null;
  };

  return (
    <aside
      className={`sidebar ${
        collapsed ? "collapsed" : ""
      } bg-sentra-primary-dark text-white transition-all duration-200`}
    >
      {/* Top: Logo + toggle */}
      <div className="flex items-center justify-end  px-3 py-2">
        <button onClick={onToggle} className="text-sm">
          {collapsed ? "⯈" : "⯇"}
        </button>
      </div>
      {/* Navigation */}
      <nav className="sidebar-navigation">
        {navItems.map(({ path, icon: Icon, label }) => {
          const isActive =
            pathname === path || pathname.startsWith(path.slice(0, 2)); // crude matching
          return (
            <Link
              key={path}
              to={path}
              className={`flex items-center px-2 py-2 rounded-md text-sm font-medium ${
                isActive
                  ? "bg-sentra-accent text-white"
                  : "hover:bg-sentra-accent-light text-gray-300"
              }`}
            >
              <Icon className="w-4 h-4 mr-2" />
              {!collapsed && <span>{label}</span>}
            </Link>
          );
        })}
      </nav>
      {/* Contextual Sidebar */}
      {!collapsed && (
        <div className="flex-1 overflow-y-auto mt-4 px-2">
          {renderContextualSidebar()}
        </div>
      )}
      {/* Footer */}
      <div className="p-2 mt-auto">
        {/* <UserMenu collapsed={collapsed} /> */}
      </div>
    </aside>
  );
}
