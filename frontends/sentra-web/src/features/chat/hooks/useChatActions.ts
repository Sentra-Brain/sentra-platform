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
import { 
  stepStarted, 
  stepUpdated, 
  clearSteps 
} from '@features/chat/stepsSlice'
import { chatService } from '@features/chat/chatService'
import { conversationService } from '@features/conversations/conversationService'

export function useChatActions() {
  const dispatch = useAppDispatch()
  const currentConversationId = useAppSelector(s => s.conversation.currentConversationId)
  const userId = useAppSelector(s => s.auth.user?.id)
  const { selectedContext } = useAppSelector(s => s.chat)

  // Use selected context or empty arrays if RAG is disabled
  const context_source_ids = selectedContext.useRag ? selectedContext.sourceIds : []
  const context_document_ids = selectedContext.useRag ? selectedContext.documentIds : []

  const sendMessage = async (content: string) => {
    const trimmed = content.trim()
    if (!trimmed) return

    // Clear any previous steps when starting a new message
    dispatch(clearSteps())
    
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
        user_id: userId,
        conversation_id: conversationId,
        message_id: userMessageId,
        response_message_id: assistantMessageId,
        content: trimmed,
        context_source_ids: context_source_ids,
        context_document_ids: context_document_ids,
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
      (stepEvent) => {
        // Handle step events
        if (stepEvent.type === "step_start" && stepEvent.step_id && stepEvent.label) {
          dispatch(stepStarted({
            stepId: stepEvent.step_id,
            label: stepEvent.label
          }))
        } else if (stepEvent.type === "step_end" || stepEvent.type === "step_error") {
          if (stepEvent.step_id) {
            dispatch(stepUpdated({
              stepId: stepEvent.step_id,
              status: stepEvent.type === "step_error" ? "error" : "done",
              meta: stepEvent.meta
            }))
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
      conversationService.generateLlmTitle(conversationId)
        .then(() => {
          // Fetch the updated conversation to get the new title
          conversationService.get(conversationId)
            .then((updatedConv) => {
              // Update the conversation title in the Redux store
              dispatch(updateConversationTitle({ 
                id: conversationId, 
                title: updatedConv.title 
              }))
            })
            .catch(err => {
              console.warn('Failed to fetch updated conversation', err)
            })
        })
        .catch(err => {
          console.warn('Failed to trigger title generation', err)
        })
    }
  }

  return { sendMessage }
}
