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
    return httpClient.get('/knowledge-sources', {
      params: { limit, offset },
    });
  },

  createKnowledgeSource(data: CreateKnowledgeSourceRequest): Promise<KnowledgeSource> {
    return httpClient.post('/knowledge-sources', data);
  },

  // Documents
  listDocuments(
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
};