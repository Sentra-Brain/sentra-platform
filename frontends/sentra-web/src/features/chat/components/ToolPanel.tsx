import type { SentraEventContent } from '@features/chat/types/events'

function renderContent(content?: SentraEventContent) {
  if (!content || !content.parts) return null
  // For now, just show text parts, but could render function_call/response
  const text = content.parts.map(p => p.text).filter(Boolean).join('')
  return text ? <pre className="text-xs whitespace-pre-wrap">{text}</pre> : null
}

export default function ToolPanel({ label, content }: { label?: string; content?: SentraEventContent }) {
  return (
    <div className="border rounded-lg p-3 bg-purple-100 text-purple-900">
      {label && <div className="font-semibold mb-1">{label}</div>}
      {renderContent(content)}
    </div>
  )
}

