// src/features/chat/hooks/useChatActions.ts
import { useAppDispatch } from '@store/hooks'
import { v4 as uuidv4 } from 'uuid'

import {
  createConversation,
  selectConversation,
  fetchConversationById,
} from '@features/conversations/conversationSlice'

import { chatService } from '@features/chat/chatService'
import {
  setStreaming,
  setWaitingForAnswer,
} from '@features/chat/chatSlice'

import { conversationService } from '@features/conversations/conversationService'

export function useChatActions() {
  const dispatch = useAppDispatch()

  const startNewConversation = async (initialPrompt: string) => {
    // 1. Crear conversación vacía (sin initial_prompt)
    const conversation = await dispatch(
      createConversation({ content: initialPrompt }) // `initial_prompt` es opcional, pero puede ir aquí
    ).unwrap()

    const conversationId = conversation.id
    const userMessageId = uuidv4()
    const assistantMessageId = uuidv4()

    // 2. Cambiar estado global para indicar que ya hay conversación activa
    dispatch(selectConversation(conversationId))

    // 3. Opcionalmente, cargar conversación completa (para mostrar mensajes vacíos, etc.)
    dispatch(fetchConversationById(conversationId))

    // 4. Iniciar stream con el primer mensaje del usuario
    dispatch(setStreaming(true))
    dispatch(setWaitingForAnswer(true))

    chatService.sendMessageStream(
      {
        conversation_id: conversationId,
        content: initialPrompt,
        message_id: userMessageId,
        response_message_id: assistantMessageId,
      },
      (chunk) => {
        // Aquí normalmente ya lo procesa chatSlice via SSE events o similar
        console.log('Streamed chunk:', chunk)
      },
      (err) => {
        console.error('Streaming failed', err)
        // Podrías despachar un error si tienes setChatError(...)
      }
    )

    // 5. En paralelo, generar título para la conversación
    conversationService
      .update(conversationId, { title: '...' }) // <-- puede ir vacío o con título temporal
      .then(() => {
        // Posteriormente el título se actualizará desde el backend al finalizar la generación
      })
      .catch((err) => {
        console.warn('Failed to request title generation', err)
      })

    // 6. Liberar flags (si no lo gestiona el streaming completo)
    dispatch(setStreaming(false))
    dispatch(setWaitingForAnswer(false))
  }

  return { startNewConversation }
}
