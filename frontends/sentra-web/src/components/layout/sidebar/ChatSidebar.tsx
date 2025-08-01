import SidebarSection from "./Shared/SidebarSection";
import SidebarItem from "./Shared/SidebarItem";
import { PlusCircle } from "lucide-react";

export default function ChatSidebar() {
  return (
    <>
      <SidebarSection title="Conversations">
        <SidebarItem icon={PlusCircle} label="New chat" />
        {/* TODO: Render list of conversations */}
      </SidebarSection>
    </>
  );
}
