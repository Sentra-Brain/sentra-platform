// features/chat/ChatPage.tsx
import { useAppSelector } from "@store/hooks";
import ChatContent from "./components/ChatContent";
import ChatFooter from "./components/ChatFooter";
import ChatInputContainer from "./components/ChatInputContainer";

import { useEffect } from "react";
import { useAppDispatch } from "@store/hooks";
import { fetchConversationById } from "@features/conversations/conversationsSlice";
import type { ConversationDetails } from "@features/conversations/types/conversationModels";
import { addEvent, resetEvents } from "./eventsSlice";
import { SentraEventType } from "./types/events";

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
            dispatch(resetEvents());
            payload.messages.forEach(m => {
              dispatch(addEvent({
                id: m.id,
                type: SentraEventType.MESSAGE_FINAL,
                author: m.role,
                content: { role: m.role, parts: [{ text: m.content }] },
                timestamp: new Date(m.timestamp).toISOString(),
              }))
            });
          }
        });
      }
    }, [currentConversationId, dispatch]);

    const isConversationActive = !!currentConversationId;

  return (
    <div className="flex flex-col h-full w-full min-h-0">
      {isConversationActive ? (
        <>
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
