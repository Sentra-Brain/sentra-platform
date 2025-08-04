import { useKnowledge } from '../useKnowledge';
import KnowledgeSourceCard from './KnowledgeSourceCard';
import type { KnowledgeSourceVisibility } from '../types/knowledgeModels';

interface Props {
  visibility: KnowledgeSourceVisibility;
}

export default function KnowledgeSourceList({ visibility }: Props) {
  const {
    sources,
    documents,
    selectedSourceId,
    selectSourceById,
    selectDocumentById,
    resetSelection,
  } = useKnowledge();  // ← Asegúrate que useKnowledge expone selectDocumentById

  const visibleSources = sources.filter((s) => s.visibility === visibility);

  const handleSelect = (id: string) => {
    if (id === selectedSourceId) {
      resetSelection();
    } else {
      selectSourceById(id);
    }
  };

  return (
    <div className="space-y-2">
      {visibleSources.map((source) => (
        <div key={source.id}>
          <KnowledgeSourceCard
            source={source}
            selected={source.id === selectedSourceId}
            onClick={() => handleSelect(source.id)}
          />

          {/* ⬇️ Render documents if this source is selected */}
          {source.id === selectedSourceId && (
            <div className="ml-6 mt-1 space-y-1">
              {documents.length === 0 ? (
                <div className="text-sm text-muted">No documents</div>
              ) : (
                documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="text-sm px-2 py-1 rounded hover:bg-[var(--sentra-primary-light)] cursor-pointer"
                    onClick={() => selectDocumentById(doc.id)}  // ✅ Aquí está el fix
                  >
                    📄 {doc.filename}
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
