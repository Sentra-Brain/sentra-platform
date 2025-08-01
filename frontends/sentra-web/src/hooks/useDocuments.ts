// src/hooks/useDocuments.ts
// Simple state management for documents with request deduplication
import { useState, useCallback } from 'react';
import { knowledgeService } from '../services/knowledgeService';
import { notifyError } from '../lib/notify';
import { requestCache } from '../lib/requestCache';
import type { Document, DocumentUploadRequest } from '../models/knowledgeModels';

export const useDocuments = () => {
  const [documentsBySource, setDocumentsBySource] = useState<Record<string, Document[]>>({});

  const loadDocumentsForSource = useCallback(async (sourceId: string): Promise<Document[]> => {
    try {
      // Use request cache to prevent duplicate concurrent calls and infinite loops
      const response = await requestCache.get(
        `knowledge/sources/${sourceId}/documents`,
        () => knowledgeService.listDocuments(sourceId),
        { ttl: 2 * 60 * 1000 } // Cache for 2 minutes
      );
      
      const documents = response.documents;
      setDocumentsBySource(prev => ({ ...prev, [sourceId]: documents }));
      return documents;
    } catch (err) {
      notifyError(`Failed to load documents for source: ${err}`);
      return [];
    }
  }, []); // No dependencies to prevent re-creation and infinite loops

  const uploadDocument = useCallback(async (knowledgeSourceId: string, file: File, data: DocumentUploadRequest): Promise<Document> => {
    const newDocument = await knowledgeService.uploadDocument(knowledgeSourceId, file, data);
    
    // Add to the specified source's documents
    setDocumentsBySource(prev => ({
      ...prev,
      [knowledgeSourceId]: [
        ...(prev[knowledgeSourceId] || []),
        newDocument
      ]
    }));
    // Invalidate cache for this source
    requestCache.invalidate(`knowledge/sources/${knowledgeSourceId}/documents`);
    
    return newDocument;
  }, []);

  const removeDocument = useCallback(async (documentId: string): Promise<void> => {
    const removedDocument = await knowledgeService.removeDocument(documentId);
    
    // Remove from the source's documents
    if (removedDocument.knowledge_source_id) {
      setDocumentsBySource(prev => ({
        ...prev,
        [removedDocument.knowledge_source_id]: (prev[removedDocument.knowledge_source_id] || [])
          .filter(doc => doc.id !== documentId)
      }));
      // Invalidate cache for this source
      requestCache.invalidate(`knowledge/sources/${removedDocument.knowledge_source_id}/documents`);
    }
  }, []);

  const reindexDocument = useCallback(async (documentId: string): Promise<void> => {
    const reindexedDocument = await knowledgeService.reindexDocument(documentId);
    
    // Update the document in the cache
    if (reindexedDocument.knowledge_source_id) {
      setDocumentsBySource(prev => ({
        ...prev,
        [reindexedDocument.knowledge_source_id]: (prev[reindexedDocument.knowledge_source_id] || [])
          .map(doc => doc.id === documentId ? reindexedDocument : doc)
      }));
      // Invalidate cache for this source
      requestCache.invalidate(`knowledge/sources/${reindexedDocument.knowledge_source_id}/documents`);
    }
  }, []);

  const getDocumentsForSource = useCallback((sourceId: string): Document[] => {
    return documentsBySource[sourceId] || [];
  }, [documentsBySource]);

  const getDocumentById = useCallback((documentId: string): Document | undefined => {
    for (const documents of Object.values(documentsBySource)) {
      const doc = documents.find(d => d.id === documentId);
      if (doc) return doc;
    }
    return undefined;
  }, [documentsBySource]);

  const isLoadingSource = useCallback((_sourceId: string): boolean => {
    // We'll rely on the request cache for loading state - always return false for now
    // In the future, we could enhance the request cache to expose loading state
    return false;
  }, []);

  const refreshDocumentsForSource = useCallback(async (sourceId: string): Promise<void> => {
    // Invalidate cache first, then reload
    requestCache.invalidate(`knowledge/sources/${sourceId}/documents`);
    setDocumentsBySource(prev => {
      const updated = { ...prev };
      delete updated[sourceId];
      return updated;
    });
    await loadDocumentsForSource(sourceId);
  }, [loadDocumentsForSource]);

  return {
    documentsBySource,
    loadDocumentsForSource,
    uploadDocument,
    removeDocument,
    reindexDocument,
    getDocumentsForSource,
    getDocumentById,
    isLoadingSource,
    refreshDocumentsForSource,
  };
};