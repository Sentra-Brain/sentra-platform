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
import { SentraEventType, type SentraEvent } from '@features/chat/types/events'

export function useChatActions() {
  const dispatch = useAppDispatch()
  const currentSessionId = useAppSelector(s => s.session.currentSessionId)
  const userId = useAppSelector(s => s.auth.user?.id)
  const { selectedContext, mode } = useAppSelector(s => s.events)

  const sendMessage = async (content: string) => {
    const trimmed = content.trim()
    if (!trimmed) return

    let sessionId = currentSessionId
    const userEvent: SentraEvent = {
      id: uuidv4(),
      type: SentraEventType.MESSAGE_FINAL,
      author: 'user',
      content: { role: 'user', parts: [{ text: trimmed }] },
      timestamp: new Date().toISOString(),
    }

    const wasNewSession = !sessionId

    if (!sessionId) {
      const newSession = await dispatch(createSession({ initial_prompt: trimmed })).unwrap()
      sessionId = newSession.id
      dispatch(selectSession(sessionId))
      await dispatch(fetchSessionById(sessionId))
    }

    dispatch(setStreaming(true))
    dispatch(setWaitingForAnswer(true))

    dispatch(addEvent(userEvent))

    let titleTriggered = false

    chatService.sendMessageStream(
      {
        user_id: userId,
        session_id: sessionId!,
        id: userEvent.id,
        content: trimmed,
        context_source_ids: selectedContext.useRag ? selectedContext.sourceIds : [],
        context_document_ids: selectedContext.useRag ? selectedContext.documentIds : [],
        mode,
      },
      (event: SentraEvent) => {
        dispatch(updateEvent(event))
        if (event.type === SentraEventType.MESSAGE_FINAL) {
          dispatch(setWaitingForAnswer(false))
          dispatch(setStreaming(false))

          if (wasNewSession && !titleTriggered) {
            titleTriggered = true
            dispatch(regenerateTitle(sessionId!)).catch(err => {
              console.warn('Failed to regenerate title', err)
            })
          }
        } else if (event.type === SentraEventType.ERROR) {
          dispatch(setWaitingForAnswer(false))
          dispatch(setStreaming(false))
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

