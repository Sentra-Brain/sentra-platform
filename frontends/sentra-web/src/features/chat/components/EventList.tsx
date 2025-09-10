import { useEffect, useRef } from 'react'
import { useAppSelector } from '@store/hooks'
import MessageBubble from './MessageBubble'
import WaitingForAnswer from './WaitingForAnswer'
import StepPanel from './StepPanel'
import ErrorBubble from './ErrorBubble'
import ToolPanel from './ToolPanel'



import type { SentraEvent, SentraEventContent } from '../eventsSlice'

function toSentraEventContent(content: unknown): SentraEventContent | undefined {
  if (!content) return undefined
  if (
    typeof content === 'object' &&
    content !== null &&
    'parts' in content &&
    Array.isArray((content as { parts?: unknown }).parts)
  ) {
    return content as SentraEventContent
  }
  if (typeof content === 'string') return { parts: [{ text: content }] }
  return undefined
}

export default function EventList({ events }: { events: SentraEvent[] }) {
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
        const content = toSentraEventContent(evt.content)
        switch (evt.type) {
          case 'user_message':
            return <MessageBubble key={evt.id} id={evt.id} role="user" content={content} />
          case 'message_delta':
          case 'message_final':
            return <MessageBubble key={evt.id} id={evt.id} role="assistant" content={content} />
          case 'step_start':
          case 'step_progress':
          case 'step_end':
            return <StepPanel key={evt.id} event={{ ...evt, content }} />
          case 'step_error':
            return <ErrorBubble key={evt.id} label={evt.label} content={content} />
          case 'tool_call':
            return <ToolPanel key={evt.id} label={evt.label} content={content} />
          default:
            return null
        }
      })}
      {waitingForAnswer && <WaitingForAnswer />}
      <div ref={endRef} />
    </div>
  )
}

