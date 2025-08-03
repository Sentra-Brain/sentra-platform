// features/chat/components/ChatContent.tsx
import { useAppSelector } from '@store/hooks'
import MessageList from './MessageList'
import type { ConversationDetails } from '@features/conversations/types/conversationModels'

type ChatMessage = ConversationDetails['messages'][number]

export default function ChatContent() {
  const messages: ChatMessage[] =
    useAppSelector((state) => state.conversation.selectedConversationDetails?.messages) ?? []

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <MessageList messages={messages} />
    </div>
  )
}
