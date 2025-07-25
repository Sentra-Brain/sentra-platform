// src/components/knowledge/UploadDialog.tsx
// Dialog for uploading documents to knowledge sources
import React, { useState, useRef } from 'react';
import { X, Upload, Folder, AlertCircle } from 'lucide-react';
import type { KnowledgeSource } from '../../models/knowledgeModels';
import { KnowledgeSourceType } from '../../models/knowledgeModels';
import { knowledgeService } from '../../services/knowledgeService';

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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold">Upload Documents</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded"
            disabled={uploading}
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Knowledge Source Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Upload to Knowledge Source
            </label>
            <select
              value={selectedKnowledgeSourceId}
              onChange={(e) => setSelectedKnowledgeSourceId(e.target.value)}
              className="w-full p-2 border border-blue-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
              <p className="text-sm text-gray-500 mt-1">
                No knowledge sources available for upload. Contact your administrator.
              </p>
            )}
          </div>

          {/* File Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Select Files
            </label>
            <div
              className="border-2 border-dashed border-blue-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-2" />
              <p className="text-gray-600 mb-2">
                Drag and drop files here, or{' '}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="text-blue-600 hover:text-blue-700 font-medium"
                  disabled={uploading}
                >
                  browse
                </button>
              </p>
              <p className="text-xs text-gray-500">
                Supported formats: PDF, DOCX, TXT, MD
              </p>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.docx,.txt,.md"
                onChange={handleFileSelect}
                className="hidden"
                disabled={uploading}
              />
            </div>
          </div>

          {/* Selected Files */}
          {selectedFiles.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-300 mb-2">
                Selected Files ({selectedFiles.length})
              </h3>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {selectedFiles.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded"
                  >
                    <div className="flex items-center gap-2">
                      <Folder size={16} className="text-gray-400" />
                      <span className="text-sm font-medium">{file.name}</span>
                      <span className="text-xs text-gray-500">
                        ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </span>
                    </div>
                    {!uploading && (
                      <button
                        onClick={() => removeFile(index)}
                        className="text-red-600 hover:text-red-700 p-1"
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
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle size={16} className="text-red-600" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}
        </div>

        {/* Dialog Actions */}
        <div className="flex items-center justify-between p-6 border-t bg-gray-50">
          <div className="text-sm text-gray-500">
            {selectedFiles.length > 0 && 
              `${selectedFiles.length} file${selectedFiles.length === 1 ? '' : 's'} selected`
            }
          </div>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-300 border border-blue-300 rounded-md hover:bg-gray-50"
              disabled={uploading}
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              disabled={selectedFiles.length === 0 || !selectedKnowledgeSourceId || uploading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {uploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
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