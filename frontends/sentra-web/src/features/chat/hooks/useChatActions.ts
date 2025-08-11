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

    chatService.sendMessageStream(
      {
        user_id: userId,
        conversation_id: conversationId,
        message_id: userMessageId,
        response_message_id: assistantMessageId,
        content: trimmed,
        context_source_ids: selectedContext.useRag ? selectedContext.sourceIds : [],
        context_document_ids: selectedContext.useRag ? selectedContext.documentIds : [],
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
        }

        if (chunk.final) {
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
