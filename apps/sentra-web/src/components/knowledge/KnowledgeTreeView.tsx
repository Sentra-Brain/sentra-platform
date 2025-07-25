// src/components/knowledge/KnowledgeTreeView.tsx
// Tree-based knowledge explorer component
import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronDown, RefreshCw, Folder, File, Upload, Plus } from 'lucide-react';
import type {
  KnowledgeSource,
  Document,
  KnowledgeSourceVisibility,
  KnowledgeTreeNode,
} from '../../models/knowledgeModels';
import { KnowledgeSourceVisibility as KSVisibility } from '../../models/knowledgeModels';
import { knowledgeService } from '../../services/knowledgeService';
import StatusBadge from './StatusBadge';
import UploadDialog from './UploadDialog';
import CreateKnowledgeSourceDialog from './CreateKnowledgeSourceDialog';

interface KnowledgeTreeViewProps {
  onSelectNode: (node: KnowledgeTreeNode) => void;
  selectedNodeId?: string;
}

const KnowledgeTreeView: React.FC<KnowledgeTreeViewProps> = ({
  onSelectNode,
  selectedNodeId,
}) => {
  const [knowledgeSources, setKnowledgeSources] = useState<KnowledgeSource[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [showCreateSourceDialog, setShowCreateSourceDialog] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sourcesResponse, documentsResponse] = await Promise.all([
        knowledgeService.listKnowledgeSources(),
        knowledgeService.listDocuments(),
      ]);
      setKnowledgeSources(sourcesResponse.sources);
      setDocuments(documentsResponse.documents);
    } catch (err) {
      setError('Failed to load knowledge data');
      console.error('Error loading knowledge data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const buildTreeNodes = (): KnowledgeTreeNode[] => {
    const visibilityGroups: Record<KnowledgeSourceVisibility, KnowledgeTreeNode> = {
      [KSVisibility.PRIVATE]: {
        id: 'private',
        name: 'Private',
        type: 'visibility-group',
        visibility: KSVisibility.PRIVATE,
        children: [],
        expanded: expandedNodes.has('private'),
      },
      [KSVisibility.SHARED]: {
        id: 'shared',
        name: 'Shared',
        type: 'visibility-group',
        visibility: KSVisibility.SHARED,
        children: [],
        expanded: expandedNodes.has('shared'),
      },
      [KSVisibility.ORG_WIDE]: {
        id: 'org-wide',
        name: 'Organization-Wide',
        type: 'visibility-group',
        visibility: KSVisibility.ORG_WIDE,
        children: [],
        expanded: expandedNodes.has('org-wide'),
      },
    };

    // Group sources by visibility
    knowledgeSources.forEach((source) => {
      const sourceDocuments = documents.filter(
        (doc) => doc.knowledge_source_id === source.id
      );

      const sourceNode: KnowledgeTreeNode = {
        id: source.id,
        name: source.name,
        type: 'knowledge-source',
        knowledgeSource: source,
        documentCount: sourceDocuments.length,
        expanded: expandedNodes.has(source.id),
        children: sourceDocuments.map((doc) => ({
          id: doc.id,
          name: doc.display_name,
          type: 'document',
          document: doc,
        })),
      };

      visibilityGroups[source.visibility].children!.push(sourceNode);
    });

    return Object.values(visibilityGroups);
  };

  const toggleExpanded = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  const handleNodeClick = (node: KnowledgeTreeNode) => {
    if (node.type === 'visibility-group' || node.type === 'knowledge-source') {
      toggleExpanded(node.id);
    }
    onSelectNode(node);
  };

  const renderTreeNode = (node: KnowledgeTreeNode, level = 0): React.ReactNode => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = node.expanded;
    const isSelected = selectedNodeId === node.id;

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
          <div className="flex items-center gap-2">
            <StatusBadge status={node.knowledgeSource.status} />
            {node.documentCount !== undefined && (
              <span className="text-xs text-gray-500">
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
          className={`flex items-center gap-2 p-2 cursor-pointer hover:bg-gray-800 ${
            isSelected ? 'border-l-4 border-blue-400' : ''
          }`}
          style={{ paddingLeft: `${level * 20 + 8}px` }}
          onClick={() => handleNodeClick(node)}
        >
          <div className="flex items-center gap-2 flex-1 min-w-0">
            {getNodeIcon()}
            <span className="truncate font-medium">{node.name}</span>
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
    loadData(); // Refresh the tree to show new uploads
  };

  const handleCreateSourceComplete = () => {
    loadData(); // Refresh the tree to show new knowledge source
  };

  const getUserUploadSource = (): KnowledgeSource | undefined => {
    // Find the user's personal upload source (typically a private upload-type source)
    return knowledgeSources.find(source => 
      source.visibility === KSVisibility.PRIVATE && 
      source.type === 'upload'
    );
  };

  if (loading) {
    return (
      <div className="p-4 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
        <p className="text-gray-500 mt-2">Loading knowledge sources...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-center">
        <p className="text-red-600 mb-2">{error}</p>
        <button
          onClick={loadData}
          className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    );
  }

  const treeNodes = buildTreeNodes();

  return (
    <div className="h-full flex flex-col">
      <div className="p-3 border-b space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">Knowledge Explorer</h2>
          <button
            onClick={loadData}
            className="p-1 hover:bg-gray-100 rounded"
            title="Refresh"
          >
            <RefreshCw size={16} />
          </button>
        </div>
        
        {/* Upload Actions */}
        <div className="flex gap-2">
          <button
            onClick={() => setShowUploadDialog(true)}
            className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm flex-1"
            title="Upload documents to an existing knowledge source"
          >
            <Upload size={16} />
            Upload Documents
          </button>
          <button
            onClick={() => setShowCreateSourceDialog(true)}
            className="flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
            title="Create a new knowledge source from folder upload"
          >
            <Plus size={16} />
          </button>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto">
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