// src/components/knowledge/DocumentCard.tsx
// Simple card component for displaying a document
import React, { useState } from 'react';
import { MoreHorizontal, RefreshCw, Trash2 } from 'lucide-react';
import { useDocuments } from '../../hooks/useDocuments';
import { useKnowledgeNavigation } from '../../hooks/useKnowledgeNavigation';
import { notifySuccess, notifyError } from '../../lib/notify';
import StatusBadge from './StatusBadge';
import type { Document } from '../../models/knowledgeModels';
import './KnowledgeComponents.css';

interface DocumentCardProps {
  document: Document;
}

const DocumentCard: React.FC<DocumentCardProps> = ({ document }) => {
  const { removeDocument, reindexDocument } = useDocuments();
  const { navigateToDocument } = useKnowledgeNavigation();
  const [showActions, setShowActions] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleCardClick = () => {
    navigateToDocument(document.id);
  };

  const handleReindex = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsProcessing(true);
    try {
      await reindexDocument(document.id);
      notifySuccess('Document reindexing started');
    } catch (error) {
      notifyError(error);
    } finally {
      setIsProcessing(false);
      setShowActions(false);
    }
  };

  const handleRemove = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(`Are you sure you want to remove "${document.display_name}"?`)) {
      return;
    }
    
    setIsProcessing(true);
    try {
      await removeDocument(document.id);
      notifySuccess('Document marked for removal');
    } catch (error) {
      notifyError(error);
    } finally {
      setIsProcessing(false);
      setShowActions(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getFileIcon = (filetype: string) => {
    switch (filetype.toLowerCase()) {
      case 'pdf':
        return '📄';
      case 'docx':
        return '📝';
      case 'txt':
        return '📋';
      case 'md':
        return '📖';
      default:
        return '📄';
    }
  };

  return (
    <div className="document-card" onClick={handleCardClick}>
      <div className="document-card-header">
        <div className="document-icon">
          {getFileIcon(document.filetype)}
        </div>
        <div className="document-info">
          <h4 className="document-name">{document.display_name}</h4>
          <p className="document-filename">{document.filename}</p>
        </div>
        <div className="document-actions">
          <StatusBadge status={document.status} />
          <button
            className="actions-button"
            onClick={(e) => {
              e.stopPropagation();
              setShowActions(!showActions);
            }}
            disabled={isProcessing}
          >
            <MoreHorizontal size={16} />
          </button>
        </div>
      </div>

      {document.description && (
        <p className="document-description">{document.description}</p>
      )}

      <div className="document-footer">
        <span className="document-meta">
          {document.filetype.toUpperCase()}
        </span>
        {document.chunks_count && (
          <span className="document-meta">
            {document.chunks_count} chunks
          </span>
        )}
        <span className="document-meta">
          {formatDate(document.created_at)}
        </span>
      </div>

      {document.error && (
        <div className="document-error">
          <p className="error-message">{document.error}</p>
        </div>
      )}

      {showActions && (
        <div className="document-actions-menu">
          <button
            onClick={handleReindex}
            className="action-item"
            disabled={isProcessing}
          >
            <RefreshCw size={14} />
            Reindex
          </button>
          <button
            onClick={handleRemove}
            className="action-item action-item-danger"
            disabled={isProcessing}
          >
            <Trash2 size={14} />
            Remove
          </button>
        </div>
      )}
    </div>
  );
};

export default DocumentCard;