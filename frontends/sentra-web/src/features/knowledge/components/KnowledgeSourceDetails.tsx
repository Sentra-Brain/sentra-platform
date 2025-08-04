import { Calendar, UserCircle, Settings } from 'lucide-react';
import type { KnowledgeSource } from '../types/knowledgeModels';

interface Props {
  source: KnowledgeSource;
}

export default function KnowledgeSourceDetails({ source }: Props) {
  const statusBadge = {
    active: (
      <span className="bg-green-800 text-green-300 text-xs px-2 py-0.5 rounded-full border border-green-600">
        ✔ Active
      </span>
    ),
    error: (
      <span className="bg-red-800 text-red-300 text-xs px-2 py-0.5 rounded-full border border-red-600">
        ✖ Error
      </span>
    ),
    disabled: (
      <span className="bg-yellow-800 text-yellow-200 text-xs px-2 py-0.5 rounded-full border border-yellow-600">
        ⚠ Disabled
      </span>
    ),
  };

  return (
    <div className="space-y-6 text-sm">
      {/* Nombre y status */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">{source.name}</h2>
          {source.description && (
            <div className="text-muted text-xs italic">{source.description}</div>
          )}
        </div>
        {statusBadge[source.status]}
      </div>

      {/* Grid de metadata */}
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <div className="text-muted uppercase text-xs">Visibility</div>
          <div className="font-medium">{source.visibility}</div>
        </div>

        <div>
          <div className="text-muted uppercase text-xs flex items-center gap-1">
            <Settings className="w-4 h-4" />
            Auto-index
          </div>
          <div className="font-medium">
            {source.auto_index ? 'Enabled' : 'Disabled'}
          </div>
        </div>

        <div>
          <div className="text-muted uppercase text-xs flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            Created
          </div>
          <div className="font-medium">
            {new Date(source.created_at).toLocaleString(undefined, {
              dateStyle: 'medium',
              timeStyle: 'short',
            })}
          </div>
        </div>

        <div>
          <div className="text-muted uppercase text-xs flex items-center gap-1">
            <UserCircle className="w-4 h-4" />
            Created by
          </div>
          <div className="font-medium">{source.created_by.full_name}</div>
        </div>
      </div>
    </div>
  );
}
