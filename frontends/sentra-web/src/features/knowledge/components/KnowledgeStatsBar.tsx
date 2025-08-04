// features/knowledge/components/KnowledgeStatsBar.tsx
import type { KnowledgeSourceVisibility } from '../types/knowledgeModels';
import { useKnowledge } from '../useKnowledge';

interface Props {
  visibility: KnowledgeSourceVisibility;
}

export default function KnowledgeStatsBar({ visibility }: Props) {
  const { sources, documents } = useKnowledge();

  const visibleSources = sources.filter((s) => s.visibility === visibility);

  return (
    <div className="bg-[var(--sentra-primary-dark)] text-[var(--sentra-text)] px-4 py-3 rounded-md mb-4 border border-[var(--sentra-accent-light)] flex items-center justify-between">
      <div>
        <span className="text-sm font-medium">📁 Sources:</span>{' '}
        <span className="font-semibold">{visibleSources.length}</span>
      </div>
      <div>
        <span className="text-sm font-medium">📄 Documents:</span>{' '}
        <span className="font-semibold">{documents.length}</span>
      </div>
    </div>
  );
}
