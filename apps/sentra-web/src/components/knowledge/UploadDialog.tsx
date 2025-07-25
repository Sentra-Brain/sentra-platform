// src/components/knowledge/UploadDialog.tsx
// Dialog for uploading documents to knowledge sources
import React, { useState, useRef } from 'react';
import { X, Upload, Folder, AlertCircle } from 'lucide-react';
import type { KnowledgeSource } from '../../models/knowledgeModels';
import { KnowledgeSourceType } from '../../models/knowledgeModels';
import { knowledgeService } from '../../services/knowledgeService';
import './UploadDialog.css';

interface UploadDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadComplete: () => void;
  knowledgeSources: KnowledgeSource[];
  defaultKnowledgeSourceId?: string;
}

const UploadDialog: React.FC<UploadDialogProps> = ({
  isOpen,
  onClose,
  onUploadComplete,
  knowledgeSources,
  defaultKnowledgeSourceId,
}) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [selectedKnowledgeSourceId, setSelectedKnowledgeSourceId] = useState<string>(
    defaultKnowledgeSourceId || ''
  );
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setSelectedFiles(files);
    setError(null);
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const isUploadAllowed = (source: KnowledgeSource): boolean => {
    // Allow uploads to UPLOAD type sources and sources the user can write to
    return source.type === KnowledgeSourceType.UPLOAD || 
           source.type === KnowledgeSourceType.FOLDER;
  };

  const getFilteredSources = () => {
    return knowledgeSources.filter(isUploadAllowed);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one file');
      return;
    }

    if (!selectedKnowledgeSourceId) {
      setError('Please select a knowledge source');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      await knowledgeService.uploadMultipleDocuments(
        selectedFiles,
        selectedKnowledgeSourceId
      );
      
      // Reset form and close dialog
      setSelectedFiles([]);
      setSelectedKnowledgeSourceId(defaultKnowledgeSourceId || '');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      onUploadComplete();
      onClose();
    } catch (err) {
      console.error('Upload failed:', err);
      setError('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const files = Array.from(event.dataTransfer.files);
    setSelectedFiles(prev => [...prev, ...files]);
    setError(null);
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  if (!isOpen) return null;

  const filteredSources = getFilteredSources();

  return (
    <div className="upload-dialog-overlay">
      <div className="upload-dialog">
        <div className="upload-dialog-header">
          <h2 className="upload-dialog-title">Upload Documents</h2>
          <button
            onClick={onClose}
            className="dialog-close-button"
            disabled={uploading}
          >
            <X size={20} />
          </button>
        </div>

        <div className="upload-dialog-content">
          {/* Knowledge Source Selection */}
          <div className="form-group">
            <label className="form-label">
              Upload to Knowledge Source
            </label>
            <select
              value={selectedKnowledgeSourceId}
              onChange={(e) => setSelectedKnowledgeSourceId(e.target.value)}
              className="form-select"
              disabled={uploading}
            >
              <option value="">Select a knowledge source...</option>
              {filteredSources.map((source) => (
                <option key={source.id} value={source.id}>
                  {source.name} ({source.visibility})
                </option>
              ))}
            </select>
            {filteredSources.length === 0 && (
              <p className="form-help-text">
                No knowledge sources available for upload. Contact your administrator.
              </p>
            )}
          </div>

          {/* File Selection */}
          <div className="form-group">
            <label className="form-label">
              Select Files
            </label>
            <div
              className="upload-drop-zone"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <Upload className="upload-icon" size={48} />
              <p className="upload-text">
                Drag and drop files here, or{' '}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="upload-browse-button"
                  disabled={uploading}
                >
                  browse
                </button>
              </p>
              <p className="upload-supported-formats">
                Supported formats: PDF, DOCX, TXT, MD
              </p>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.docx,.txt,.md"
                onChange={handleFileSelect}
                className="upload-file-input"
                disabled={uploading}
              />
            </div>
          </div>

          {/* Selected Files */}
          {selectedFiles.length > 0 && (
            <div className="selected-files">
              <h3 className="selected-files-title">
                Selected Files ({selectedFiles.length})
              </h3>
              <div className="selected-files-list">
                {selectedFiles.map((file, index) => (
                  <div key={index} className="selected-file-item">
                    <div className="selected-file-info">
                      <Folder size={16} className="selected-file-icon" />
                      <span className="selected-file-name">{file.name}</span>
                      <span className="selected-file-size">
                        ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </span>
                    </div>
                    {!uploading && (
                      <button
                        onClick={() => removeFile(index)}
                        className="remove-file-button"
                      >
                        <X size={16} />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="error-message">
              <AlertCircle size={16} className="error-icon" />
              <p className="error-text">{error}</p>
            </div>
          )}
        </div>

        {/* Dialog Actions */}
        <div className="upload-dialog-footer">
          <div className="upload-dialog-status">
            {selectedFiles.length > 0 && 
              `${selectedFiles.length} file${selectedFiles.length === 1 ? '' : 's'} selected`
            }
          </div>
          <div className="upload-dialog-actions">
            <button
              onClick={onClose}
              className="btn-secondary"
              disabled={uploading}
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              disabled={selectedFiles.length === 0 || !selectedKnowledgeSourceId || uploading}
              className="btn-upload"
            >
              {uploading ? (
                <>
                  <div className="upload-spinner"></div>
                  Uploading...
                </>
              ) : (
                <>
                  <Upload size={16} />
                  Upload {selectedFiles.length > 1 ? `${selectedFiles.length} Files` : 'File'}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadDialog;