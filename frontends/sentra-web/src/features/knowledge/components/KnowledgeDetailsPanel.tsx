// features/knowledge/components/KnowledgeDetailsPanel.tsx
import { useKnowledge } from '../useKnowledge';
import type { Document } from '../types/knowledgeModels';

export default function KnowledgeDetailsPanel() {
  const {
    selectedSourceId,
    selectedDocumentId,
    sources,
    documents,
  } = useKnowledge();

  const source = sources.find((s) => s.id === selectedSourceId);
  const doc: Document | undefined = documents.find((d) => d.id === selectedDocumentId);

  if (doc) {
    return (
      <div>
        <h2 className="text-lg font-semibold mb-2">📄 Document Details</h2>
        <div className="text-sm">File: {doc.filename}</div>
        <div className="text-sm">Status: {doc.status}</div>
        {/* etc. */}
      </div>
    );
  }

  if (source) {
    return (
      <div>
        <h2 className="text-lg font-semibold mb-2">📁 Source Details</h2>
        <div className="text-sm">Name: {source.name}</div>
        <div className="text-sm">Status: {source.status}</div>
        {/* etc. */}
      </div>
    );
  }

  return <div className="text-sm text-gray-400">Select a source or document...</div>;
}
