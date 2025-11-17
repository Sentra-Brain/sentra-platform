// src/features/chat/hooks/useChatActions.ts
import { useRef } from "react";
import { useAppDispatch, useAppSelector } from "@store/hooks";
import { v4 as uuidv4 } from "uuid";
import {
  createConversation,
  selectConversation,
  fetchConversationById,
  regenerateTitle,
} from "@features/conversations/conversationsSlice";
import {
  addEvent,
  setStreaming,
  setWaitingForAnswer,
  type AGUIEvent,
} from "@features/chat/eventsSlice";
import { chatService } from "@features/chat/chatService";
import { EventType } from "@ag-ui/core";
import { createCompletedMessageEvents } from "@features/chat/utils/aguiMessages";

export function useChatActions() {
  const dispatch = useAppDispatch();
  const abortRef = useRef<(() => void) | null>(null);
  const currentConversationId = useAppSelector((s) => s.conversation.currentConversationId);
  const { selectedContext, mode } = useAppSelector((s) => s.events);
  const selectedAgent = useAppSelector((s) => s.agents.selected);

  const cancelActiveStream = () => {
    if (abortRef.current) {
      abortRef.current();
      abortRef.current = null;
    }
  };

  const stopStreaming = () => {
    cancelActiveStream();
    dispatch(setWaitingForAnswer(false));
    dispatch(setStreaming(false));
  };

  const sendMessage = async (content: string) => {
    const trimmed = content.trim();
    if (!trimmed) return;

    let conversationId = currentConversationId;

    // Step 1: ensure conversation exists
    if (!conversationId) {
      const newConversation = await dispatch(
        createConversation({ initial_prompt: trimmed, agent: selectedAgent?.key || undefined })
      ).unwrap();
      conversationId = newConversation.id;
      dispatch(selectConversation(conversationId));
      await dispatch(fetchConversationById(conversationId));
    }

    // Step 2: add local user event
    const userMessageId = uuidv4();
    createCompletedMessageEvents(userMessageId, "user", trimmed).forEach((event) =>
      dispatch(addEvent(event))
    );

    dispatch(setStreaming(true));
    dispatch(setWaitingForAnswer(true));

    // Step 3: send message to API
    cancelActiveStream();
    abortRef.current = chatService.sendMessageStream(
      {
        threadId: conversationId!,
        messageId: userMessageId,
        content: trimmed,
        contextSourceIds: selectedContext.useRag
          ? selectedContext.sourceIds
          : [],
        contextDocumentIds: selectedContext.useRag
          ? selectedContext.documentIds
          : [],
        mode,
        agent: selectedAgent?.key || undefined,
      },
      (event) => {
        dispatch(addEvent(event as AGUIEvent));
        if (event.type === EventType.RUN_FINISHED) {
          stopStreaming();
          if (!currentConversationId) {
            dispatch(regenerateTitle(conversationId!)).catch(console.warn);
          }
        }
        if (event.type === EventType.RUN_ERROR) {
          stopStreaming();
        }
      },
      (err) => {
        console.error("Streaming error:", err);
        dispatch(
          addEvent({
            type: EventType.RUN_ERROR,
            message: err.message,
          })
        );
        stopStreaming();
      }
    );
  };

  return { sendMessage, stopStreaming };
}
