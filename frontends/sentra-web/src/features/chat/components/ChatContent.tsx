// features/chat/components/ChatContent.tsx
import { useAppSelector } from '@store/hooks'
import EventList from './EventList'
import { selectAllEvents } from '@features/chat/eventsSlice'

export default function ChatContent() {
  const events = useAppSelector(selectAllEvents)

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="w-full max-w-[768px] mx-auto">
          <EventList events={events} />
      </div>
    </div>
  )
}
