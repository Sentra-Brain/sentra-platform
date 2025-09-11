// features/chat/components/MessageBubble.tsx
import type { SentraEventContent } from '@features/chat/types/events'
import type { MessageRole } from '@features/sessions/types/sessionModels'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

type Props = {
  id: string
  role: MessageRole
  content?: SentraEventContent
}

function renderContent(content?: SentraEventContent) {
  if (!content || !content.parts) return null
  // For now, concatenate all text parts, ignore function_call/response
  const text = content.parts.map(p => p.text).filter(Boolean).join('')
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]}>
      {text}
    </ReactMarkdown>
  )
}

export default function MessageBubble({ role, content }: Props) {
  const isUser = role === 'user'

  return (
    <div
      className={`rounded-xl px-4 py-3 max-w-[768px] prose dark:prose-invert max-w-none ${
        isUser
          ? 'bg-[var(--sentra-primary-dark)] self-end text-right'
          : 'bg-[var(--sentra-primary-light)] self-start'
      }`}
      style={{ color: 'var(--color-text-base)' }}
    >
      {renderContent(content)}
    </div>
  )
}
