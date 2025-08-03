import { MoreVertical, LayoutPanelLeft } from 'lucide-react'

export default function ChatHeader() {
  return (
    <div className="px-4 py-1">
      <div className="flex justify-end items-center gap-2 text-[var(--sentra-text-muted)]">
        <button
          className="p-1 rounded hover:bg-[var(--sentra-primary-dark)]"
          title="Menu"
        >
          <MoreVertical size={16} />
        </button>

        <button
          className="p-1 rounded hover:bg-[var(--sentra-primary-dark)]"
          title="Toggle panel"
        >
          <LayoutPanelLeft size={16} />
        </button>
      </div>
    </div>
  )
}
