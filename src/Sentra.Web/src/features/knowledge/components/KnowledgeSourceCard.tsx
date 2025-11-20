import type { KnowledgeSource } from '../types/knowledgeModels';
import { Folder} from 'lucide-react';
import { useKnowledge } from '../useKnowledge';

interface Props {
  source: KnowledgeSource;
  selected?: boolean;
  onClick?: () => void;
}

export default function KnowledgeSourceCard({ source, selected, onClick }: Props) {
  const { documentsBySource } = useKnowledge();

  const docCount = documentsBySource[source.id]?.length || 0;

  const statusBadge = {
    active: <span className="text-green-400 text-xs font-medium">🟢 Active</span>,
    disabled: <span className="text-yellow-400 text-xs font-medium">🟡 Disabled</span>,
    error: <span className="text-red-400 text-xs font-medium">🔴 Error</span>,
  };

  return (
    <div
      onClick={onClick}
      className={`cursor-pointer border rounded-md px-3 py-2 transition-colors ${
        selected
          ? 'bg-sentra-accent text-white border-sentra-accent'
          : 'hover:bg-sentra-accent-light border-[var(--sentra-primary-light)]'
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Folder className="w-4 h-4" />
          <div className="text-sm font-medium truncate">{source.name}</div>
        </div>
        <div className="text-xs text-muted">{docCount} docs</div>
      </div>

      <div className="text-xs mt-1">{statusBadge[source.status]}</div>
    </div>
  );
}
