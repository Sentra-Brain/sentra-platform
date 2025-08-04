// features/knowledge/components/KnowledgeSourceCard.tsx
import type { KnowledgeSource } from '../types/knowledgeModels';
import { Folder } from 'lucide-react';

interface Props {
  source: KnowledgeSource;
  selected?: boolean;
  onClick?: () => void;
}

export default function KnowledgeSourceCard({ source, selected, onClick }: Props) {
  return (
    <div
      onClick={onClick}
      className={`cursor-pointer border rounded-md px-3 py-2 transition-colors ${
        selected
          ? 'bg-sentra-accent text-white border-sentra-accent'
          : 'hover:bg-sentra-accent-light border-[var(--sentra-primary-light)]'
      }`}
    >
      <div className="flex items-center gap-2">
        <Folder className="w-4 h-4" />
        <div className="text-sm font-medium truncate">{source.name}</div>
      </div>
    </div>
  );
}
