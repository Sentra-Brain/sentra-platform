import { X, Edit3, Folder, FileText } from 'lucide-react';

interface ContextChipProps {
  type: 'source' | 'document';
  name: string;
  onRemove: () => void;
  onEdit?: () => void;
}

export default function ContextChip({ type, name, onRemove, onEdit }: ContextChipProps) {
  const Icon = type === 'source' ? Folder : FileText;
  
  return (
    <div className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded-md text-sm border border-blue-200 dark:border-blue-700">
      <Icon size={12} />
      <span className="max-w-32 truncate" title={name}>{name}</span>
      {onEdit && (
        <button
          onClick={onEdit}
          className="p-0.5 hover:bg-blue-200 dark:hover:bg-blue-800/50 rounded transition-colors"
          title="Edit context"
        >
          <Edit3 size={10} />
        </button>
      )}
      <button
        onClick={onRemove}
        className="p-0.5 hover:bg-red-200 dark:hover:bg-red-800/50 rounded transition-colors"
        title="Remove from context"
      >
        <X size={10} />
      </button>
    </div>
  );
}