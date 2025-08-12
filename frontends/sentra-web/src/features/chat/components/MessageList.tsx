import { useEffect, useRef } from 'react'
import { useAppSelector } from '@store/hooks'
import MessageBubble from './MessageBubble'
import WaitingForAnswer from './WaitingForAnswer'
import type { ChatMessage } from '@features/conversations/types/conversationModels'

export default function MessageList({ messages }: { messages: ChatMessage[] }) {
  const endRef = useRef<HTMLDivElement | null>(null)
  const waitingForAnswer = useAppSelector((state) => state.chat.waitingForAnswer)

  useEffect(() => {
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages.length, waitingForAnswer]) // scroll when messages change or waiting state changes

  return (
    <div className="flex flex-col gap-4 overflow-y-auto">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} {...msg} />
      ))}
      {waitingForAnswer && <WaitingForAnswer />}
      <div ref={endRef} />
    </div>
  )
}