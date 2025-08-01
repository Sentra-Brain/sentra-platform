import { useAppDispatch, useAppSelector } from '../store/hooks'
import {
  fetchConversations,
  selectConversation,
  clearConversation,
  createConversation,
} from '../features/conversations/conversationSlice'

export function useConversations() {
  const dispatch = useAppDispatch()
  const { conversations, currentConversationId, loading, error } = useAppSelector(
    (state) => state.conversation // ✅ match your reducer key
  )

  const loadConversations = () => {
    dispatch(fetchConversations())
  }

  const select = (id: string) => {
    dispatch(selectConversation(id))
  }

  const clear = () => {
    dispatch(clearConversation())
  }

  const create = (content: string, title?: string, description?: string, initial_prompt?: string) => {
    return dispatch(createConversation({ content, title, description, initial_prompt }))
  }

  return {
    conversations,
    currentConversationId,
    loading,
    error,
    loadConversations,
    select,
    clear,
    create,
  }
}
