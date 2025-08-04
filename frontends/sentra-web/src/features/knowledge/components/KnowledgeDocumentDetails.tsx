import { useState } from 'react';
import type { KnowledgeDocument } from '../types/knowledgeModels';
import { useKnowledge } from '../useKnowledge';

interface Props {
  document: KnowledgeDocument;
}

export default function KnowledgeDocumentDetails({ document }: Props) {
  const { updateDocumentMetadata, reindexDocument } = useKnowledge();
  const [displayName, setDisplayName] = useState(document.display_name);
  const [description, setDescription] = useState(document.description ?? '');

  const handleSave = () => {
    updateDocumentMetadata(document.id, { display_name: displayName, description });
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">📄 Document Details</h2>

      <div className="text-sm text-muted">Filename: {document.filename}</div>

      <div>
        <label className="text-sm font-medium">Display Name</label>
        <input
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          className="w-full px-2 py-1 rounded bg-[var(--sentra-primary-dark)]"
        />
      </div>

      <div>
        <label className="text-sm font-medium">Description</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-2 py-1 rounded bg-[var(--sentra-primary-dark)]"
        />
      </div>

      <div className="text-sm">
        Status: <span className="font-medium">{document.status}</span>
        {document.status_message && <div className="text-xs text-muted">{document.status_message}</div>}
        {document.error && <div className="text-xs text-red-400">❌ {document.error}</div>}
      </div>

      {document.status !== 'indexed' && (
        <button onClick={() => reindexDocument(document.id)} className="btn btn-outline">
          🔄 Reindex
        </button>
      )}

      <div className="text-xs text-muted">
        Created by {document.created_by.full_name} at {new Date(document.created_at).toLocaleString()}
      </div>

      <button onClick={handleSave} className="btn btn-primary mt-2">
        ave Changes
      </button>
    </div>
  );
}
