// src/components/knowledge/KnowledgeSourcesList.tsx
// Simple list of knowledge sources
import React from 'react';
import { Folder, Plus, RefreshCw, Upload } from 'lucide-react';
import { useKnowledgeSources } from '../../hooks/useKnowledgeSources';
import { useKnowledgeNavigation } from '../../hooks/useKnowledgeNavigation';
import StatusBadge from './StatusBadge';
import './KnowledgeComponents.css';

interface KnowledgeSourcesListProps {
  onCreateSource: () => void;
  onUpload: () => void;
}

const KnowledgeSourcesList: React.FC<KnowledgeSourcesListProps> = ({ 
  onCreateSource, 
  onUpload 
}) => {
  const { sources, loading, error, refresh } = useKnowledgeSources();
  const { navigateToKnowledgeSource } = useKnowledgeNavigation();

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

  const formatVisibility = (visibility: string) => {
    return visibility.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading) {
    return (
      <div className="loading-state">
        <div className="loading-spinner"></div>
        <p className="loading-text">Loading knowledge sources...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-state">
        <p className="error-text">{error}</p>
        <button onClick={refresh} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="knowledge-sources-list">
      <div className="knowledge-sources-header">
        <div className="header-title">
          <h2>Knowledge Sources</h2>
          <button
            onClick={refresh}
            className="refresh-button"
            title="Refresh"
          >
            <RefreshCw size={16} />
          </button>
        </div>
        
        <div className="header-actions">
          <button
            onClick={onUpload}
            className="btn btn-primary"
            title="Upload documents"
          >
            <Upload size={16} />
            Upload
          </button>
          <button
            onClick={onCreateSource}
            className="btn btn-success"
            title="Create new knowledge source"
          >
            <Plus size={16} />
            New Source
          </button>
        </div>
      </div>

      {sources.length === 0 ? (
        <div className="empty-state">
          <Folder size={48} className="empty-state-icon" />
          <h3 className="empty-state-title">No Knowledge Sources</h3>
          <p className="empty-state-text">
            Create your first knowledge source or upload documents to get started.
          </p>
        </div>
      ) : (
        <div className="sources-grid">
          {sources.map((source) => (
            <div
              key={source.id}
              className="source-card"
              onClick={() => navigateToKnowledgeSource(source.id)}
            >
              <div className="source-card-header">
                <div className="source-icon">
                  {getTypeIcon(source.type)}
                </div>
                <div className="source-info">
                  <h3 className="source-name">{source.name}</h3>
                  <p className="source-type">
                    {source.type.replace('_', ' ')} • {formatVisibility(source.visibility)}
                  </p>
                </div>
                <StatusBadge status={source.status} />
              </div>
              
              {source.description && (
                <p className="source-description">{source.description}</p>
              )}
              
              <div className="source-footer">
                <span className="source-meta">
                  Created by {source.created_by?.full_name}
                </span>
                <span className="source-meta">
                  {new Date(source.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default KnowledgeSourcesList;