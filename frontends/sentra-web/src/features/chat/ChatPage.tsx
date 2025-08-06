// features/chat/ChatPage.tsx
import { useAppSelector } from "@store/hooks";
import ChatHeader from "./components/ChatHeader";
import ChatContent from "./components/ChatContent";
import ChatFooter from "./components/ChatFooter";
import ChatInputContainer from "./components/ChatInputContainer";

import { setMessages } from "./chatSlice";
import { useEffect } from "react";
import { useAppDispatch } from "@store/hooks";
import { fetchConversationById } from "@features/conversations/conversationSlice";
import type { ConversationDetails } from "@features/conversations/types/conversationModels";

export default function ChatPage() {
  const dispatch = useAppDispatch();
  const currentConversationId = useAppSelector(
    (state) => state.conversation.currentConversationId
  );

  useEffect(() => {
    if (currentConversationId) {
      dispatch(fetchConversationById(currentConversationId)).then((res) => {
        const payload = res.payload as ConversationDetails;
        if (payload?.messages) {
          // Filter out system messages that match user messages (to avoid duplication)
          const filteredMessages = payload.messages.filter((message, _, array) => {
            if (message.role === 'system') {
              // Check if there's a user message with the same content
              const hasMatchingUserMessage = array.some(
                (msg) => msg.role === 'user' && msg.content.trim() === message.content.trim()
              );
              return !hasMatchingUserMessage;
            }
            return true;
          });
          dispatch(setMessages(filteredMessages));
        }
      });
    }
  }, [currentConversationId, dispatch]);

  const isConversationActive = !!currentConversationId;

  return (
    <div className="flex flex-col h-full w-full min-h-0">
      {isConversationActive ? (
        <>
          <ChatHeader />
          <div className="flex-1 min-h-0 overflow-hidden flex flex-col">
            <ChatContent />
            <ChatFooter>
              <ChatInputContainer />
            </ChatFooter>
          </div>
        </>
      ) : (
        <div className="flex-1 flex items-center justify-center px-4">
          <ChatInputContainer />
        </div>
      )}
    </div>
  );
}
