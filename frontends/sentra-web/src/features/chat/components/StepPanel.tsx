import type { SentraEvent, SentraEventContent } from '../eventsSlice'

function renderContent(content?: SentraEventContent) {
  if (!content || !content.parts) return null
  const text = content.parts.map(p => p.text).filter(Boolean).join('')
  return text ? <div className="mb-1 text-sm whitespace-pre-wrap">{text}</div> : null
}

export default function StepPanel({ event }: { event: SentraEvent }) {
  const label = 'label' in event && event.label ? event.label : 'Step';
  const status = 'status' in event && event.status ? event.status : '';
  let progress: number | undefined = undefined;
  if ('meta' in event && event.meta && Object.prototype.hasOwnProperty.call(event.meta, 'progress')) {
    const meta = event.meta as { progress?: number };
    if (typeof meta.progress === 'number') {
      progress = meta.progress;
    }
  }

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

