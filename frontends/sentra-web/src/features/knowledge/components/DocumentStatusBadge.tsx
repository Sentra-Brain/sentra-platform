import { DocumentStatus } from '../types/knowledgeModels';

interface Props {
  status: DocumentStatus;
}

const statusMap: Record<DocumentStatus, { label: string; className: string }> = {
  pending:     { label: 'Pending', className: 'bg-gray-500 text-white' },
  processing:  { label: 'Processing', className: 'bg-blue-500 text-white' },
  extracting:  { label: 'Extracting', className: 'bg-yellow-500 text-black' },
  chunking:    { label: 'Chunking', className: 'bg-yellow-600 text-white' },
  embedding:   { label: 'Embedding', className: 'bg-purple-500 text-white' },
  indexing:    { label: 'Indexing', className: 'bg-indigo-500 text-white' },
  indexed:     { label: 'Indexed', className: 'bg-green-500 text-white' },
  failed:      { label: 'Failed', className: 'bg-red-600 text-white' },
  to_be_removed: { label: 'To Be Removed', className: 'bg-orange-600 text-white' },
  removed:     { label: 'Removed', className: 'bg-gray-700 text-white' },
};

export default function DocumentStatusBadge({ status }: Props) {
  const info = statusMap[status] ?? {
    label: 'Unknown',
    className: 'bg-gray-400 text-white',
  };

  return (
    <span className={`px-2 py-1 rounded text-xs font-semibold ${info.className}`}>
      {info.label}
    </span>
  );
}
