// src/components/knowledge/CreateKnowledgeSourceDialog.tsx
// Dialog for creating new knowledge sources from folder uploads
import React, { useState, useRef } from 'react';
import { X, FolderPlus, Upload, AlertCircle, CheckCircle } from 'lucide-react';
import type { CreateKnowledgeSourceRequest } from '../../models/knowledgeModels';
import { KnowledgeSourceType, KnowledgeSourceVisibility } from '../../models/knowledgeModels';
import { knowledgeService } from '../../services/knowledgeService';
import './CreateKnowledgeSourceDialog.css';

interface CreateKnowledgeSourceDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateComplete: () => void;
}

const CreateKnowledgeSourceDialog: React.FC<CreateKnowledgeSourceDialogProps> = ({
  isOpen,
  onClose,
  onCreateComplete,
}) => {
  const [step, setStep] = useState<'metadata' | 'upload' | 'progress'>('metadata');
  const [formData, setFormData] = useState<CreateKnowledgeSourceRequest>({
    name: '',
    type: KnowledgeSourceType.UPLOAD, // For folder uploads
    description: '',
    visibility: KnowledgeSourceVisibility.PRIVATE,
    auto_index: true,
  });
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({ uploaded: 0, total: 0 });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const resetForm = () => {
    setStep('metadata');
    setFormData({
      name: '',
      type: KnowledgeSourceType.UPLOAD,
      description: '',
      visibility: KnowledgeSourceVisibility.PRIVATE,
      auto_index: true,
    });
    setSelectedFiles([]);
    setUploading(false);
    setUploadProgress({ uploaded: 0, total: 0 });
    setError(null);
    setSuccess(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleClose = () => {
    if (!uploading) {
      resetForm();
      onClose();
    }
  };

  const handleInputChange = (
    field: keyof CreateKnowledgeSourceRequest,
    value: string | boolean
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setSelectedFiles(files);
    setError(null);
  };

  const handleFolderSelect = () => {
    // Create a file input that accepts directories
    const input = document.createElement('input');
    input.type = 'file';
    input.webkitdirectory = true;
    input.multiple = true;
    input.accept = '.pdf,.docx,.txt,.md';
    
    input.onchange = (e) => {
      const files = Array.from((e.target as HTMLInputElement).files || []);
      // Filter to only supported file types
      const supportedFiles = files.filter(file => 
        /\.(pdf|docx|txt|md)$/i.test(file.name)
      );
      setSelectedFiles(supportedFiles);
      setError(null);
    };
    
    input.click();
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const validateMetadata = (): boolean => {
    if (!formData.name.trim()) {
      setError('Knowledge source name is required');
      return false;
    }
    return true;
  };

  const handleNext = () => {
    if (!validateMetadata()) return;
    setStep('upload');
  };

  const handleBack = () => {
    setStep('metadata');
    setError(null);
  };

  const handleCreate = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one file');
      return;
    }

    setUploading(true);
    setStep('progress');
    setError(null);
    setUploadProgress({ uploaded: 0, total: selectedFiles.length });

    try {
      // Create the knowledge source with folder upload
      await knowledgeService.uploadFolderAsKnowledgeSource(
        selectedFiles,
        formData
      );

      setSuccess(true);
      setUploadProgress({ uploaded: selectedFiles.length, total: selectedFiles.length });
      
      // Wait a moment to show success, then close
      setTimeout(() => {
        onCreateComplete();
        handleClose();
      }, 2000);
    } catch (err) {
      console.error('Failed to create knowledge source:', err);
      setError('Failed to create knowledge source. Please try again.');
      setStep('upload'); // Go back to upload step
    } finally {
      setUploading(false);
    }
  };

  if (!isOpen) return null;

  const renderMetadataStep = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Knowledge Source Name *
        </label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => handleInputChange('name', e.target.value)}
          className="w-full p-2 border border-blue-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Enter a name for your knowledge source"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Description
        </label>
        <textarea
          value={formData.description}
          onChange={(e) => handleInputChange('description', e.target.value)}
          rows={3}
          className="w-full p-2 border border-blue-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Optional description"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Visibility
        </label>
        <select
          value={formData.visibility}
          onChange={(e) => handleInputChange('visibility', e.target.value as KnowledgeSourceVisibility)}
          className="w-full p-2 border border-blue-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-800"
        >
          <option value={KnowledgeSourceVisibility.PRIVATE}>Private</option>
          <option value={KnowledgeSourceVisibility.SHARED}>Shared</option>
          <option value={KnowledgeSourceVisibility.ORG_WIDE}>Organization-Wide</option>
        </select>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="auto_index"
          checked={formData.auto_index}
          onChange={(e) => handleInputChange('auto_index', e.target.checked)}
          className="mr-2"
        />
        <label htmlFor="auto_index" className="text-sm text-gray-300">
          Enable automatic indexing of new documents
        </label>
      </div>
    </div>
  );

  const renderUploadStep = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Select Folder or Files
        </label>
        <div className="space-y-3">
          <button
            type="button"
            onClick={handleFolderSelect}
            className="w-full p-4 border-2 border-dashed border-blue-300 rounded-lg text-center hover:border-blue-400 transition-colors"
          >
            <FolderPlus className="mx-auto h-8 w-8 text-gray-400 mb-2" />
            <p className="text-gray-600 font-medium">Select Folder</p>
            <p className="text-xs text-gray-500">
              Choose a folder to upload all its contents
            </p>
          </button>

          <div className="text-center text-gray-500">or</div>

          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="w-full p-4 border-2 border-dashed border-blue-300 rounded-lg text-center hover:border-blue-400 transition-colors"
          >
            <Upload className="mx-auto h-8 w-8 text-gray-400 mb-2" />
            <p className="text-gray-600 font-medium">Select Individual Files</p>
            <p className="text-xs text-gray-500">
              Choose specific files to upload
            </p>
          </button>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.md"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {selectedFiles.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-300 mb-2">
            Selected Files ({selectedFiles.length})
          </h3>
          <div className="space-y-2 max-h-48 overflow-y-auto border rounded-lg p-3">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-gray-50 rounded"
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <Upload size={16} className="text-gray-400 flex-shrink-0" />
                  <span className="text-sm font-medium truncate">{file.name}</span>
                  <span className="text-xs text-gray-500 flex-shrink-0">
                    ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </span>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-red-600 hover:text-red-700 p-1 flex-shrink-0"
                >
                  <X size={16} />
                </button>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Unsupported file types will be skipped automatically
          </p>
        </div>
      )}
    </div>
  );

  const renderProgressStep = () => (
    <div className="space-y-6 text-center">
      {success ? (
        <div className="space-y-4">
          <CheckCircle className="mx-auto h-16 w-16 text-green-500" />
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              Knowledge Source Created Successfully!
            </h3>
            <p className="text-gray-600 mt-1">
              {formData.name} has been created with {selectedFiles.length} documents
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto"></div>
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              Creating Knowledge Source...
            </h3>
            <p className="text-gray-600 mt-1">
              Uploading {uploadProgress.uploaded} of {uploadProgress.total} files
            </p>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{
                width: `${uploadProgress.total > 0 ? (uploadProgress.uploaded / uploadProgress.total) * 100 : 0}%`
              }}
            ></div>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="create-dialog-overlay">
      <div className="create-dialog">
        <div className="create-dialog-header">
          <h2 className="create-dialog-title">Create Knowledge Source</h2>
          <button
            onClick={handleClose}
            className="dialog-close-button"
            disabled={uploading}
          >
            <X size={20} />
          </button>
        </div>

        <div className="create-dialog-content">
          {step === 'metadata' && renderMetadataStep()}
          {step === 'upload' && renderUploadStep()}
          {step === 'progress' && renderProgressStep()}

          {/* Error Message */}
          {error && (
            <div className="error-message">
              <AlertCircle size={16} className="error-icon" />
              <p className="error-text">{error}</p>
            </div>
          )}
        </div>

        {/* Dialog Actions */}
        {step !== 'progress' && (
          <div className="flex items-center justify-between p-6 border-t">
            <div className="flex gap-2">
              {step === 'upload' && (
                <button
                  onClick={handleBack}
                  className="px-4 py-2 text-gray-300 border border-blue-300 rounded-md hover:bg-gray-800"
                >
                  Back
                </button>
              )}
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleClose}
                className="px-4 py-2 text-gray-300 border border-blue-300 rounded-md hover:bg-gray-800"
                disabled={uploading}
              >
                Cancel
              </button>
              {step === 'metadata' && (
                <button
                  onClick={handleNext}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Next
                </button>
              )}
              {step === 'upload' && (
                <button
                  onClick={handleCreate}
                  disabled={selectedFiles.length === 0}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <FolderPlus size={16} />
                  Create & Upload
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CreateKnowledgeSourceDialog;