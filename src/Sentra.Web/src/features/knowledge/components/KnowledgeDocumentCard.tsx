import type { KnowledgeDocument } from '../types/knowledgeModels';
import { FileText, Loader, CheckCircle2, XCircle } from 'lucide-react';

interface Props {
  document: KnowledgeDocument;
  selected?: boolean;
  onClick?: () => void;
}

export default function KnowledgeDocumentCard({ document, selected, onClick }: Props) {
  return (
    <div
      onClick={onClick}
      className={`cursor-pointer border rounded-md px-3 py-2 transition-colors ${
        selected
          ? 'bg-sentra-accent text-white border-sentra-accent'
          : 'hover:bg-sentra-accent-light border-[var(--sentra-primary-light)]'
      }`}
    >
      <div className="flex items-center gap-2 justify-between">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4" />
          <div className="text-sm font-medium truncate">{document.display_name}</div>
        </div>

        {/* Status icon */}
        <div className="flex items-center gap-1">
          {document.status === 'indexed' && (
            <CheckCircle2 className="text-green-500 w-4 h-4" name="Indexed" />
          )}
          {document.status === 'processing' && (
            <Loader className="animate-spin text-blue-400 w-4 h-4" name ="Processing" />
          )}
          {document.status === 'failed' && (
            <XCircle className="text-red-500 w-4 h-4" name="Failed" />
          )}
        </div>
      </div>
    </div>
  );
}
