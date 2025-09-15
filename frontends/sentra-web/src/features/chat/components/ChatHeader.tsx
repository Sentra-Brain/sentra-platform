import { MoreVertical, LayoutPanelLeft } from 'lucide-react'
import AgentSelector from '../../agents/components/AgentSelector'

export default function ChatHeader() {
  return (
    <div className="px-4 py-1">
      <div className="flex justify-between items-center gap-4 text-[var(--sentra-text-muted)]">
        <AgentSelector />
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
