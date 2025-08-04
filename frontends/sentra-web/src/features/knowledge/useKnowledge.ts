// features/knowledge/useKnowledge.ts
import { useAppDispatch, useAppSelector } from "@store/hooks";
import {
  fetchSourcesWithDocuments,
  fetchDocumentsForSource,
  setVisibility,
  selectSource,
  selectDocument,
  clearSelection,
  updateDocumentMetadata as updateDocMetadataAction,
  markDocumentAsReindexing,
  createKnowledgeSource,
  updateSourceMetadata,
  uploadDocumentToSource,
} from "./knowledgeSlice";
import type {
  CreateKnowledgeSourceRequest,
  DocumentUploadRequest,
} from "./types/knowledgeModels";
import { knowledgeService } from "./knowledgeService";
import type { KnowledgeDocument } from "./types/knowledgeModels";
import { useNavigate } from "react-router-dom";
import { useCallback } from "react";

export function useKnowledge() {
  const dispatch = useAppDispatch();
  const state = useAppSelector((s) => s.knowledge);
  const navigate = useNavigate();

  const loadSources = (force = false) => {
    if (force || (!state.sourcesLoaded && !state.sourcesLoading)) {
      dispatch(fetchSourcesWithDocuments());
    }
  };

  const loadDocuments = useCallback(
    (sourceId: string, force = false) => {
      if (
        !sourceId ||
        force ||
        (state.selectedSourceId === sourceId && state.documentsLoaded)
      ) {
        return;
      }
      dispatch(fetchDocumentsForSource(sourceId));
    },
    [dispatch, state.selectedSourceId, state.documentsLoaded]
  );

  const changeVisibility = (v: typeof state.visibility) =>
    dispatch(setVisibility(v));

  const selectSourceById = (id: string | null) => {
    dispatch(selectSource(id));
    dispatch(selectDocument(null)); // limpiar doc
    const visibility = state.visibility;
    if (id) {
      navigate(`/k/${visibility}/s/${id}`);
    } else {
      navigate(`/k/${visibility}`);
    }
  };

  const selectDocumentById = (id: string | null) => {
    dispatch(selectDocument(id));
    const visibility = state.visibility;
    const sourceId = state.selectedSourceId;
    if (id && sourceId) {
      navigate(`/k/${visibility}/s/${sourceId}/d/${id}`);
    }
  };

  const selectDocumentWithSource = (sourceId: string, documentId: string) => {
    dispatch(selectSource(sourceId));
    dispatch(selectDocument(documentId));
  };

  const resetSelection = () => dispatch(clearSelection());

  const updateDocumentMetadata = async (
    id: string,
    changes: Partial<Pick<KnowledgeDocument, "display_name" | "description">>
  ) => {
    await knowledgeService.updateDocumentMetadata(id, changes);
    dispatch(updateDocMetadataAction({ id, changes }));
  };

  const createNewSource = async (data: CreateKnowledgeSourceRequest) => {
    await dispatch(createKnowledgeSource(data));
  };

  const uploadToSource = async (
    sourceId: string,
    file: File,
    payload: DocumentUploadRequest
  ) => {
    await dispatch(uploadDocumentToSource({ sourceId, file, payload }));
  };

  const reindexDocument = async (id: string) => {
    await knowledgeService.reindexDocument(id); // POST to /reindex
    dispatch(markDocumentAsReindexing(id));
  };

  return {
    ...state,
    loadSources,
    loadDocuments,
    changeVisibility,
    selectSourceById,
    selectDocumentById,
    selectDocumentWithSource,
    resetSelection,
    updateDocumentMetadata,
    createNewSource,
    uploadToSource,
    updateSourceMetadata,
    reindexDocument,
  };
}
