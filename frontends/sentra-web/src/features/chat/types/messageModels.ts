// features/chat/types/messageModels.ts
import type { ConversationDetails } from '@features/conversations/types/conversationModels'

export type ChatMessage = ConversationDetails['messages'][number]
