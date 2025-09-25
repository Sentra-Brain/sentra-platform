import { useEffect, useRef } from 'react'
import { useAppSelector } from '@store/hooks'
import MessageBubble from './MessageBubble'
import WaitingForAnswer from './WaitingForAnswer'
import StepPanel from './StepPanel'
import ErrorBubble from './ErrorBubble'
import ToolPanel from './ToolPanel'
import { SentraEventType, type SentraEvent } from '@features/chat/types/events'
import type { MessageRole } from '@features/conversations/types/conversationModels'

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
        if (
          evt.type === SentraEventType.MESSAGE_DELTA ||
          evt.type === SentraEventType.MESSAGE_FINAL
        ) {
          const role = evt.author as MessageRole
          if (
            evt.content?.parts.some(
              (p) => p.function_call || p.function_response
            )
          ) {
            return (
              <ToolPanel
                key={evt.id}
                label={evt.meta?.label as string | undefined}
                content={evt.content}
              />
            )
          }
          return (
            <MessageBubble
              key={evt.id}
              id={evt.id}
              role={role}
              content={evt.content}
            />
          )
        }
        if (
          evt.type === SentraEventType.STEP_START ||
          evt.type === SentraEventType.STEP_END ||
          evt.type === SentraEventType.CONTEXT_BUILT ||
          evt.type === SentraEventType.LLM_CALLED
        ) {
          return <StepPanel key={evt.id} event={evt} />
        }
        if (evt.type === SentraEventType.ERROR) {
          return (
            <ErrorBubble
              key={evt.id}
              label={evt.meta?.label as string | undefined}
              content={evt.content}
            />
          )
        }
        return null
      })}
      {waitingForAnswer && <WaitingForAnswer />}
      <div ref={endRef} />
    </div>
  )
}

