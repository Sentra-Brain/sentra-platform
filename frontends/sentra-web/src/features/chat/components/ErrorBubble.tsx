import type { SentraEventContent } from '../eventsSlice'

function renderContent(content?: SentraEventContent) {
  if (!content || !content.parts) return null
  const text = content.parts.map(p => p.text).filter(Boolean).join('')
  return text ? <div className="whitespace-pre-wrap text-sm">{text}</div> : null
}

export default function ErrorBubble({ label, content }: { label?: string; content?: SentraEventContent }) {
  return (
    <div className="bg-red-200 text-red-900 rounded-xl px-4 py-3 max-w-[768px] self-start">
      {label && <div className="font-semibold mb-1">{label}</div>}
      {renderContent(content)}
    </div>
  )
}

