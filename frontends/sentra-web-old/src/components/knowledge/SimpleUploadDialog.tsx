// src/components/knowledge/SimpleUploadDialog.tsx
// Simplified upload dialog for documents
import React, { useState } from 'react';
import { X, Upload, File } from 'lucide-react';
import { useDocuments } from '../../hooks/useDocuments';
import { notifySuccess, notifyError } from '../../lib/notify';
import './DialogComponents.css';

interface SimpleUploadDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadComplete?: () => void;
  knowledgeSourceId: string;
}

const SimpleUploadDialog: React.FC<SimpleUploadDialogProps> = ({
  isOpen,
  onClose,
  onUploadComplete,
  knowledgeSourceId,
}) => {
  const { uploadDocument } = useDocuments();
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    try {
      // Upload files one by one
      for (const file of selectedFiles) {
        const displayName = file.name.replace(/\.[^/.]+$/, ''); // Remove extension
        await uploadDocument(knowledgeSourceId, file, { display_name: displayName });
      }
      
      notifySuccess(`Successfully uploaded ${selectedFiles.length} file(s)`);
      setSelectedFiles([]);
      onUploadComplete?.();
      onClose();
    } catch (error) {
      notifyError(error);
    } finally {
      setUploading(false);
    }
  };

  const handleCancel = () => {
    if (!uploading) {
      setSelectedFiles([]);
      onClose();
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (!isOpen) return null;

  return (
    <div className="dialog-overlay">
      <div className="dialog">
        <div className="dialog-header">
          <h3 className="dialog-title">Upload Documents</h3>
          <button
            onClick={handleCancel}
            className="dialog-close"
            disabled={uploading}
          >
            <X size={20} />
          </button>
        </div>

        <div className="dialog-content">
          <div className="upload-area">
            <div className="file-input-wrapper">
              <input
                type="file"
                id="file-input"
                multiple
                accept=".pdf,.docx,.txt,.md"
                onChange={handleFileSelect}
                disabled={uploading}
                className="file-input"
              />
              <label htmlFor="file-input" className="file-input-label">
                <Upload size={24} />
                <span>Click to select files or drag and drop</span>
                <small>Supported: PDF, DOCX, TXT, MD</small>
              </label>
            </div>

            {selectedFiles.length > 0 && (
              <div className="selected-files">
                <h4>Selected Files ({selectedFiles.length})</h4>
                <div className="files-list">
                  {selectedFiles.map((file, index) => (
                    <div key={index} className="file-item">
                      <File size={16} />
                      <div className="file-info">
                        <span className="file-name">{file.name}</span>
                        <span className="file-size">{formatFileSize(file.size)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="dialog-footer">
          <button
            onClick={handleCancel}
            className="btn btn-secondary"
            disabled={uploading}
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            className="btn btn-primary"
            disabled={selectedFiles.length === 0 || uploading}
          >
            {uploading ? 'Uploading...' : `Upload ${selectedFiles.length} file(s)`}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SimpleUploadDialog;