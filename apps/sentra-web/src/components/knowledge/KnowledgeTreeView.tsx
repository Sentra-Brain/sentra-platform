// src/components/knowledge/KnowledgeTreeView.tsx
// Tree-based knowledge explorer component
import React from 'react';
import { ChevronRight, ChevronDown, RefreshCw, Folder, File, Upload, Plus } from 'lucide-react';
import type { KnowledgeTreeNode } from '../../models/knowledgeModels';
import { useKnowledge } from '../../hooks/useKnowledge';
import StatusBadge from './StatusBadge';
import UploadDialog from './UploadDialog';
import CreateKnowledgeSourceDialog from './CreateKnowledgeSourceDialog';
import './KnowledgeTreeView.css';

const KnowledgeTreeView: React.FC = () => {
  const {
    treeNodes,
    selectedNode,
    loading,
    error,
    showUploadDialog,
    showCreateSourceDialog,
    refresh,
    selectNode,
    setShowUploadDialog,
    setShowCreateSourceDialog,
    knowledgeSources,
    getUserUploadSource,
  } = useKnowledge();

  const renderTreeNode = (node: KnowledgeTreeNode, level = 0): React.ReactNode => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = node.expanded;
    const isSelected = selectedNode?.id === node.id;

    const getNodeIcon = () => {
      switch (node.type) {
        case 'visibility-group':
          return hasChildren && isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />;
        case 'knowledge-source':
          return hasChildren && isExpanded ? <ChevronDown size={16} /> : hasChildren ? <ChevronRight size={16} /> : <Folder size={16} />;
        case 'document':
          return <File size={16} />;
        default:
          return null;
      }
    };

    const getNodeInfo = () => {
      if (node.type === 'knowledge-source' && node.knowledgeSource) {
        return (
          <div className="tree-node-info">
            <StatusBadge status={node.knowledgeSource.status} />
            {node.documentCount !== undefined && (
              <span className="document-count">
                {node.documentCount} docs
              </span>
            )}
          </div>
        );
      }
      if (node.type === 'document' && node.document) {
        return <StatusBadge status={node.document.status} />;
      }
      return null;
    };

    return (
      <div key={node.id}>
        <div
          className={`tree-node ${isSelected ? 'selected' : ''}`}
          style={{ paddingLeft: `${level * 20 + 8}px` }}
          onClick={() => selectNode(node)}
        >
          <div className="tree-node-content">
            {getNodeIcon()}
            <span className="tree-node-name">{node.name}</span>
          </div>
          {getNodeInfo()}
        </div>
        {hasChildren && isExpanded && (
          <div>
            {node.children!.map((child) => renderTreeNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  const handleUploadComplete = () => {
    refresh(); // Refresh the tree to show new uploads
  };

  const handleCreateSourceComplete = () => {
    refresh(); // Refresh the tree to show new knowledge source
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
    <div className="knowledge-tree">
      <div className="knowledge-tree-header">
        <div className="knowledge-tree-title">
          <h2>Knowledge Explorer</h2>
          <button
            onClick={refresh}
            className="refresh-button"
            title="Refresh"
          >
            <RefreshCw size={16} />
          </button>
        </div>
        
        {/* Upload Actions */}
        <div className="upload-actions">
          <button
            onClick={() => setShowUploadDialog(true)}
            className="btn btn-primary"
            title="Upload documents to an existing knowledge source"
          >
            <Upload size={16} />
            Upload Documents
          </button>
          <button
            onClick={() => setShowCreateSourceDialog(true)}
            className="btn btn-success"
            title="Create a new knowledge source from folder upload"
          >
            <Plus size={16} />
          </button>
        </div>
      </div>
      
      <div className="tree-content">
        {treeNodes.map((node) => renderTreeNode(node))}
      </div>

      {/* Upload Dialog */}
      <UploadDialog
        isOpen={showUploadDialog}
        onClose={() => setShowUploadDialog(false)}
        onUploadComplete={handleUploadComplete}
        knowledgeSources={knowledgeSources}
        defaultKnowledgeSourceId={getUserUploadSource()?.id}
      />

      {/* Create Knowledge Source Dialog */}
      <CreateKnowledgeSourceDialog
        isOpen={showCreateSourceDialog}
        onClose={() => setShowCreateSourceDialog(false)}
        onCreateComplete={handleCreateSourceComplete}
      />
    </div>
  );
};

export default KnowledgeTreeView;