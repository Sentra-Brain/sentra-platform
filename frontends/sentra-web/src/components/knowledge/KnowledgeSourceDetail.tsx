// src/components/knowledge/KnowledgeSourceDetail.tsx
// Detail view for a specific knowledge source and its documents
import React, { useEffect, useState } from 'react';
import { ArrowLeft, RefreshCw, Power, PowerOff, Upload, Settings, Calendar, User, Folder } from 'lucide-react';
import { useKnowledgeSources } from '../../hooks/useKnowledgeSources';
import { useDocuments } from '../../hooks/useDocuments';
import { useKnowledgeNavigation } from '../../hooks/useKnowledgeNavigation';
import { notifySuccess, notifyError } from '../../lib/notify';
import StatusBadge from './StatusBadge';
import DocumentCard from './DocumentCard';
import './KnowledgeComponents.css';

interface KnowledgeSourceDetailProps {
  sourceId: string;
  onUpload: () => void;
}

const KnowledgeSourceDetail: React.FC<KnowledgeSourceDetailProps> = ({ 
  sourceId, 
  onUpload 
}) => {
  const { getSourceById, updateSourceStatus } = useKnowledgeSources();
  const { 
    loadDocumentsForSource, 
    getDocumentsForSource, 
    isLoadingSource,
    refreshDocumentsForSource 
  } = useDocuments();
  const { navigateToKnowledgeHome } = useKnowledgeNavigation();
  
  const [isTogglingStatus, setIsTogglingStatus] = useState(false);
  
  const source = getSourceById(sourceId);
  const documents = getDocumentsForSource(sourceId);
  const loadingDocuments = isLoadingSource(sourceId);

  useEffect(() => {
    if (sourceId) {
      loadDocumentsForSource(sourceId);
    }
  }, [sourceId, loadDocumentsForSource]);

  const handleToggleStatus = async () => {
    if (!source) return;
    
    const newStatus = source.status !== 'active';
    setIsTogglingStatus(true);
    try {
      await updateSourceStatus(source.id, newStatus);
      notifySuccess(`Knowledge source ${newStatus ? 'enabled' : 'disabled'} successfully`);
    } catch (error) {
      notifyError(error);
    } finally {
      setIsTogglingStatus(false);
    }
  };

  const handleRefreshDocuments = () => {
    refreshDocumentsForSource(sourceId);
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

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'upload':
        return '📁';
      case 'folder':
        return '🗂️';
      case 'external_api':
        return '🔗';
      case 'manual':
        return '✏️';
      case 'mcp_tool':
        return '🔧';
      default:
        return '📄';
    }
  };

  if (!source) {
    return (
      <div className="error-state">
        <p className="error-text">Knowledge source not found</p>
        <button onClick={navigateToKnowledgeHome} className="btn btn-primary">
          <ArrowLeft size={16} />
          Back to Knowledge
        </button>
      </div>
    );
  }

  return (
    <div className="knowledge-source-detail">
      <div className="detail-header">
        <button
          onClick={navigateToKnowledgeHome}
          className="back-button"
          title="Back to knowledge sources"
        >
          <ArrowLeft size={16} />
        </button>
        
        <div className="detail-title-section">
          <span className="detail-title-icon">{getTypeIcon(source.type)}</span>
          <div>
            <h1 className="detail-title">{source.name}</h1>
            <p className="detail-subtitle">
              {source.type.replace('_', ' ')} Source • {source.visibility.replace('-', ' ')}
            </p>
          </div>
        </div>
        
        <div className="detail-header-actions">
          <StatusBadge status={source.status} />
          <button
            onClick={handleToggleStatus}
            disabled={isTogglingStatus}
            className={`status-toggle-button ${source.status === 'active' ? 'active' : 'inactive'}`}
            title={source.status === 'active' ? 'Disable knowledge source' : 'Enable knowledge source'}
          >
            {source.status === 'active' ? (
              <>
                <PowerOff size={16} />
                Disable
              </>
            ) : (
              <>
                <Power size={16} />
                Enable
              </>
            )}
          </button>
        </div>
      </div>

      {source.description && (
        <div className="detail-section">
          <h3 className="section-title">Description</h3>
          <p className="section-content">{source.description}</p>
        </div>
      )}

      <div className="detail-grid">
        <div className="detail-field">
          <Folder size={16} className="field-icon" />
          <div className="field-content">
            <p className="field-label">Visibility</p>
            <p className="field-value">{source.visibility.replace('-', ' ')}</p>
          </div>
        </div>

        <div className="detail-field">
          <Settings size={16} className="field-icon" />
          <div className="field-content">
            <p className="field-label">Auto-index</p>
            <p className="field-value">{source.auto_index ? 'Enabled' : 'Disabled'}</p>
          </div>
        </div>

        <div className="detail-field">
          <Calendar size={16} className="field-icon" />
          <div className="field-content">
            <p className="field-label">Created</p>
            <p className="field-value">{formatDate(source.created_at)}</p>
          </div>
        </div>

        <div className="detail-field">
          <User size={16} className="field-icon" />
          <div className="field-content">
            <p className="field-label">Created by</p>
            <p className="field-value">{source.created_by?.full_name}</p>
          </div>
        </div>
      </div>

      {source.path && (
        <div className="detail-section">
          <h3 className="section-title">Path</h3>
          <code className="code-block">{source.path}</code>
        </div>
      )}

      <div className="documents-section">
        <div className="documents-header">
          <h3 className="documents-title">Documents ({documents.length})</h3>
          <div className="documents-actions">
            <button
              onClick={onUpload}
              className="btn btn-primary"
              title="Upload documents to this source"
            >
              <Upload size={16} />
              Upload
            </button>
            <button
              onClick={handleRefreshDocuments}
              className="documents-refresh"
              title="Refresh documents"
              disabled={loadingDocuments}
            >
              <RefreshCw size={16} className={loadingDocuments ? 'animate-spin' : ''} />
            </button>
          </div>
        </div>

        {loadingDocuments ? (
          <div className="loading-documents">
            <div className="loading-spinner"></div>
            <p>Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="empty-documents">
            <p className="empty-documents-text">No documents found</p>
            <button onClick={onUpload} className="btn btn-secondary">
              Upload your first document
            </button>
          </div>
        ) : (
          <div className="documents-grid">
            {documents.map((doc) => (
              <DocumentCard key={doc.id} document={doc} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default KnowledgeSourceDetail;