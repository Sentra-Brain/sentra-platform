import { useAppDispatch, useAppSelector } from '../store/hooks'
import {
  fetchConversations,
  fetchConversationById,
  selectConversation,
  clearConversation,
  createConversation,
} from '../features/conversations/conversationSlice'

export function useConversations() {
  const dispatch = useAppDispatch()
  const {
    conversations,
    currentConversationId,
    selectedConversationDetails,
    loadingList,
    loadingConversation,
    error,
  } = useAppSelector((state) => state.conversation)

  return {
    conversations,
    currentConversationId,
    selectedConversationDetails,
    loadingList,
    loadingConversation,
    error,
    loadConversations: () => dispatch(fetchConversations()),
    loadConversationDetails: (id: string) => dispatch(fetchConversationById(id)),
    select: (id: string) => dispatch(selectConversation(id)),
    clear: () => dispatch(clearConversation()),
    create: (content: string, title?: string, description?: string, initial_prompt?: string) =>
      dispatch(createConversation({ content, title, description, initial_prompt })),
  }
}
