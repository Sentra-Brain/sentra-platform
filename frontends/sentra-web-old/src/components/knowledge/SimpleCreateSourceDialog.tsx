// src/components/knowledge/SimpleCreateSourceDialog.tsx
// Simplified create knowledge source dialog
import React, { useState } from 'react';
import { X } from 'lucide-react';
import { useKnowledgeSources } from '../../hooks/useKnowledgeSources';
import { notifySuccess, notifyError } from '../../lib/notify';
import type { CreateKnowledgeSourceRequest, KnowledgeSourceType, KnowledgeSourceVisibility } from '../../models/knowledgeModels';
import './DialogComponents.css';

interface SimpleCreateSourceDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateComplete?: () => void;
}

const SimpleCreateSourceDialog: React.FC<SimpleCreateSourceDialogProps> = ({
  isOpen,
  onClose,
  onCreateComplete,
}) => {
  const { createSource } = useKnowledgeSources();
  const [formData, setFormData] = useState<CreateKnowledgeSourceRequest>({
    name: '',
    type: 'manual' as KnowledgeSourceType,
    visibility: 'private' as KnowledgeSourceVisibility,
    description: '',
    path: '',
    auto_index: true,
  });
  const [creating, setCreating] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      notifyError('Please enter a name for the knowledge source');
      return;
    }

    setCreating(true);
    try {
      await createSource({
        ...formData,
        name: formData.name.trim(),
        description: formData.description?.trim() || undefined,
        path: formData.path?.trim() || undefined,
      });
      
      notifySuccess('Knowledge source created successfully');
      handleCancel();
      onCreateComplete?.();
    } catch (error) {
      notifyError(error);
    } finally {
      setCreating(false);
    }
  };

  const handleCancel = () => {
    if (!creating) {
      setFormData({
        name: '',
        type: 'manual',
        visibility: 'private',
        description: '',
        path: '',
        auto_index: true,
      });
      onClose();
    }
  };

  const handleInputChange = (
    field: keyof CreateKnowledgeSourceRequest,
    value: string | boolean
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (!isOpen) return null;

  return (
    <div className="dialog-overlay">
      <div className="dialog">
        <div className="dialog-header">
          <h3 className="dialog-title">Create Knowledge Source</h3>
          <button
            onClick={handleCancel}
            className="dialog-close"
            disabled={creating}
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="dialog-content">
            <div className="form-group">
              <label htmlFor="name" className="form-label">
                Name <span className="required">*</span>
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                className="form-input"
                placeholder="Enter knowledge source name"
                required
                disabled={creating}
              />
            </div>

            <div className="form-group">
              <label htmlFor="description" className="form-label">
                Description
              </label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                className="form-textarea"
                placeholder="Optional description"
                rows={3}
                disabled={creating}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="type" className="form-label">
                  Type
                </label>
                <select
                  id="type"
                  value={formData.type}
                  onChange={(e) => handleInputChange('type', e.target.value)}
                  className="form-select"
                  disabled={creating}
                >
                  <option value="manual">Manual</option>
                  <option value="folder">Folder</option>
                  <option value="upload">Upload</option>
                  <option value="external_api">External API</option>
                  <option value="mcp_tool">MCP Tool</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="visibility" className="form-label">
                  Visibility
                </label>
                <select
                  id="visibility"
                  value={formData.visibility}
                  onChange={(e) => handleInputChange('visibility', e.target.value)}
                  className="form-select"
                  disabled={creating}
                >
                  <option value="private">Private</option>
                  <option value="shared">Shared</option>
                  <option value="org-wide">Organization-Wide</option>
                </select>
              </div>
            </div>

            {(formData.type === 'folder' || formData.type === 'external_api') && (
              <div className="form-group">
                <label htmlFor="path" className="form-label">
                  Path {formData.type === 'folder' ? '(Folder)' : '(URL)'}
                </label>
                <input
                  type="text"
                  id="path"
                  value={formData.path}
                  onChange={(e) => handleInputChange('path', e.target.value)}
                  className="form-input"
                  placeholder={
                    formData.type === 'folder' 
                      ? '/path/to/folder' 
                      : 'https://api.example.com'
                  }
                  disabled={creating}
                />
              </div>
            )}

            <div className="form-group">
              <label className="form-checkbox">
                <input
                  type="checkbox"
                  checked={formData.auto_index}
                  onChange={(e) => handleInputChange('auto_index', e.target.checked)}
                  disabled={creating}
                />
                <span className="form-checkbox-label">Enable auto-indexing</span>
              </label>
              <small className="form-help">
                Automatically index new documents added to this source
              </small>
            </div>
          </div>

          <div className="dialog-footer">
            <button
              type="button"
              onClick={handleCancel}
              className="btn btn-secondary"
              disabled={creating}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={creating || !formData.name.trim()}
            >
              {creating ? 'Creating...' : 'Create Source'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SimpleCreateSourceDialog;