// src/layout/GlobalTopBar.tsx
import { UserCircle } from "lucide-react";
import { useLocation } from "react-router-dom";
import { useAppSelector } from "@store/hooks";

import SearchInput from "@features/search/SearchInput";
// import GlobalMenuPanel from './GlobalMenuPanel';

export default function GlobalTopBar() {
  const location = useLocation();
  const user = useAppSelector((s) => s.auth.user);

  const getBreadcrumb = () => {
    const path = location.pathname;
    if (path.startsWith("/c")) return "Sentra / Chat";
    if (path.startsWith("/k")) return "Sentra / Knowledge";
    if (path.startsWith("/prompts")) return "Sentra / Prompts";
    if (path.startsWith("/skills")) return "Sentra / Skills";
    if (path.startsWith("/settings")) return "Sentra / Settings";
    return "Sentra";
  };

  return (
    <header
      className="
        fixed top-0 left-0 right-0 z-50 h-14 
        flex items-center justify-between 
        px-4 border-b shadow 
        bg-[var(--sentra-primary-dark)] 
        border-[var(--sentra-primary)]
      "
    >
      {/* Left */}
      <div className="flex items-center gap-4 flex-shrink-0 min-w-0">
        {/* <button
          onClick={onToggleSidebar}
          title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          className="
            p-2 rounded transition hover:bg-[var(--sentra-primary)]
            focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sentra-accent)]
            text-[var(--sentra-text)]
          "
        >
          <Menu size={20} />
        </button> */}

        <img
          src="/sentra_brain_logo_64.png"
          alt="Sentra Logo"
          className="w-7 h-7 object-contain"
        />

        <span className="text-sm font-medium text-[var(--sentra-text)] whitespace-nowrap hidden sm:inline">
          {getBreadcrumb()}
        </span>
      </div>

      {/* Center */}
      <div className="flex-1 flex justify-center px-2 max-w-[600px]">
        <SearchInput />
      </div>

      {/* Right */}
      <div className="flex items-center gap-3 flex-shrink-0">
        {user && (
          <div
            title={user.full_name || user.email}
            className="
              p-1 rounded-full hover:bg-[var(--sentra-primary)]
              cursor-pointer transition
            "
          >
            <UserCircle size={24} className="text-[var(--sentra-text)]" />
          </div>
        )}
      </div>
    </header>
  );
}
