export default function ToolPanel({ label, content }: { label?: string; content?: string }) {
  return (
    <div className="border rounded-lg p-3 bg-purple-100 text-purple-900">
      {label && <div className="font-semibold mb-1">{label}</div>}
      {content && <pre className="text-xs whitespace-pre-wrap">{content}</pre>}
    </div>
  )
}

