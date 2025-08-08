// features/chat/components/ChatContent.tsx
import { useAppSelector } from '@store/hooks'
import MessageList from './MessageList'
import StepsTimeline from './StepsTimeline'
import type { ChatMessage } from '@features/conversations/types/conversationModels'

export default function ChatContent() {
  const messages: ChatMessage[] = useAppSelector((state) => state.chat.messages)

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="w-full max-w-[768px] mx-auto">
        <StepsTimeline />
        <MessageList messages={messages} />
      </div>
    </div>
  )
}
