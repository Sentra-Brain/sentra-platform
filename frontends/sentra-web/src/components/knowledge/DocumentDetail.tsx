// src/components/knowledge/DocumentDetail.tsx
// Detail view for a specific document
import React from 'react';
import { ArrowLeft, File, Calendar, User, RefreshCw, Trash2 } from 'lucide-react';
import { useDocuments } from '../../hooks/useDocuments';
import { useKnowledgeSources } from '../../hooks/useKnowledgeSources';
import { useKnowledgeNavigation } from '../../hooks/useKnowledgeNavigation';
import { notifySuccess, notifyError } from '../../lib/notify';
import StatusBadge from './StatusBadge';
import './KnowledgeComponents.css';

interface DocumentDetailProps {
  documentId: string;
}

const DocumentDetail: React.FC<DocumentDetailProps> = ({ documentId }) => {
  const { getDocumentById, removeDocument, reindexDocument } = useDocuments();
  const { getSourceById } = useKnowledgeSources();
  const { navigateToKnowledgeHome, navigateToKnowledgeSource } = useKnowledgeNavigation();
  
  const document = getDocumentById(documentId);
  const source = document ? getSourceById(document.knowledge_source_id) : undefined;

  const handleReindex = async () => {
    if (!document) return;
    
    try {
      await reindexDocument(document.id);
      notifySuccess('Document reindexing started');
    } catch (error) {
      notifyError(error);
    }
  };

  const handleRemove = async () => {
    if (!document) return;
    
    if (!confirm(`Are you sure you want to remove "${document.display_name}"?`)) {
      return;
    }
    
    try {
      await removeDocument(document.id);
      notifySuccess('Document marked for removal');
      navigateToKnowledgeHome();
    } catch (error) {
      notifyError(error);
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

  if (!document) {
    return (
      <div className="error-state">
        <p className="error-text">Document not found</p>
        <button onClick={navigateToKnowledgeHome} className="btn btn-primary">
          <ArrowLeft size={16} />
          Back to Knowledge
        </button>
      </div>
    );
  }

  return (
    <div className="document-detail">
      <div className="detail-header">
        <button
          onClick={() => source ? navigateToKnowledgeSource(source.id) : navigateToKnowledgeHome()}
          className="back-button"
          title="Back"
        >
          <ArrowLeft size={16} />
        </button>
        
        <div className="detail-title-section">
          <span className="detail-title-icon">{getFileIcon(document.filetype)}</span>
          <div>
            <h1 className="detail-title">{document.display_name}</h1>
            <p className="detail-subtitle">{document.filename}</p>
          </div>
        </div>
        
        <div className="detail-header-actions">
          <StatusBadge status={document.status} />
          <button
            onClick={handleReindex}
            className="btn btn-secondary"
            title="Reindex document"
          >
            <RefreshCw size={16} />
            Reindex
          </button>
          <button
            onClick={handleRemove}
            className="btn btn-danger"
            title="Remove document"
          >
            <Trash2 size={16} />
            Remove
          </button>
        </div>
      </div>

      {source && (
        <div className="detail-breadcrumb">
          <button
            onClick={() => navigateToKnowledgeSource(source.id)}
            className="breadcrumb-link"
          >
            {source.name}
          </button>
          <span className="breadcrumb-separator">›</span>
          <span className="breadcrumb-current">{document.display_name}</span>
        </div>
      )}

      {document.description && (
        <div className="detail-section">
          <h3 className="section-title">Description</h3>
          <p className="section-content">{document.description}</p>
        </div>
      )}

      <div className="detail-grid">
        <div className="detail-field">
          <File size={16} className="field-icon" />
          <div className="field-content">
            <p className="field-label">File Type</p>
            <p className="field-value">{document.filetype.toUpperCase()}</p>
          </div>
        </div>

        <div className="detail-field">
          <Calendar size={16} className="field-icon" />
          <div className="field-content">
            <p className="field-label">Created</p>
            <p className="field-value">{formatDate(document.created_at)}</p>
          </div>
        </div>

        <div className="detail-field">
          <User size={16} className="field-icon" />
          <div className="field-content">
            <p className="field-label">Created by</p>
            <p className="field-value">{document.created_by?.full_name}</p>
          </div>
        </div>

        {document.chunks_count && (
          <div className="detail-field">
            <div className="field-content">
              <p className="field-label">Chunks</p>
              <p className="field-value">{document.chunks_count}</p>
            </div>
          </div>
        )}
      </div>

      <div className="detail-section">
        <h3 className="section-title">File Path</h3>
        <code className="code-block">{document.path}</code>
      </div>

      {document.status_message && (
        <div className="detail-section">
          <h3 className="section-title">Status Message</h3>
          <p className="section-content">{document.status_message}</p>
        </div>
      )}

      {document.error && (
        <div className="error-section">
          <h3 className="error-section-title">Error</h3>
          <p className="error-section-text">{document.error}</p>
        </div>
      )}
    </div>
  );
};

export default DocumentDetail;