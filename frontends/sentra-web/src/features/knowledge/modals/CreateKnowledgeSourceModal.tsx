// features/knowledge/modals/CreateKnowledgeSourceModal.tsx
import { useState } from 'react';
import { X } from 'lucide-react';
import { useKnowledge } from '../useKnowledge';
import type { CreateKnowledgeSourceRequest, KnowledgeSourceType, KnowledgeSourceVisibility } from '../types/knowledgeModels';

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export default function CreateKnowledgeSourceModal({ isOpen, onClose }: Props) {
  const { visibility, loadSources, createNewSource } = useKnowledge();
  const [creating, setCreating] = useState(false);

  const [form, setForm] = useState<CreateKnowledgeSourceRequest>({
    name: '',
    type: 'manual',
    visibility,
    description: '',
    path: '',
    auto_index: true,
  });

  const handleChange = (field: keyof CreateKnowledgeSourceRequest, value: string | boolean) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    if (!form.name.trim()) return;
    setCreating(true);

    try {

      await createNewSource({
        ...form,
        name: form.name.trim(),
        description: form.description?.trim() || undefined,
        path: form.path?.trim() || undefined,
      });

      loadSources(true);
      onClose();
    } catch (err) {
      console.error(err);
      alert('Failed to create source');
    } finally {
      setCreating(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-[var(--sentra-primary-dark)] w-full max-w-lg rounded-lg p-6 border border-[var(--sentra-accent-light)] relative">
        <button
          onClick={onClose}
          disabled={creating}
          className="absolute top-3 right-3 text-[var(--sentra-text-muted)] hover:text-white"
        >
          <X className="w-5 h-5" />
        </button>

        <h2 className="text-lg font-semibold mb-4">➕ Create Knowledge Source</h2>

        <div className="space-y-3">
          <input
            type="text"
            className="w-full px-3 py-2 rounded bg-[var(--sentra-primary)]"
            placeholder="Source name"
            value={form.name}
            onChange={(e) => handleChange('name', e.target.value)}
            disabled={creating}
          />

          <textarea
            placeholder="Optional description"
            className="w-full px-3 py-2 rounded bg-[var(--sentra-primary)]"
            rows={3}
            value={form.description}
            onChange={(e) => handleChange('description', e.target.value)}
            disabled={creating}
          />

          <div className="flex gap-3">
            <select
              className="flex-1 px-3 py-2 rounded bg-[var(--sentra-primary)]"
              value={form.type}
              onChange={(e) => handleChange('type', e.target.value as KnowledgeSourceType)}
              disabled={creating}
            >
              <option value="manual">Manual</option>
              <option value="folder">Folder</option>
              <option value="upload">Upload</option>
              <option value="external_api">External API</option>
              <option value="mcp_tool">MCP Tool</option>
            </select>

            <select
              className="flex-1 px-3 py-2 rounded bg-[var(--sentra-primary)]"
              value={form.visibility}
              onChange={(e) => handleChange('visibility', e.target.value as KnowledgeSourceVisibility)}
              disabled={creating}
            >
              <option value="private">Private</option>
              <option value="shared">Shared</option>
              <option value="org-wide">Organization</option>
            </select>
          </div>

          {(form.type === 'folder' || form.type === 'external_api') && (
            <input
              type="text"
              placeholder={form.type === 'folder' ? '/path/to/folder' : 'https://api.example.com'}
              className="w-full px-3 py-2 rounded bg-[var(--sentra-primary)]"
              value={form.path}
              onChange={(e) => handleChange('path', e.target.value)}
              disabled={creating}
            />
          )}

          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={form.auto_index}
              onChange={(e) => handleChange('auto_index', e.target.checked)}
              disabled={creating}
            />
            Enable auto-indexing
          </label>
        </div>

        <div className="flex justify-end mt-4 gap-2">
          <button onClick={onClose} disabled={creating} className="btn btn-secondary">
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={creating || !form.name.trim()}
            className="btn btn-primary"
          >
            {creating ? 'Creating...' : 'Create'}
          </button>
        </div>
      </div>
    </div>
  );
}
