// src/features/chat/hooks/useChatActions.ts
import { useAppDispatch, useAppSelector } from '@store/hooks'
import { v4 as uuidv4 } from 'uuid'
import {
  createSession,
  selectSession,
  fetchSessionById,
  regenerateTitle,
} from '@features/sessions/sessionsSlice'
import {
  addEvent,
  updateEvent,
  setStreaming,
  setWaitingForAnswer,
} from '@features/chat/eventsSlice'
import { chatService } from '@features/chat/chatService'
import type { SentraEvent } from '@features/chat/types/events'

export function useChatActions() {
  const dispatch = useAppDispatch()
  const currentSessionId = useAppSelector(s => s.session.currentSessionId)
  const userId = useAppSelector(s => s.auth.user?.id)
  const { selectedContext, mode } = useAppSelector(s => s.events)

  const sendMessage = async (content: string) => {
    const trimmed = content.trim()
    if (!trimmed) return

    let sessionId = currentSessionId
  const userEventId = uuidv4()
  const assistantEventId = uuidv4()

    const wasNewSession = !sessionId

    if (!sessionId) {
      const newSession = await dispatch(createSession({ initial_prompt: trimmed })).unwrap()
      sessionId = newSession.id
      dispatch(selectSession(sessionId))
      await dispatch(fetchSessionById(sessionId))
    }

    dispatch(setStreaming(true))
    dispatch(setWaitingForAnswer(true))

    dispatch(addEvent({
      event_id: userEventId,
      type: 'user_message',
      content: { parts: [{ text: trimmed }] },
      timestamp: new Date().toISOString(),
      assistant_event_id: assistantEventId,
    }))

    let titleTriggered = false

    chatService.sendMessageStream(
      {
        user_id: userId,
        session_id: sessionId!,
        event_id: userEventId,
        content: trimmed, // If backend expects string, keep as is. If not, wrap as above.
        context_source_ids: selectedContext.useRag ? selectedContext.sourceIds : [],
        context_document_ids: selectedContext.useRag ? selectedContext.documentIds : [],
        mode,
      },
  (event: SentraEvent) => {
        switch (event.type) {
          case 'message_delta': {
            dispatch(updateEvent({
              event_id: assistantEventId,
              type: 'message_delta',
              content: event.content
                ? typeof event.content === 'string'
                  ? { parts: [{ text: event.content }] }
                  : event.content
                : undefined,
              timestamp: event.timestamp,
            }))
            break
          }
          case 'message_final': {
            dispatch(updateEvent({
              event_id: assistantEventId,
              type: 'message_final',
              content: event.content
                ? typeof event.content === 'string'
                  ? { parts: [{ text: event.content }] }
                  : event.content
                : undefined,
              timestamp: event.timestamp,
            }))

            dispatch(setWaitingForAnswer(false))
            dispatch(setStreaming(false))

            if (wasNewSession && !titleTriggered) {
              titleTriggered = true
              dispatch(regenerateTitle(sessionId!)).catch(err => {
                console.warn('Failed to regenerate title', err)
              })
            }
            break
          }
          case 'step_start':
          case 'step_progress':
          case 'step_end':
          case 'step_error':
          case 'tool_call': {
            // normal step/tool events
            dispatch(addEvent({
              ...event,
              content: event.content
                ? typeof event.content === 'string'
                  ? { parts: [{ text: event.content }] }
                  : event.content
                : undefined,
            }))
            break
          }
          default:
            break
        }
      },
      (err) => {
        console.error('Streaming error:', err)
        dispatch(setWaitingForAnswer(false))
        dispatch(setStreaming(false))
      }
    )
  }

  return { sendMessage }
}

