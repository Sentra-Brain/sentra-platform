import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import type { ChatMessage } from '@features/conversations/types/conversationModels'

export default function MessageList({ messages }: { messages: ChatMessage[] }) {
  const endRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages.length]) // solo cuando cambia la cantidad

  return (
    <div className="flex flex-col gap-4 overflow-y-auto">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} {...msg} />
      ))}
      <div ref={endRef} />
    </div>
  )
}
