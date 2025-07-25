// src/components/knowledge/KnowledgeDetailPanel.tsx
// Detail panel for selected knowledge source or document
import React, { useState, useEffect } from 'react';
import { RefreshCw, Folder, File, Calendar, User, Settings } from 'lucide-react';
import type {
  KnowledgeTreeNode,
  KnowledgeSource,
  Document,
  KnowledgeSourceType,
} from '../../models/knowledgeModels';
import { KnowledgeSourceType as KSType } from '../../models/knowledgeModels';
import { knowledgeService } from '../../services/knowledgeService';
import StatusBadge from './StatusBadge';

interface KnowledgeDetailPanelProps {
  selectedNode?: KnowledgeTreeNode;
}

const KnowledgeDetailPanel: React.FC<KnowledgeDetailPanelProps> = ({ selectedNode }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDocuments = async (knowledgeSourceId: string) => {
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
  };

  useEffect(() => {
    if (selectedNode?.type === 'knowledge-source' && selectedNode.knowledgeSource) {
      loadDocuments(selectedNode.knowledgeSource.id);
    } else {
      setDocuments([]);
    }
  }, [selectedNode]);

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
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{getTypeIcon(source.type)}</span>
          <div>
            <h2 className="text-xl font-semibold">{source.name}</h2>
            <p className=" capitalize">{source.type.replace('_', ' ')} Source</p>
          </div>
        </div>
        <StatusBadge status={source.status} />
      </div>

      {source.description && (
        <div>
          <h3 className="font-medium  mb-2">Description</h3>
          <p className="text-gray-300">{source.description}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Folder size={16} className="text-gray-400" />
            <div>
              <p className="text-sm font-medium ">Visibility</p>
              <p className="text-sm  capitalize">{source.visibility.replace('-', ' ')}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Settings size={16} className="text-gray-400" />
            <div>
              <p className="text-sm font-medium ">Auto-index</p>
              <p className="text-sm ">{source.auto_index ? 'Enabled' : 'Disabled'}</p>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Calendar size={16} className="text-gray-400" />
            <div>
              <p className="text-sm font-medium ">Created</p>
              <p className="text-sm ">{formatDate(source.created_at)}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <User size={16} className="text-gray-400" />
            <div>
              <p className="text-sm font-medium ">Created by</p>
              <p className="text-sm ">{source.created_by}</p>
            </div>
          </div>
        </div>
      </div>

      {source.path && (
        <div>
          <h3 className="font-medium  mb-2">Path</h3>
          <code className="block p-2 bg-gray-100 rounded text-sm font-mono">{source.path}</code>
        </div>
      )}

      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-medium ">Documents ({documents.length})</h3>
          <button
            onClick={() => loadDocuments(source.id)}
            className="p-1 hover:bg-gray-100 rounded"
            title="Refresh documents"
            disabled={loading}
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>

        {loading ? (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
          </div>
        ) : error ? (
          <div className="text-center py-4">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        ) : documents.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No documents found</p>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  <File size={16} className="text-gray-400 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-sm truncate">{doc.display_name}</p>
                    <p className="text-xs text-gray-500">{doc.filename}</p>
                  </div>
                </div>
                <StatusBadge status={doc.status} className="ml-2" />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const renderDocumentDetail = (document: Document) => (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <File size={24} className="text-gray-400" />
          <div>
            <h2 className="text-xl font-semibold">{document.display_name}</h2>
            <p className="">{document.filename}</p>
          </div>
        </div>
        <StatusBadge status={document.status} />
      </div>

      {document.description && (
        <div>
          <h3 className="font-medium  mb-2">Description</h3>
          <p className="text-gray-300">{document.description}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-3">
          <div>
            <p className="text-sm font-medium ">File Type</p>
            <p className="text-sm  uppercase">{document.filetype}</p>
          </div>

          <div>
            <p className="text-sm font-medium ">Uploaded</p>
            <p className="text-sm ">{formatDate(document.uploaded_at)}</p>
          </div>
        </div>

        <div className="space-y-3">
          <div>
            <p className="text-sm font-medium ">Uploaded by</p>
            <p className="text-sm ">{document.uploaded_by}</p>
          </div>

          <div>
            <p className="text-sm font-medium ">Knowledge Source</p>
            <p className="text-sm ">{document.knowledge_source_id}</p>
          </div>
        </div>
      </div>

      {document.error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <h3 className="font-medium text-red-900 mb-1">Error</h3>
          <p className="text-sm text-red-300">{document.error}</p>
        </div>
      )}

      <div>
        <h3 className="font-medium  mb-2">File Path</h3>
        <code className="block p-2 bg-gray-200 rounded text-sm font-mono">{document.path}</code>
      </div>
    </div>
  );

  const renderVisibilityGroupDetail = (node: KnowledgeTreeNode) => (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Folder size={24} className="text-gray-400" />
        <div>
          <h2 className="text-xl font-semibold">{node.name}</h2>
          <p className="text-gray-300">Knowledge visibility group</p>
        </div>
      </div>

      <div className="text-center py-8">
        <p className="text-gray-200">Select a knowledge source or document to view details</p>
      </div>
    </div>
  );

  if (!selectedNode) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Folder size={48} className="text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">Knowledge Management</h3>
          <p className="text-gray-200">Select an item from the explorer to view details</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-6 border-b">
        <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
          <span>Knowledge</span>
          <span>›</span>
          <span className="capitalize">
            {selectedNode.visibility?.replace('-', ' ') || 'Details'}
          </span>
          {selectedNode.type !== 'visibility-group' && (
            <>
              <span>›</span>
              <span className="">{selectedNode.name}</span>
            </>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {selectedNode.type === 'knowledge-source' && selectedNode.knowledgeSource
          ? renderKnowledgeSourceDetail(selectedNode.knowledgeSource)
          : selectedNode.type === 'document' && selectedNode.document
            ? renderDocumentDetail(selectedNode.document)
            : renderVisibilityGroupDetail(selectedNode)}
      </div>
    </div>
  );
};

export default KnowledgeDetailPanel;
