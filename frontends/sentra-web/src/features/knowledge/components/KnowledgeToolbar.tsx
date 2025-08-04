// features/knowledge/components/KnowledgeToolbar.tsx
import { useState } from 'react';
import { Plus, UploadCloud, RefreshCcw } from 'lucide-react';
import { useKnowledge } from '../useKnowledge';
import type { KnowledgeSourceVisibility } from '../types/knowledgeModels';
import CreateKnowledgeSourceModal from '../modals/CreateKnowledgeSourceModal';
import UploadDocumentModal from '../modals/UploadDocumentModal';

interface Props {
  visibility: KnowledgeSourceVisibility;
}

export default function KnowledgeToolbar({ visibility }: Props) {
  const { sources, documents, loadSources, loadDocuments, selectedSourceId } = useKnowledge();

  const [createOpen, setCreateOpen] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);

  const handleRefresh = () => {
    loadSources(true);
    if (selectedSourceId) loadDocuments(selectedSourceId, true);
  };

  const labelMap: Record<KnowledgeSourceVisibility, string> = {
    private: 'My Sources',
    shared: 'Shared with Me',
    'org-wide': 'Organization',
  };

  const visibleSources = sources.filter((s) => s.visibility === visibility);

  return (
    <>
      <p className="text-sm text-[var(--sentra-neutral)]">{labelMap[visibility]}</p>

      <div className="bg-[var(--sentra-primary-dark)] border border-[var(--sentra-accent-light)] px-4 py-3 rounded-md flex items-center justify-between">
        <div className="flex items-center gap-4 text-sm">
          <span>📁 <b>{visibleSources.length}</b> sources</span>
          <span>📄 <b>{documents.length}</b> documents</span>
        </div>

        <div className="flex items-center gap-2">
          <button onClick={() => setCreateOpen(true)} className="btn btn-sm btn-outline">
            <Plus className="w-4 h-4 mr-1" /> New Source
          </button>
          <button onClick={() => setUploadOpen(true)} className="btn btn-sm btn-outline">
            <UploadCloud className="w-4 h-4 mr-1" /> Upload
          </button>
          <button onClick={handleRefresh} className="btn btn-sm btn-ghost">
            <RefreshCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      <CreateKnowledgeSourceModal isOpen={createOpen} onClose={() => setCreateOpen(false)} />
      <UploadDocumentModal isOpen={uploadOpen} onClose={() => setUploadOpen(false)} />
    </>
  );
}
