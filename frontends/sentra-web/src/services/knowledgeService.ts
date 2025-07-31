// src/services/knowledgeService.ts
// Knowledge Management API service
import { httpClient } from '../lib/httpClient';
import type {
  KnowledgeSource,
  KnowledgeSourceListResponse,
  CreateKnowledgeSourceRequest,
  Document,
  DocumentListResponse,
  DocumentUploadRequest,
} from '../models/knowledgeModels';

export const knowledgeService = {
  // Knowledge Sources
  listKnowledgeSources(limit = 100, offset = 0): Promise<KnowledgeSourceListResponse> {
    return httpClient.get('/knowledge/sources', {
      params: { limit, offset },
    });
  },

  createKnowledgeSource(data: CreateKnowledgeSourceRequest): Promise<KnowledgeSource> {
    return httpClient.post('/knowledge/sources', data);
  },

  // Documents
  listDocuments(
    knowledgeSourceId: string,
    limit = 100,
    offset = 0
  ): Promise<DocumentListResponse> {
    const params: Record<string, unknown> = { limit, offset };
    return httpClient.get(
      `/knowledge/sources/${knowledgeSourceId}/documents`,
      { params }
    );
  },

  // List all documents across sources
  listAllDocuments(
    knowledgeSourceId?: string,
    limit = 100,
    offset = 0
  ): Promise<DocumentListResponse> {
    const params: Record<string, unknown> = { limit, offset };
    if (knowledgeSourceId) {
      params.knowledge_source_id = knowledgeSourceId;
    }
    return httpClient.get('/documents', { params });
  },

  uploadDocument(
    file: File,
    data: DocumentUploadRequest
  ): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('display_name', data.display_name);
    if (data.description) {
      formData.append('description', data.description);
    }

    return httpClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Enable/Disable knowledge source
  updateKnowledgeSourceStatus(knowledgeSourceId: string, enabled: boolean): Promise<KnowledgeSource> {
    return httpClient.put(`/knowledge/sources/${knowledgeSourceId}/status`, null, {
      params: { enabled },
    });
  },

  // Re-index document  
  reindexDocument(documentId: string): Promise<Document> {
    return httpClient.post(`/documents/${documentId}/reindex`);
  },

  // Remove document (mark for removal)
  removeDocument(documentId: string): Promise<Document> {
    return httpClient.del(`/documents/${documentId}`);
  },
};