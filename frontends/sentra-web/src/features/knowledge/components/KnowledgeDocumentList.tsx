// features/knowledge/components/KnowledgeDocumentList.tsx
import { useKnowledge } from '../useKnowledge';
import KnowledgeDocumentCard from './KnowledgeDocumentCard';

export default function KnowledgeDocumentList() {
  const {
    documents,
    selectedDocumentId,
    selectDocumentById,
  } = useKnowledge();

  const handleSelect = (id: string) => {
    if (id === selectedDocumentId) {
      selectDocumentById(null);
    } else {
      selectDocumentById(id);
    }
  };

  return (
    <div className="space-y-2">
      {documents.length === 0 && (
        <div className="text-sm text-gray-400">No documents available.</div>
      )}
      {documents.map((doc) => (
        <KnowledgeDocumentCard
          key={doc.id}
          document={doc}
          selected={doc.id === selectedDocumentId}
          onClick={() => handleSelect(doc.id)}
        />
      ))}
    </div>
  );
}
