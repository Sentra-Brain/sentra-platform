import type { KnowledgeSource } from '../types/knowledgeModels';

interface Props {
  source: KnowledgeSource;
}

export default function KnowledgeSourceDetails({ source }: Props) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">📁 Source Details</h2>

      <div className="text-sm">Name: {source.name}</div>
      <div className="text-sm">Type: {source.type}</div>
      <div className="text-sm">Status: {source.status}</div>
      <div className="text-sm">Visibility: {source.visibility}</div>
      <div className="text-sm">Auto-index: {source.auto_index ? 'Yes' : 'No'}</div>

      {source.description && (
        <div className="text-sm text-muted">📝 {source.description}</div>
      )}

      <div className="text-xs text-muted">
        Created by {source.created_by.full_name} on {new Date(source.created_at).toLocaleString()}
      </div>
    </div>
  );
}
