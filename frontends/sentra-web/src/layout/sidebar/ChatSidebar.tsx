import SidebarSection from "./Shared/SidebarSection";
import SidebarItem from "./Shared/SidebarItem";
import { PlusCircle } from "lucide-react";
import { useSessions } from "@features/sessions/useSessions";
import { useNavigate, useLocation } from "react-router-dom";
import { SessionItem } from "@features/sessions/SessionItem";

export default function ChatSidebar() {
  const { sessions, currentSessionId, select, clear, loadingList, regenerateTitle } =
    useSessions();

  const navigate = useNavigate();
  const { pathname } = useLocation();

  const handleNewChat = () => {
    // If we're already in `/c`, just reset state
    if (pathname === "/c") {
      clear();
      // Input and UI will already react to this
    } else {
      clear();
      navigate("/c");
    }
  };

  const handleSelect = (id: string) => {
    select(id);
    navigate(`/c/${id}`);
  };

  return (
    <SidebarSection title="Sessions">
      <SidebarItem icon={PlusCircle} label="New chat" onClick={handleNewChat} />

      {loadingList && (
        <div className="px-3 py-2 text-sm text-[var(--sentra-neutral)]">Loading...</div>
      )}



      {/* 🎯 Scrollable container */}
      <div className="overflow-y-auto max-h-[calc(100vh-350px)] pr-1">
        <ul className="conversation-list space-y-1">
          {sessions.map((conv) => (
            <SessionItem
              key={conv.id}
              id={conv.id}
              title={conv.title || "Untitled"}
              active={conv.id === currentSessionId}
              onSelect={handleSelect}
              onRename={(id) => console.log("Rename", id)}
              onDelete={(id) => console.log("Delete", id)}
              onRegenerate={(id) => regenerateTitle(id)}
            />
          ))}
        </ul>
      </div>
    </SidebarSection>
  );
}
