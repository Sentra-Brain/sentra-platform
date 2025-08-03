// features/chat/components/MessageBubble.tsx
import type { MessageRole } from '@features/conversations/types/conversationModels'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

type Props = {
  id: string
  role: MessageRole
  content: string
}

export default function MessageBubble({ role, content }: Props) {
  const isUser = role === 'user'

  return (
    <div
      className={`rounded-xl px-4 py-3 max-w-[768px] w-full ${
        isUser
          ? 'bg-[var(--sentra-primary-light)] self-end text-right'
          : 'bg-[var(--sentra-background-muted)] self-start'
      }`}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  )
}
