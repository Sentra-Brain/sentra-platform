import { useEffect, useRef } from 'react'
import { useAppSelector } from '@store/hooks'
import MessageBubble from './MessageBubble'
import WaitingForAnswer from './WaitingForAnswer'
import ErrorBubble from './ErrorBubble'
import type { RenderableEvent } from '@features/chat/eventsSlice'

export default function EventList({ events }: { events: RenderableEvent[] }) {
  const endRef = useRef<HTMLDivElement | null>(null)
  const waitingForAnswer = useAppSelector((state) => state.events.waitingForAnswer)

  useEffect(() => {
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [events.length, waitingForAnswer])

  return (
    <div className="flex flex-col gap-4 overflow-y-auto">
      {events.map((evt) => {
        if (evt.type === 'message_delta' || evt.type === 'final') {
          return (
            <MessageBubble
              key={evt.id}
              id={evt.id}
              role={evt.role}
              content={evt.content}
            />
          )
        }
        if (evt.type === 'error') {
          return <ErrorBubble key={evt.id} content={evt.content} />
        }
        return null
      })}
      {waitingForAnswer && <WaitingForAnswer />}
      <div ref={endRef} />
    </div>
  )
}

