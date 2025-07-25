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
    data: DocumentUploadRequest,
    knowledgeSourceId?: string
  ): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('display_name', data.display_name);
    if (data.description) {
      formData.append('description', data.description);
    }
    if (knowledgeSourceId) {
      formData.append('knowledge_source_id', knowledgeSourceId);
    }

    return httpClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Upload multiple documents to a specific knowledge source
  uploadMultipleDocuments(
    files: File[],
    knowledgeSourceId?: string
  ): Promise<Document[]> {
    const uploadPromises = files.map(file => {
      const data: DocumentUploadRequest = {
        display_name: file.name.replace(/\.[^/.]+$/, ''), // Remove file extension
      };
      return this.uploadDocument(file, data, knowledgeSourceId);
    });
    
    return Promise.all(uploadPromises);
  },

  // Create knowledge source from folder upload
  uploadFolderAsKnowledgeSource(
    files: File[],
    sourceData: CreateKnowledgeSourceRequest
  ): Promise<{
    knowledgeSource: KnowledgeSource;
    documents: Document[];
    progress: (uploaded: number, total: number) => void;
  }> {
    // First create the knowledge source
    return this.createKnowledgeSource(sourceData).then(async (knowledgeSource) => {
      const documents: Document[] = [];

      // Upload files one by one to show progress
      for (const file of files) {
        try {
          const data: DocumentUploadRequest = {
            display_name: file.name.replace(/\.[^/.]+$/, ''),
          };
          const document = await this.uploadDocument(file, data, knowledgeSource.id);
          documents.push(document);
        } catch (error) {
          console.error(`Failed to upload ${file.name}:`, error);
          // Continue with other files
        }
      }

      return {
        knowledgeSource,
        documents,
        progress: () => {
          // This is a placeholder - in a real implementation, 
          // we'd use a callback mechanism for progress updates
        }
      };
    });
  },
};