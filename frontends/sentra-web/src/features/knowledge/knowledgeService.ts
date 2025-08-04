import apiClient from "@shared/api/apiClient";
import type {
  KnowledgeSource,
  KnowledgeSourceListResponse,
  CreateKnowledgeSourceRequest,
  KnowledgeDocument,
  DocumentListResponse,
  DocumentUploadRequest,
} from "./types/knowledgeModels";

export const knowledgeService = {
  // ─────────────────────────────────────────────
  // Knowledge Sources
  // ─────────────────────────────────────────────
  listSources(): Promise<KnowledgeSourceListResponse> {
    return apiClient.get("/knowledge/sources").then((res) => res.data);
  },

  getSource(id: string): Promise<KnowledgeSource> {
    return apiClient.get(`/knowledge/sources/${id}`).then((res) => res.data);
  },

  createSource(data: CreateKnowledgeSourceRequest): Promise<KnowledgeSource> {
    return apiClient.post("/knowledge/sources", data).then((res) => res.data);
  },

  updateSourceStatus(id: string, enabled: boolean): Promise<KnowledgeSource> {
    return apiClient
      .patch(`/knowledge/sources/${id}`, null, {
        params: { enabled },
      })
      .then((res) => res.data);
  },

  updateSourceMetadata(
    id: string,
    data: Partial<Pick<KnowledgeSource, "name" | "description" | "auto_index">>
  ) {
    return apiClient
      .patch(`/knowledge/sources/${id}`, data)
      .then((res) => res.data);
  },

  deleteSource(id: string): Promise<KnowledgeSource> {
    return apiClient.delete(`/knowledge/sources/${id}`).then((res) => res.data);
  },

  // ─────────────────────────────────────────────
  // Documents
  // ─────────────────────────────────────────────
  listDocumentsBySource(sourceId: string): Promise<DocumentListResponse> {
    return apiClient
      .get(`/knowledge/sources/${sourceId}/documents`)
      .then((res) => res.data);
  },

  listAllDocuments(
    knowledgeSourceId?: string,
    limit = 100,
    offset = 0
  ): Promise<DocumentListResponse> {
    const params: Record<string, unknown> = { limit, offset };
    if (knowledgeSourceId) {
      params.knowledge_source_id = knowledgeSourceId;
    }
    return apiClient
      .get("/knowledge/documents", { params })
      .then((res) => res.data);
  },

  getDocument(id: string): Promise<KnowledgeDocument> {
    return apiClient.get(`/knowledge/documents/${id}`).then((res) => res.data);
  },

  uploadDocument(
    sourceId: string,
    file: File,
    data: DocumentUploadRequest
  ): Promise<KnowledgeDocument> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("display_name", data.display_name);
    if (data.description) {
      formData.append("description", data.description);
    }

    return apiClient
      .post(`/knowledge/sources/${sourceId}/documents`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((res) => res.data);
  },

  updateDocumentMetadata(
    documentId: string,
    data: Partial<Pick<DocumentUploadRequest, "display_name" | "description">>
  ): Promise<KnowledgeDocument> {
    return apiClient
      .patch(`/knowledge/documents/${documentId}`, null, {
        params: data,
      })
      .then((res) => res.data);
  },

  reindexDocument(documentId: string): Promise<KnowledgeDocument> {
    return apiClient
      .post(`/knowledge/documents/${documentId}/reindex`)
      .then((res) => res.data);
  },

  removeDocument(documentId: string): Promise<KnowledgeDocument> {
    return apiClient
      .delete(`/knowledge/documents/${documentId}`)
      .then((res) => res.data);
  },
};
