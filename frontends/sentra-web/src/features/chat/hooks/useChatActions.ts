// src/features/chat/hooks/useChatActions.ts
import { useAppDispatch, useAppSelector } from '@store/hooks'
import { v4 as uuidv4 } from 'uuid'
import {
  createConversation,
  selectConversation,
  fetchConversationById,
} from '@features/conversations/conversationSlice'
import {
  addMessage,
  updateLastAssistantMessage,
  setStreaming,
  setWaitingForAnswer,
} from '@features/chat/chatSlice'
import { chatService } from '@features/chat/chatService'
import { conversationService } from '@features/conversations/conversationService'

export function useChatActions() {
  const dispatch = useAppDispatch()
  const currentConversationId = useAppSelector(s => s.conversation.currentConversationId)

  const sendMessage = async (content: string) => {
    const trimmed = content.trim()
    if (!trimmed) return

    dispatch(setStreaming(true))
    dispatch(setWaitingForAnswer(true))

    const userMessageId = uuidv4()
    const assistantMessageId = uuidv4()

    // ➕ Add user message immediately
    dispatch(addMessage({
      id: userMessageId,
      role: 'user',
      content: trimmed,
      timestamp: Date.now(),
    }))

    let conversationId = currentConversationId

    // 🆕 If no active conversation, create one first
    if (!conversationId) {
      const newConv = await dispatch(createConversation({ initial_prompt: trimmed })).unwrap()
      conversationId = newConv.id
      dispatch(selectConversation(conversationId))
      dispatch(fetchConversationById(conversationId)) // preload full conversation view
    }

    // 📡 Start streaming the assistant response
    let assistantStarted = false

    chatService.sendMessageStream(
      {
        conversation_id: conversationId,
        content: trimmed,
        message_id: userMessageId,
        response_message_id: assistantMessageId,
      },
      (chunk) => {
        if (chunk.role === 'assistant') {
          if (!assistantStarted) {
            dispatch(addMessage({
              id: assistantMessageId,
              role: 'assistant',
              content: chunk.content,
              timestamp: Date.now(),
            }))
            assistantStarted = true
          } else {
            dispatch(updateLastAssistantMessage(chunk.content))
          }

          if (chunk.final) {
            dispatch(setWaitingForAnswer(false))
          }
        }
      },
      (err) => {
        console.error('Streaming error:', err)
        dispatch(setWaitingForAnswer(false))
      }
    )

    // 🧹 Cleanup flags (in case stream doesn’t do it)
    dispatch(setStreaming(false))

    // 🧠 Trigger title generation in background
    if (!currentConversationId) {
      conversationService.generateLlmTitle(conversationId).catch(err => {
        console.warn('Failed to trigger title generation', err)
      })
    }
  }

  return { sendMessage }
}
