// features/knowledge/KnowledgePage.tsx
import { useParams, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useKnowledge } from './useKnowledge';
import KnowledgeStatsBar from './components/KnowledgeStatsBar';
import KnowledgeSourceList from './components/KnowledgeSourceList';
import KnowledgeDetailsPanel from './components/KnowledgeDetailsPanel';
import type { KnowledgeSourceVisibility } from './types/knowledgeModels';

export default function KnowledgePage() {
  const navigate = useNavigate();
  const { visibility: visibilityParam } = useParams<{ visibility: string }>();

  const {
    visibility,
    sources,
    changeVisibility,
    loadSources,
    loadDocuments,
    selectedSourceId,
  } = useKnowledge();

  // Ensure the URL param maps to a valid visibility
  useEffect(() => {
    const allowed: KnowledgeSourceVisibility[] = ['private', 'shared', 'org-wide'];
    if (!visibilityParam || !allowed.includes(visibilityParam as KnowledgeSourceVisibility)) {
      navigate('/k/private', { replace: true });
    }
  }, [visibilityParam, navigate, changeVisibility]);

  useEffect(() => {
  if (sources.length === 0) {
    loadSources();
  }
}, [sources.length, loadSources]);

  useEffect(() => {
    if (selectedSourceId) loadDocuments(selectedSourceId);
  }, [selectedSourceId, loadDocuments]);

  return (
    <div className="p-4 h-full flex flex-col gap-4">
      <h1 className="text-xl font-semibold">📚 Knowledge Management</h1>

      <KnowledgeStatsBar visibility={visibility} />

      <div className="flex flex-1 overflow-hidden">
        <div className="w-1/3 overflow-y-auto pr-4">
          <KnowledgeSourceList visibility={visibility} />
        </div>
        <div className="flex-1 overflow-y-auto pl-4 border-l border-[var(--sentra-primary-light)]">
          <KnowledgeDetailsPanel />
        </div>
      </div>
    </div>
  );
}
