import SidebarSection from "./Shared/SidebarSection";
import SidebarItem from "./Shared/SidebarItem";
import { PlusCircle } from "lucide-react";
import { useConversations } from "@features/conversations/useConversations";
import { useNavigate, useLocation } from "react-router-dom";
import { ConversationItem } from "@features/conversations/ConversationItem";

export default function ChatSidebar() {
  const { conversations, currentConversationId, select, clear, loadingList, regenerateTitle } =
    useConversations();

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
    <SidebarSection title="Conversations">
      <SidebarItem icon={PlusCircle} label="New chat" onClick={handleNewChat} />

      {loadingList && (
        <div className="px-3 py-2 text-sm text-[var(--sentra-neutral)]">Loading...</div>
      )}



      {/* 🎯 Scrollable container */}
      <div className="overflow-y-auto max-h-[calc(100vh-350px)] pr-1">
        <ul className="conversation-list space-y-1">
          {conversations.map((conv) => (
            <ConversationItem
              key={conv.id}
              id={conv.id}
              title={conv.title || "Untitled"}
              active={conv.id === currentConversationId}
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
