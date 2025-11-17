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
import { createCompletedMessageEvents } from "./utils/aguiMessages";
import type { Role } from "@ag-ui/core";
import type { MessageRole } from "@features/conversations/types/conversationModels";

const toAGUIRole = (role: MessageRole): Role => {
  switch (role) {
    case "user":
    case "system":
    case "assistant":
      return role;
    default:
      return "assistant";
  }
};

export default function ChatPage() {
  const dispatch = useAppDispatch();
  const currentConversationId = useAppSelector(
      (state) => state.conversation.currentConversationId
    );

  useEffect(() => {
    if (currentConversationId) {
      dispatch(resetEvents());
      dispatch(fetchConversationById(currentConversationId)).then((res) => {
        const payload = res.payload as ConversationDetails;
        payload?.messages?.forEach((message) => {
          createCompletedMessageEvents(
            message.id,
            toAGUIRole(message.role),
            message.content,
            message.timestamp,
          ).forEach((event) => dispatch(addEvent(event)));
        });
      });
    } else {
      dispatch(resetEvents());
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
