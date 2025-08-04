import { useKnowledge } from '../useKnowledge';
import DocumentStatusBadge from './DocumentStatusBadge';
import type { KnowledgeSourceVisibility } from '../types/knowledgeModels';

interface Props {
  visibility: KnowledgeSourceVisibility;
}

export default function KnowledgeSourceList({ visibility }: Props) {
  const {
    sources,
    documents,
    selectedSourceId,
    selectedDocumentId,
    selectSourceById,
    selectDocumentById,
  } = useKnowledge();

  const visibleSources = sources.filter((s) => s.visibility === visibility);

  return (
    <div className="space-y-1">
      {visibleSources.map((source) => {
        const docsForSource = documents.filter(
          (doc) => doc.knowledge_source_id === source.id
        );

        return (
          <div key={source.id}>
            {/* Source line */}
            <div
              onClick={() => selectSourceById(source.id)}
              className={`flex items-center justify-between cursor-pointer px-2 py-1 rounded-r-md hover:bg-[var(--sentra-primary-light)] ${
                source.id === selectedSourceId
                  ? 'border-l-4 border-[var(--sentra-accent)] bg-[var(--sentra-primary)]'
                  : ''
              }`}
            >
              <div className="flex items-center gap-2 text-sm font-semibold">
                📁 {source.display_name}
                <span className="text-muted text-xs">{docsForSource.length} docs</span>
              </div>
            </div>

            {/* Always show docs */}
            <div className="ml-4 mt-1 space-y-1">
              {docsForSource.length === 0 ? (
                <div className="text-xs text-muted italic pl-1">No documents</div>
              ) : (
                docsForSource.map((doc) => (
                  <div
                    key={doc.id}
                    onClick={() => selectDocumentById(doc.id)}
                    className={`flex items-center justify-between text-sm px-2 py-1 rounded cursor-pointer hover:bg-[var(--sentra-primary-light)] ${
                      doc.id === selectedDocumentId
                        ? 'border-l-4 border-[var(--sentra-accent)] bg-[var(--sentra-primary)]'
                        : ''
                    }`}
                  >
                    <div className="truncate">📄 {doc.display_name || '(Untitled)'}</div>
                    <DocumentStatusBadge status={doc.status} />
                  </div>
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
