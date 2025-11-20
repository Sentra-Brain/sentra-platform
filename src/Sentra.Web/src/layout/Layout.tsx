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
    <div className="h-screen w-screen flex flex-col bg-sentra-primary text-sentra-text">
      {/* Top Bar */}
      <GlobalTopBar />

      {/* Main area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <SidebarLayout collapsed={sidebarCollapsed} onToggle={toggleSidebar} />

        {/* Scrollable content area */}
        <main className="flex-1 overflow-y-auto p-4">
          {children}
        </main>
      </div>
    </div>
  );
}