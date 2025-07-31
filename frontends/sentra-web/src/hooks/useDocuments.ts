// src/hooks/useDocuments.ts
// Simple state management for documents
import { useState, useCallback } from 'react';
import { knowledgeService } from '../services/knowledgeService';
import { notifyError } from '../lib/notify';
import type { Document, DocumentUploadRequest } from '../models/knowledgeModels';

export const useDocuments = () => {
  const [documentsBySource, setDocumentsBySource] = useState<Record<string, Document[]>>({});
  const [loadingDocuments, setLoadingDocuments] = useState<Record<string, boolean>>({});

  const loadDocumentsForSource = useCallback(async (sourceId: string): Promise<Document[]> => {
    // Return cached documents if already loaded and not currently loading
    if (documentsBySource[sourceId] && !loadingDocuments[sourceId]) {
      return documentsBySource[sourceId];
    }

    setLoadingDocuments(prev => ({ ...prev, [sourceId]: true }));
    try {
      const response = await knowledgeService.listDocuments(sourceId);
      const documents = response.documents;
      setDocumentsBySource(prev => ({ ...prev, [sourceId]: documents }));
      return documents;
    } catch (err) {
      notifyError(`Failed to load documents for source: ${err}`);
      return [];
    } finally {
      setLoadingDocuments(prev => ({ ...prev, [sourceId]: false }));
    }
  }, [documentsBySource, loadingDocuments]);

  const uploadDocument = useCallback(async (file: File, data: DocumentUploadRequest): Promise<Document> => {
    const newDocument = await knowledgeService.uploadDocument(file, data);
    
    // Add to the upload source's documents (the API automatically determines the upload source)
    if (newDocument.knowledge_source_id) {
      setDocumentsBySource(prev => ({
        ...prev,
        [newDocument.knowledge_source_id]: [
          ...(prev[newDocument.knowledge_source_id] || []),
          newDocument
        ]
      }));
    }
    
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

  const isLoadingSource = useCallback((sourceId: string): boolean => {
    return loadingDocuments[sourceId] || false;
  }, [loadingDocuments]);

  const refreshDocumentsForSource = useCallback(async (sourceId: string): Promise<void> => {
    // Force refresh by removing from cache first
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