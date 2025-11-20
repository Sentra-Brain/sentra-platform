// features/chat/components/MessageBubble.tsx
import type { Role } from '@ag-ui/core'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

type Props = {
  id: string
  role: Role
  content: string
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
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  )
}
