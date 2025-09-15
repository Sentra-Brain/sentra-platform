// src/features/chat/hooks/useChatActions.ts
import { useAppDispatch, useAppSelector } from "@store/hooks";
import { v4 as uuidv4 } from "uuid";
import {
  createSession,
  selectSession,
  fetchSessionById,
  regenerateTitle,
} from "@features/sessions/sessionsSlice";
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
  const currentSessionId = useAppSelector((s) => s.session.currentSessionId);
  const { selectedContext, mode } = useAppSelector((s) => s.events);
  const selectedAgent = useAppSelector((s) => s.agents.selected);

  const sendMessage = async (content: string) => {
    const trimmed = content.trim();
    if (!trimmed) return;

    let sessionId = currentSessionId;

    // Step 1: ensure session exists
    if (!sessionId) {
      const newSession = await dispatch(
        createSession({ initial_prompt: trimmed, agent: selectedAgent || undefined })
      ).unwrap();
      sessionId = newSession.id;
      dispatch(selectSession(sessionId));
      await dispatch(fetchSessionById(sessionId));
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
        session_id: sessionId!,
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
          if (!currentSessionId) {
            dispatch(regenerateTitle(sessionId!)).catch(console.warn);
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
