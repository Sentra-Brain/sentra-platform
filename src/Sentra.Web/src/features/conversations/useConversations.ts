import { useAppDispatch, useAppSelector } from '@store/hooks'
import {
  fetchConversations,
  fetchConversationById,
  selectConversation,
  clearConversation,
  createConversation,
  regenerateTitle,
} from './conversationsSlice'

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
    create: (initial_prompt?: string) =>
      dispatch(createConversation({ initial_prompt: initial_prompt ?? '' })),
    regenerateTitle: (id: string) => dispatch(regenerateTitle(id)),
  }
}
