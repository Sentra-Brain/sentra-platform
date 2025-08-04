import { useKnowledge } from '../useKnowledge';
import KnowledgeDocumentDetails from './KnowledgeDocumentDetails';
import KnowledgeSourceDetails from './KnowledgeSourceDetails';

export default function KnowledgeDetailsPanel() {
  const { selectedSourceId, selectedDocumentId, sources, documents } = useKnowledge();

  const source = sources.find((s) => s.id === selectedSourceId);
  const doc = documents.find((d) => d.id === selectedDocumentId);

  if (doc) return <KnowledgeDocumentDetails document={doc} />;
  if (source) return <KnowledgeSourceDetails source={source} />;

  return <div className="text-sm text-muted">Select a source or document to view details</div>;
}
