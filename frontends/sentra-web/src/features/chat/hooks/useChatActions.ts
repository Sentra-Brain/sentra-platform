// src/features/chat/hooks/useChatActions.ts
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
  updateEvent,
  setStreaming,
  setWaitingForAnswer,
} from "@features/chat/eventsSlice";
import { chatService } from "@features/chat/chatService";
import { SentraEventType, type SentraEvent } from "@features/chat/types/events";

export function useChatActions() {
  const dispatch = useAppDispatch();
  const currentConversationId = useAppSelector((s) => s.conversation.currentConversationId);
  const { selectedContext, mode } = useAppSelector((s) => s.events);
  const selectedAgent = useAppSelector((s) => s.agents.selected);

  const sendMessage = async (content: string) => {
    const trimmed = content.trim();
    if (!trimmed) return;

    let conversationId = currentConversationId;

    // Step 1: ensure conversation exists
    if (!conversationId) {
      const newConversation = await dispatch(
        createConversation({ initial_prompt: trimmed, agent: selectedAgent || undefined })
      ).unwrap();
      conversationId = newConversation.id;
      dispatch(selectConversation(conversationId));
      await dispatch(fetchConversationById(conversationId));
    }

    // Step 2: add local user event
    const userEvent: SentraEvent = {
      id: uuidv4(),
      type: SentraEventType.MESSAGE_FINAL,
      author: "user",
      content: { role: "user", parts: [{ text: trimmed }] },
      timestamp: new Date().toISOString(),
    };
    dispatch(addEvent(userEvent));

    dispatch(setStreaming(true));
    dispatch(setWaitingForAnswer(true));

    // Step 3: send message to API
    chatService.sendMessageStream(
      {
        session_id: conversationId!,
        event_id: userEvent.id, // optional
        content: trimmed,
        context_source_ids: selectedContext.useRag
          ? selectedContext.sourceIds
          : [],
        context_document_ids: selectedContext.useRag
          ? selectedContext.documentIds
          : [],
        mode,
        agent: selectedAgent || undefined,
      },
      (event: SentraEvent) => {
        dispatch(updateEvent(event));
        if (event.type === SentraEventType.MESSAGE_FINAL) {
          dispatch(setWaitingForAnswer(false));
          dispatch(setStreaming(false));
          if (!currentConversationId) {
            dispatch(regenerateTitle(conversationId!)).catch(console.warn);
          }
        }
      },
      (err) => {
        console.error("Streaming error:", err);
        dispatch(setWaitingForAnswer(false));
        dispatch(setStreaming(false));
      }
    );
  };

  return { sendMessage };
}
