import type { SentraEvent, SentraEventContent } from '@features/chat/types/events'

function renderContent(content?: SentraEventContent) {
  if (!content || !content.parts) return null
  const text = content.parts.map(p => p.text).filter(Boolean).join('')
  return text ? <div className="mb-1 text-sm whitespace-pre-wrap">{text}</div> : null
}

export default function StepPanel({ event }: { event: SentraEvent }) {
  const meta = event.meta as { label?: string; progress?: number } | undefined
  const label = meta?.label ?? 'Step'
  const status = event.status || ''
  const progress: number | undefined = meta?.progress

  return (
    <div className="border rounded-lg p-3 bg-gray-100 text-gray-800">
      <div className="font-semibold mb-1">
        {String(label)}
        {status ? <span className="text-sm"> [{String(status)}]</span> : null}
      </div>
      {renderContent(event.content)}
      {typeof progress === 'number' && (
        <div className="w-full bg-gray-300 rounded-full h-2">
          <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${progress}%` }} />
        </div>
      )}
    </div>
  )
}

