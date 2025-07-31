// src/components/knowledge/KnowledgeDetailPanel.tsx
// Detail panel for selected knowledge source or document
import React, { useState, useEffect, useCallback } from 'react';
import { RefreshCw, Folder, File, Calendar, User, Settings, Power, PowerOff } from 'lucide-react';
import type {
  KnowledgeSource,
  Document,
  KnowledgeSourceType,
  KnowledgeTreeNode,
} from '../../models/knowledgeModels';
import { KnowledgeSourceType as KSType } from '../../models/knowledgeModels';
import { knowledgeService } from '../../services/knowledgeService';
import { useKnowledge } from '../../hooks/useKnowledge';
import StatusBadge from './StatusBadge';
import DocumentRow from './DocumentRow';
import { notifySuccess, notifyError } from '../../lib/notify';
import './KnowledgeDetailPanel.css';

const KnowledgeDetailPanel: React.FC = () => {
  const { selectedNode, refresh, navigateToDocument } = useKnowledge();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isTogglingStatus, setIsTogglingStatus] = useState(false);

  // Get display name for the knowledge source creator
  const { displayName: creatorDisplayName } = useUserDisplayName(
    selectedNode?.knowledgeSource?.created_by
  );

  // Get display name for document uploader (when viewing a document)
  const { displayName: uploaderDisplayName } = useUserDisplayName(
    selectedNode?.type === 'document' ? selectedNode.document?.uploaded_by : undefined
  );

  const loadDocuments = useCallback(async (knowledgeSourceId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await knowledgeService.listDocuments(knowledgeSourceId);
      setDocuments(response.documents);
    } catch (err) {
      setError('Failed to load documents');
      console.error('Error loading documents:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const toggleKnowledgeSourceStatus = async (knowledgeSource: KnowledgeSource) => {
    const newStatus = knowledgeSource.status === 'active';
    setIsTogglingStatus(true);
    try {
      await knowledgeService.updateKnowledgeSourceStatus(knowledgeSource.id, !newStatus);
      notifySuccess(`Knowledge source ${newStatus ? 'disabled' : 'enabled'} successfully`);
      refresh(); // Refresh the tree and detail panel
    } catch (error) {
      notifyError(error);
    } finally {
      setIsTogglingStatus(false);
    }
  };

  const handleDocumentUpdated = (updatedDocument: Document) => {
    setDocuments(prev => 
      prev.map(doc => doc.id === updatedDocument.id ? updatedDocument : doc)
    );
    refresh(); // Also refresh the tree to update counts
  };

  const handleDocumentClick = (document: Document) => {
    // Navigate to document detail using URL-based routing
    navigateToDocument(document.id, document.knowledge_source_id);
  };

  useEffect(() => {
    if (selectedNode?.type === 'knowledge-source' && selectedNode.knowledgeSource) {
      loadDocuments(selectedNode.knowledgeSource.id);
    } else {
      setDocuments([]);
    }
  }, [selectedNode, loadDocuments]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getTypeIcon = (type: KnowledgeSourceType) => {
    switch (type) {
      case KSType.UPLOAD:
        return '📁';
      case KSType.FOLDER:
        return '🗂️';
      case KSType.EXTERNAL_API:
        return '🔗';
      case KSType.MANUAL:
        return '✏️';
      case KSType.MCP_TOOL:
        return '🔧';
      default:
        return '📄';
    }
  };

  const renderKnowledgeSourceDetail = (source: KnowledgeSource) => (
    <div className="detail-content">
      <div className="detail-header">
        <div className="detail-title-section">
          <span className="detail-title-icon">{getTypeIcon(source.type)}</span>
          <div>
            <h2 className="detail-title">{source.name}</h2>
            <p className="detail-subtitle">{source.type.replace('_', ' ')} Source</p>
          </div>
        </div>
        <div className="detail-header-actions">
          <StatusBadge status={source.status} />
          <button
            onClick={() => toggleKnowledgeSourceStatus(source)}
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
          <button
            onClick={() => loadDocuments(source.id)}
            className="documents-refresh"
            title="Refresh documents"
            disabled={loading}
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>

        {loading ? (
          <div className="loading-documents">
            <div className="loading-spinner"></div>
          </div>
        ) : error ? (
          <div className="error-documents">
            <p className="error-documents-text">{error}</p>
          </div>
        ) : documents.length === 0 ? (
          <p className="empty-documents">No documents found</p>
        ) : (
          <div className="documents-list">
            {documents.map((doc) => (
              <DocumentRow
                key={doc.id}
                document={doc}
                onDocumentUpdated={handleDocumentUpdated}
                onDocumentClick={handleDocumentClick}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const renderDocumentDetail = (document: Document) => {
    return (
      <div className="detail-content">
        <div className="detail-header">
          <div className="detail-title-section">
            <File size={24} className="detail-title-icon" />
            <div>
              <h2 className="detail-title">{document.display_name}</h2>
              <p className="detail-subtitle">{document.filename}</p>
            </div>
          </div>
          <StatusBadge status={document.status} />
        </div>

        {document.description && (
          <div className="detail-section">
            <h3 className="section-title">Description</h3>
            <p className="section-content">{document.description}</p>
          </div>
        )}

        <div className="detail-grid">
          <div className="detail-field">
            <div className="field-content">
              <p className="field-label">File Type</p>
              <p className="field-value">{document.filetype.toUpperCase()}</p>
            </div>
          </div>

          <div className="detail-field">
            <div className="field-content">
              <p className="field-label">Created</p>
              <p className="field-value">{formatDate(document.created_at)}</p>
            </div>
          </div>

          <div className="detail-field">
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

        {document.error && (
          <div className="error-section">
            <h3 className="error-section-title">Error</h3>
            <p className="error-section-text">{document.error}</p>
          </div>
        )}

        <div className="detail-section">
          <h3 className="section-title">File Path</h3>
          <code className="code-block">{document.path}</code>
        </div>
      </div>
    );
  };

  const renderVisibilityGroupDetail = (node: KnowledgeTreeNode) => (
    <div className="detail-content">
      <div className="detail-header">
        <div className="detail-title-section">
          <Folder size={24} className="detail-title-icon" />
          <div>
            <h2 className="detail-title">{node.name}</h2>
            <p className="detail-subtitle">Knowledge visibility group</p>
          </div>
        </div>
      </div>

      <div className="empty-state">
        <div className="empty-state-content">
          <p className="empty-state-text">Select a knowledge source or document to view details</p>
        </div>
      </div>
    </div>
  );

  if (!selectedNode) {
    return (
      <div className="knowledge-detail-panel">
        <div className="empty-state">
          <div className="empty-state-content">
            <Folder size={48} className="empty-state-icon" />
            <h3 className="empty-state-title">Knowledge Management</h3>
            <p className="empty-state-text">Select an item from the explorer to view details</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="knowledge-detail-panel">
      <div className="detail-breadcrumb">
        <div className="breadcrumb-nav">
          <span>Knowledge</span>
          <span className="breadcrumb-separator">›</span>
          <span className="breadcrumb-current">
            {selectedNode.visibility?.replace('-', ' ') || 'Details'}
          </span>
          {selectedNode.type !== 'visibility-group' && (
            <>
              <span className="breadcrumb-separator">›</span>
              <span className="breadcrumb-current">{selectedNode.name}</span>
            </>
          )}
        </div>
      </div>

      {selectedNode.type === 'knowledge-source' && selectedNode.knowledgeSource
        ? renderKnowledgeSourceDetail(selectedNode.knowledgeSource)
        : selectedNode.type === 'document' && selectedNode.document
          ? renderDocumentDetail(selectedNode.document)
          : renderVisibilityGroupDetail(selectedNode)}
    </div>
  );
};

export default KnowledgeDetailPanel;
