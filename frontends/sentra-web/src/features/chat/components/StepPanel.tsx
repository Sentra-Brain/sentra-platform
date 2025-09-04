import type { EngineEvent } from '@features/chat/types/events'

export default function StepPanel({ event }: { event: EngineEvent }) {
  const label = (event as any).label || 'Step'
  const status = (event as any).status || ''
  const content = event.content || ''
  const progress = (event as any).meta?.progress as number | undefined

  return (
    <div className="border rounded-lg p-3 bg-gray-100 text-gray-800">
      <div className="font-semibold mb-1">
        {label} {status && <span className="text-sm">[{status}]</span>}
      </div>
      {content && <div className="mb-1 text-sm whitespace-pre-wrap">{content}</div>}
      {typeof progress === 'number' && (
        <div className="w-full bg-gray-300 rounded-full h-2">
          <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${progress}%` }} />
        </div>
      )}
    </div>
  )
}

