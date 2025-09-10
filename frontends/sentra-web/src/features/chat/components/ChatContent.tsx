// features/chat/components/ChatContent.tsx
import { useAppSelector } from '@store/hooks'
import EventList from './EventList'
import type { SentraEvent } from '@features/chat/types/events'

export default function ChatContent() {
  const events: SentraEvent[] = useAppSelector((state) => state.events.events)

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="w-full max-w-[768px] mx-auto">
          <EventList events={events} />
      </div>
    </div>
  )
}
