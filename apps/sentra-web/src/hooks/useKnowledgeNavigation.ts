// src/hooks/useKnowledgeNavigation.ts
// Hook for URL-based knowledge navigation
import { useParams, useNavigate } from 'react-router-dom';
import type { KnowledgeTreeNode } from '../models/knowledgeModels';

export const useKnowledgeNavigation = () => {
  const params = useParams<{
    sourceId?: string;
    documentId?: string;
  }>();
  const navigate = useNavigate();

  const navigateToKnowledgeSource = (sourceId: string) => {
    navigate(`/knowledge/source/${sourceId}`);
  };

  const navigateToDocument = (documentId: string, sourceId?: string) => {
    if (sourceId) {
      navigate(`/knowledge/source/${sourceId}/document/${documentId}`);
    } else {
      navigate(`/knowledge/document/${documentId}`);
    }
  };

  const navigateToKnowledge = () => {
    navigate('/knowledge');
  };

  const getSelectedNodeFromUrl = (
    knowledgeSources: any[],
    documents: any[]
  ): KnowledgeTreeNode | undefined => {
    const { sourceId, documentId } = params;

    if (documentId) {
      // Find document by ID
      const document = documents.find(doc => doc.id === documentId);
      if (document) {
        return {
          id: document.id,
          name: document.display_name,
          type: 'document',
          document,
        };
      }
    }

    if (sourceId) {
      // Find knowledge source by ID
      const source = knowledgeSources.find(ks => ks.id === sourceId);
      if (source) {
        return {
          id: source.id,
          name: source.name,
          type: 'knowledge-source',
          knowledgeSource: source,
        };
      }
    }

    return undefined;
  };

  return {
    params,
    navigateToKnowledgeSource,
    navigateToDocument,
    navigateToKnowledge,
    getSelectedNodeFromUrl,
  };
};