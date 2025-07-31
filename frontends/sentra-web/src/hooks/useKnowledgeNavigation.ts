// src/hooks/useKnowledgeNavigation.ts
// Simple navigation for knowledge sources and documents
import { useCallback } from 'react';
import { useNavigate, useLocation, useParams } from 'react-router-dom';

export const useKnowledgeNavigation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const params = useParams();

  const navigateToKnowledgeSource = useCallback((sourceId: string) => {
    navigate(`/knowledge/sources/${sourceId}`);
  }, [navigate]);

  const navigateToDocument = useCallback((documentId: string, _sourceId?: string) => {
    navigate(`/knowledge/documents/${documentId}`);
  }, [navigate]);

  const navigateToKnowledgeHome = useCallback(() => {
    navigate('/knowledge');
  }, [navigate]);

  const getCurrentSourceId = useCallback((): string | undefined => {
    return params.sourceId;
  }, [params]);

  const getCurrentDocumentId = useCallback((): string | undefined => {
    return params.documentId;
  }, [params]);

  const isOnKnowledgePage = useCallback((): boolean => {
    return location.pathname.startsWith('/knowledge');
  }, [location]);

  const isOnSourcePage = useCallback((): boolean => {
    return location.pathname.includes('/knowledge/sources/');
  }, [location]);

  const isOnDocumentPage = useCallback((): boolean => {
    return location.pathname.includes('/knowledge/documents/');
  }, [location]);

  return {
    navigateToKnowledgeSource,
    navigateToDocument,
    navigateToKnowledgeHome,
    getCurrentSourceId,
    getCurrentDocumentId,
    isOnKnowledgePage,
    isOnSourcePage,
    isOnDocumentPage,
  };
};