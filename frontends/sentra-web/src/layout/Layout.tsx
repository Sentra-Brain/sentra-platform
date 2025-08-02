import { useState, type ReactNode } from "react";
import GlobalTopBar from "./GlobalTopBar";
import SidebarLayout from "./Sidebar";

interface Props {
  children: ReactNode;
}

export default function Layout({ children }: Props) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const toggleSidebar = () => setSidebarCollapsed((prev) => !prev);

  return (
    <div className="flex flex-col min-h-screen bg-sentra-primary text-sentra-text">
      {/* Always fixed at top */}
      <GlobalTopBar />

      {/* Content below topbar */}
      <div className="flex flex-1 pt-14">
        <SidebarLayout collapsed={sidebarCollapsed} onToggle={toggleSidebar} />
        <main className="flex-1 overflow-y-auto p-4">{children}</main>
      </div>
    </div>
  );
}
