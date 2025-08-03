// features/chat/components/ChatInputContainer.tsx
import { useState, useRef } from "react";
import {
  Plus,
  Settings,
  Mic,
  Send,
  X,
  ChevronDown,
  Paperclip,
} from "lucide-react";
import { v4 as uuidv4 } from "uuid";
import { useAppDispatch, useAppSelector } from "@store/hooks";
import { chatService } from "../chatService";
import { setStreaming, setWaitingForAnswer } from "@features/chat/chatSlice";

export default function ChatInputContainer() {
  const [value, setValue] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const dispatch = useAppDispatch();
  const isStreaming = useAppSelector((s) => s.chat.isStreaming);
  const conversationId = useAppSelector(
    (s) => s.conversation.currentConversationId
  );

  const handleSend = async () => {
    const content = value.trim();
    console.log("[SEND] Triggered", { content, conversationId, isStreaming });

    if (!content || !conversationId || isStreaming) {
      console.log("[SEND] Aborted — Invalid input or streaming in progress");
      return;
    }

    const userMessageId = uuidv4();
    const assistantMessageId = uuidv4();

    dispatch(setStreaming(true));
    dispatch(setWaitingForAnswer(true));

    try {
      console.log("[SEND] Calling chatService.sendMessageStream()");
      chatService.sendMessageStream(
        {
          conversation_id: conversationId,
          content,
          message_id: userMessageId,
          response_message_id: assistantMessageId,
        },
        (chunk) => {
          console.log("[STREAM] Received chunk:", chunk);
        },
        (error) => {
          console.error("[STREAM] Error:", error);
        }
      );
      setValue("");
    } catch (err) {
      console.error("[SEND] Failed:", err);
    } finally {
      dispatch(setStreaming(false));
      dispatch(setWaitingForAnswer(false));
    }
  };

  const handleKeyDown = async (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      await handleSend();
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Placeholder for future file support
    e.target.value = "";
  };

  const handleStop = () => {
    dispatch(setStreaming(false));
  };

  return (
    <div className="w-full max-w-[768px] bg-[var(--sentra-primary-dark)] border border-[var(--sentra-accent-light)] rounded-xl px-4 py-3 shadow-md flex items-end gap-2">
      <button className="icon-btn" disabled title="Coming soon">
        <Plus size={18} />
      </button>

      <button className="icon-btn" disabled title="Coming soon">
        <Paperclip size={18} />
      </button>

      <button className="icon-btn" disabled title="Tools (coming soon)">
        <Settings size={18} />
      </button>

      <div className="flex-1">
        <textarea
          className="w-full resize-none bg-transparent text-[var(--sentra-text)] placeholder-[var(--sentra-muted)] focus:outline-none"
          rows={1}
          placeholder={
            conversationId
              ? "Type a message..."
              : "Ask anything to start a new conversation..."
          }
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isStreaming}
        />
      </div>

      <input
        type="file"
        ref={fileInputRef}
        hidden
        onChange={handleFileUpload}
      />

      <button className="icon-btn" disabled title="Dictate (coming soon)">
        <Mic size={18} />
      </button>

      {isStreaming ? (
        <button className="icon-btn" onClick={handleStop} title="Stop">
          <X size={18} />
        </button>
      ) : (
        <button
          className="icon-btn send"
          onClick={handleSend}
          title="Send"
          disabled={!value.trim() || isStreaming}
        >
          <Send size={18} />
        </button>
      )}

      <button className="icon-btn" title="Scroll to bottom">
        <ChevronDown size={20} />
      </button>
    </div>
  );
}
