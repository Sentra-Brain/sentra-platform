// src/components/knowledge/DocumentRow.tsx
// Individual document row component with actions
import React, { useState } from 'react';
import { RotateCcw, Trash2, Edit3 } from 'lucide-react';
import type { Document } from '../../models/knowledgeModels';
import { knowledgeService } from '../../services/knowledgeService';
import { notifySuccess, notifyError } from '../../lib/notify';
import StatusBadge from './StatusBadge';
import './DocumentRow.css';

interface DocumentRowProps {
  document: Document;
  onDocumentUpdated: (document: Document) => void;
  onDocumentClick?: (document: Document) => void;
}

const DocumentRow: React.FC<DocumentRowProps> = ({ 
  document, 
  onDocumentUpdated, 
  onDocumentClick
}) => {
  const [isReindexing, setIsReindexing] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);
  const [isRenaming, setIsRenaming] = useState(false);

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

  const handleRename = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent row click
    const newName = window.prompt('Enter new document name:', document.display_name);
    if (!newName || newName === document.display_name) {
      return;
    }
    
    setIsRenaming(true);
    try {
      // TODO: Implement rename API endpoint when available
      // const updatedDocument = await knowledgeService.renameDocument(document.id, newName);
      // onDocumentUpdated(updatedDocument);
      notifySuccess('Rename functionality will be available soon');
    } catch (error) {
      notifyError(error);
    } finally {
      setIsRenaming(false);
    }
  };

  const handleDocumentNameClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent row click
    if (onDocumentClick) {
      onDocumentClick(document);
    }
  };

  return (
    <div className="document-row">
      <div className="document-row-content">
        <div className="document-info">
          <button
            className="document-name-link"
            onClick={handleDocumentNameClick}
            title="View document details"
          >
            {document.display_name}
          </button>
          <StatusBadge status={document.status} className="document-status" />
        </div>
        
        <div className="document-actions">
          <button
            onClick={handleReindex}
            disabled={isReindexing}
            className="action-button reindex-button"
            title="Re-index this document"
          >
            <RotateCcw size={14} className={isReindexing ? 'animate-spin' : ''} />
          </button>
          
          <button
            onClick={handleRename}
            disabled={isRenaming}
            className="action-button rename-button"
            title="Rename this document"
          >
            <Edit3 size={14} />
          </button>
          
          <button
            onClick={handleRemove}
            disabled={isRemoving || document.status === 'to_be_removed'}
            className="action-button remove-button"
            title="Remove this document"
          >
            <Trash2 size={14} />
          </button>
        </div>
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