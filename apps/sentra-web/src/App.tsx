import { ChatProvider } from "./context/ChatContext";
import { Sidebar, TopBar, ChatArea, MessageInput, SettingsModal } from "./components";
import { useState } from "react";

export default function App() {
  const [settingsOpen, setSettingsOpen] = useState(false);

  return (
    <ChatProvider>
      <div className="app-root" style={{ display: "flex", height: "100vh", width: "100vw" }}>
        <Sidebar />
        <div className="main-content" style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
          <TopBar onSettings={() => setSettingsOpen(true)} />
          <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
            <ChatArea />
          </div>
          <MessageInput />
        </div>
        <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
      </div>
    </ChatProvider>
  );
}
