// src/features/chat/hooks/useChatActions.ts
import { useAppDispatch, useAppSelector } from '@store/hooks'
import { v4 as uuidv4 } from 'uuid'
import {
  createConversation,
  selectConversation,
  fetchConversationById,
  updateConversationTitle,
} from '@features/conversations/conversationSlice'
import {
  addMessage,
  updateLastAssistantMessage,
  setStreaming,
  setWaitingForAnswer,
} from '@features/chat/chatSlice'
import { chatService } from '@features/chat/chatService'
import { conversationService } from '@features/conversations/conversationService'
import type { ConversationEvent } from '@features/chat/types/events'
import type { ChatMessage } from '@features/conversations/types/conversationModels'

export function useChatActions() {
  const dispatch = useAppDispatch()
  const currentConversationId = useAppSelector(s => s.conversation.currentConversationId)
  const userId = useAppSelector(s => s.auth.user?.id)
  const { selectedContext } = useAppSelector(s => s.chat)

  const sendMessage = async (content: string) => {
    const trimmed = content.trim()
    if (!trimmed) return

    let conversationId = currentConversationId
    const userMessageId = uuidv4()
    const assistantMessageId = uuidv4()

    const wasNewConversation = !conversationId

    if (!conversationId) {
      const newConv = await dispatch(createConversation({ initial_prompt: trimmed })).unwrap()
      conversationId = newConv.id
      dispatch(selectConversation(conversationId))
      await dispatch(fetchConversationById(conversationId))
    }

    dispatch(setStreaming(true))
    dispatch(setWaitingForAnswer(true))

    dispatch(addMessage({
      id: userMessageId,
      role: 'user',
      content: trimmed,
      timestamp: Date.now(),
    }))

    let assistantStarted = false
    let titleTriggered = false

    const toSystemMessage = (e: ConversationEvent): ChatMessage => {
      // Minimal, safe mapping that doesn’t require extending ChatMessage type yet
      const label = 'label' in e && e.label ? e.label : undefined
      const status = 'status' in e && e.status ? ` [${e.status}]` : ''
      const body = e.content || ''
      const header = label ? `${label}${status}` : undefined
      const finalText = header ? `${header}\n${body}` : body || (e.type === 'step_start' ? 'Started.' : e.type === 'step_end' ? 'Completed.' : e.type === 'step_error' ? 'Error.' : '')
      return {
        id: e.event_id,
        role: 'system',
        content: finalText,
        timestamp: Date.now(),
      }
    }

    chatService.sendMessageStream(
      {
        user_id: userId,
        conversation_id: conversationId!,
        message_id: userMessageId,
        response_message_id: assistantMessageId,
        content: trimmed,
        context_source_ids: selectedContext.useRag ? selectedContext.sourceIds : [],
        context_document_ids: selectedContext.useRag ? selectedContext.documentIds : [],
      },
      // onEvent
      (event: ConversationEvent) => {
        switch (event.type) {
          case 'message_delta': {
            const delta = event.content ?? ''
            if (!delta) break
            if (!assistantStarted) {
              dispatch(addMessage({
                id: assistantMessageId,
                role: 'assistant',
                content: delta,
                timestamp: Date.now(),
              }))
              assistantStarted = true
            } else {
              dispatch(updateLastAssistantMessage(delta))
            }
            break
          }
          case 'message_final': {
            // Finalize stream
            dispatch(setWaitingForAnswer(false))
            dispatch(setStreaming(false))

            if (wasNewConversation && !titleTriggered) {
              titleTriggered = true
              ;(async () => {
                try {
                  const resp = await conversationService.generateLlmTitle(conversationId!)
                  if (resp.title) {
                    dispatch(updateConversationTitle({
                      id: resp.conversation_id,
                      title: resp.title,
                    }))
                  }
                } catch (err) {
                  console.warn('Failed to generate/fetch title', err)
                }
              })()
            }
            break
          }
          case 'step_start':
          case 'step_progress':
          case 'step_end':
          case 'step_error': {
            // Inline system message so we can SEE the steps immediately
            const sysMsg = toSystemMessage(event)
            if (sysMsg.content && sysMsg.content.trim().length > 0) {
              dispatch(addMessage(sysMsg))
            }
            break
          }
          default:
            // ignore unknown event types gracefully
            break
        }
      },
      // onError
      (err) => {
        console.error('Streaming error:', err)
        dispatch(setWaitingForAnswer(false))
        dispatch(setStreaming(false))
      }
    )
  }

  return { sendMessage }
}
