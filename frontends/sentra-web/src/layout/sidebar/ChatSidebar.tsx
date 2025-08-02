import SidebarSection from "./Shared/SidebarSection";
import SidebarItem from "./Shared/SidebarItem";
import { PlusCircle } from "lucide-react";
import { useConversations } from "@features/conversations/useConversations";
import { useNavigate, useLocation } from "react-router-dom";
import { ConversationItem } from "./ConversationItem";

export default function ChatSidebar() {
  const { conversations, currentConversationId, select, clear, loadingList } =
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
        <div className="px-3 py-2 text-sm text-gray-400">Loading...</div>
      )}

      <ul className="conversation-list">
        {conversations.map((conv) => (
          <ConversationItem
            key={conv.id}
            id={conv.id}
            title={conv.title || "Untitled"}
            active={conv.id === currentConversationId}
            onSelect={handleSelect}
            onRename={(id) => console.log("Rename", id)}
            onDelete={(id) => console.log("Delete", id)}
          />
        ))}
      </ul>
    </SidebarSection>
  );
}
