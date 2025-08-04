// features/knowledge/components/KnowledgeSourceList.tsx
import { useKnowledge } from '../useKnowledge';
import KnowledgeSourceCard from './KnowledgeSourceCard';
import type { KnowledgeSourceVisibility } from '../types/knowledgeModels';

interface Props {
  visibility: KnowledgeSourceVisibility;
}

export default function KnowledgeSourceList({ visibility }: Props) {
  const {
    sources,
    selectedSourceId,
    selectSourceById,
    resetSelection,
  } = useKnowledge();

  const visibleSources = sources.filter((s) => s.visibility === visibility);

  const handleSelect = (id: string) => {
    if (id === selectedSourceId) {
      resetSelection(); // toggle
    } else {
      selectSourceById(id);
    }
  };

  return (
    <div className="space-y-2">
      {visibleSources.map((source) => (
        <KnowledgeSourceCard
          key={source.id}
          source={source}
          selected={source.id === selectedSourceId}
          onClick={() => handleSelect(source.id)}
        />
      ))}
    </div>
  );
}
