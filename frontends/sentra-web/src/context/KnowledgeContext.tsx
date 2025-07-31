import React, { useState, useEffect, useCallback } from 'react';
import { knowledgeService } from '../services/knowledgeService';
import { useKnowledgeNavigation } from '../hooks/useKnowledgeNavigation';
import type {
  KnowledgeSource,
  Document,
  KnowledgeTreeNode,
} from '../models/knowledgeModels';
import { KnowledgeSourceVisibility as KSVisibility } from '../models/knowledgeModels';
import { KnowledgeContext } from './KnowledgeContextInstance';
import { notifyError } from '../lib/notify';

export type KnowledgeContextType = {
  // Data
  knowledgeSources: KnowledgeSource[];
  documentsBySourceId: Record<string, Document[]>;
  treeNodes: KnowledgeTreeNode[];
  
  // Selected state
  selectedNode: KnowledgeTreeNode | undefined;
  
  // Expanded nodes state
  expandedNodes: Set<string>;
  
  // Loading & error states
  loading: boolean;
  error: string | null;
  
  // Dialog states
  showUploadDialog: boolean;
  showCreateSourceDialog: boolean;
  
  // Actions
  loadData: () => Promise<void>;
  selectNode: (node: KnowledgeTreeNode) => void;
  navigateToKnowledgeSource: (sourceId: string) => void;
  navigateToDocument: (documentId: string, sourceId?: string) => void;
  toggleExpanded: (nodeId: string) => void;
  setShowUploadDialog: (show: boolean) => void;
  setShowCreateSourceDialog: (show: boolean) => void;
  refresh: () => Promise<void>;
  
  // Upload dialog helpers
  getUserUploadSource: () => KnowledgeSource | undefined;
  loadDocumentsForSource: (sourceId: string) => Promise<void>;
  getDocumentsForSource: (sourceId: string) => Document[] | undefined;
};

export const KnowledgeProvider = ({ children }: { children: React.ReactNode }) => {
  const [knowledgeSources, setKnowledgeSources] = useState<KnowledgeSource[]>([]);
  const [documentsBySourceId, setDocumentsBySourceId] = useState<Record<string, Document[]>>({});
  const [loadingSources, setLoadingSources] = useState<Set<string>>(new Set());
  const [selectedNode, setSelectedNode] = useState<KnowledgeTreeNode | undefined>();
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [showCreateSourceDialog, setShowCreateSourceDialog] = useState(false);

  const { 
    navigateToKnowledgeSource, 
    navigateToDocument, 
    getSelectedNodeFromUrl 
  } = useKnowledgeNavigation();

  const loadDocumentsForSource = useCallback(async (sourceId: string) => {
    if (loadingSources.has(sourceId)) return;

    setLoadingSources((prev) => new Set(prev).add(sourceId));
    try {
      const documents = await knowledgeService.listDocuments(sourceId);
      if (Array.isArray(documents)) {
        setDocumentsBySourceId((prev) => ({ ...prev, [sourceId]: documents }));
      } else {
        console.error(`Unexpected response format for documents:`, documents);
      }
    } catch (err) {
      console.error(`Failed to load documents for source ${sourceId}:`, err);
      notifyError(err);
    } finally {
      setLoadingSources((prev) => {
        const newSet = new Set(prev);
        newSet.delete(sourceId);
        return newSet;
      });
    }
  }, [loadingSources]);

  const getDocumentsForSource = (sourceId: string): Document[] | undefined => {
    return documentsBySourceId[sourceId];
  };

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const sourcesResponse = await knowledgeService.listKnowledgeSources();
      setKnowledgeSources(sourcesResponse.sources);
    } catch (err) {
      setError('Failed to load knowledge data');
      console.error('Error loading knowledge data:', err);
      notifyError(err);
    } finally {
      setLoading(false);
    }
  };

  const refresh = async () => {
    await loadData();
  };

  const selectNode = (node: KnowledgeTreeNode) => {
    if (node.type === 'knowledge-source') {
      if (!documentsBySourceId[node.id]) {
        loadDocumentsForSource(node.id);
      }
      navigateToKnowledgeSource(node.id);
    } else if (node.type === 'document' && node.document) {
      navigateToDocument(node.document.id, node.document.knowledge_source_id);
    }

    setSelectedNode(node);
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

  const getUserUploadSource = (): KnowledgeSource | undefined => {
    // Find the user's personal upload source (typically a private upload-type source)
    return knowledgeSources.find(source => 
      source.visibility === KSVisibility.PRIVATE && 
      source.type === 'upload'
    );
  };

  const buildTreeNodes = (): KnowledgeTreeNode[] => {
    const visibilityGroups: Record<string, KnowledgeTreeNode> = {
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

    knowledgeSources.forEach((source) => {
      const sourceDocuments = documentsBySourceId[source.id] || [];

      const sourceNode: KnowledgeTreeNode = {
        id: source.id,
        name: source.name,
        type: 'knowledge-source',
        knowledgeSource: source,
        documentCount: sourceDocuments.length,
        expanded: expandedNodes.has(source.id),
        children: expandedNodes.has(source.id)
          ? sourceDocuments.map((doc) => ({
              id: doc.id,
              name: doc.display_name,
              type: 'document',
              document: doc,
            }))
          : [],
      };

      visibilityGroups[source.visibility].children!.push(sourceNode);
    });

    return Object.values(visibilityGroups);
  };

  const treeNodes = React.useMemo(buildTreeNodes, [knowledgeSources, documentsBySourceId, expandedNodes]);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (knowledgeSources.length > 0) {
      const allDocuments: Document[] = Object.values(documentsBySourceId).flat();
      const nodeFromUrl = getSelectedNodeFromUrl(knowledgeSources, allDocuments);
      setSelectedNode(nodeFromUrl);
    }
  }, [knowledgeSources, documentsBySourceId, getSelectedNodeFromUrl]);

  return (
    <KnowledgeContext.Provider
      value={{
        knowledgeSources,
        documentsBySourceId,
        treeNodes,
        selectedNode,
        expandedNodes,
        loading,
        error,
        showUploadDialog,
        showCreateSourceDialog,
        loadData,
        selectNode,
        navigateToKnowledgeSource,
        navigateToDocument,
        toggleExpanded,
        setShowUploadDialog,
        setShowCreateSourceDialog,
        refresh,
        getUserUploadSource,
        loadDocumentsForSource,
        getDocumentsForSource,
      }}
    >
      {children}
    </KnowledgeContext.Provider>
  );
};