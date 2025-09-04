export default function ErrorBubble({ label, content }: { label?: string; content?: string }) {
  return (
    <div className="bg-red-200 text-red-900 rounded-xl px-4 py-3 max-w-[768px] self-start">
      {label && <div className="font-semibold mb-1">{label}</div>}
      {content && <div className="whitespace-pre-wrap text-sm">{content}</div>}
    </div>
  )
}

