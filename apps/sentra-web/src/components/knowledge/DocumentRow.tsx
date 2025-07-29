// src/components/knowledge/DocumentRow.tsx
// Individual document row component with actions
import React, { useState } from 'react';
import { File, RotateCcw, Trash2, ExternalLink } from 'lucide-react';
import type { Document } from '../../models/knowledgeModels';
import { knowledgeService } from '../../services/knowledgeService';
import { notifySuccess, notifyError } from '../../lib/notify';
import StatusBadge from './StatusBadge';
import './DocumentRow.css';

interface DocumentRowProps {
  document: Document;
  onDocumentUpdated: (document: Document) => void;
  onDocumentClick?: (document: Document) => void;
  userDisplayName?: string;
}

const DocumentRow: React.FC<DocumentRowProps> = ({ 
  document, 
  onDocumentUpdated, 
  onDocumentClick,
  userDisplayName 
}) => {
  const [isReindexing, setIsReindexing] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);

  const handleReindex = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent row click
    setIsReindexing(true);
    try {
      const updatedDocument = await knowledgeService.reindexDocument(document.id);
      onDocumentUpdated(updatedDocument);
      notifySuccess('Document queued for re-indexing');
    } catch (error) {
      notifyError(error);
    } finally {
      setIsReindexing(false);
    }
  };

  const handleRemove = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent row click
    if (!window.confirm('Are you sure you want to remove this document? This action cannot be undone.')) {
      return;
    }
    
    setIsRemoving(true);
    try {
      const updatedDocument = await knowledgeService.removeDocument(document.id);
      onDocumentUpdated(updatedDocument);
      notifySuccess('Document marked for removal');
    } catch (error) {
      notifyError(error);
    } finally {
      setIsRemoving(false);
    }
  };

  const handleRowClick = () => {
    if (onDocumentClick) {
      onDocumentClick(document);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div 
      className={`document-row ${onDocumentClick ? 'clickable' : ''}`}
      onClick={handleRowClick}
    >
      <div className="document-row-main">
        <div className="document-info">
          <File size={16} className="document-icon" />
          <div className="document-details">
            <div className="document-name-section">
              <p className="document-name">{document.display_name}</p>
              {onDocumentClick && (
                <ExternalLink size={14} className="document-link-icon" />
              )}
            </div>
            <p className="document-filename">{document.filename}</p>
            <div className="document-metadata">
              <span className="metadata-item">
                Uploaded: {formatDate(document.uploaded_at)}
              </span>
              {userDisplayName && (
                <span className="metadata-item">
                  by {userDisplayName}
                </span>
              )}
              {document.filetype && (
                <span className="metadata-item">
                  {document.filetype.toUpperCase()}
                </span>
              )}
            </div>
          </div>
        </div>
        
        <div className="document-status-section">
          <StatusBadge status={document.status} className="document-status" />
          {document.chunks_count && (
            <span className="chunks-count">
              {document.chunks_count} chunks
            </span>
          )}
        </div>
      </div>

      <div className="document-actions">
        <button
          onClick={handleReindex}
          disabled={isReindexing}
          className="action-button reindex-button"
          title="Re-index this document"
        >
          <RotateCcw size={16} className={isReindexing ? 'animate-spin' : ''} />
          Re-Index
        </button>
        
        <button
          onClick={handleRemove}
          disabled={isRemoving || document.status === 'to_be_removed'}
          className="action-button remove-button"
          title="Remove this document"
        >
          <Trash2 size={16} />
          Remove
        </button>
      </div>

      {document.error && (
        <div className="document-error">
          <p className="error-text">{document.error}</p>
        </div>
      )}
    </div>
  );
};

export default DocumentRow;