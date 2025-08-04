// features/knowledge/useKnowledge.ts
import { useAppDispatch, useAppSelector } from "@store/hooks";
import {
  fetchKnowledgeSources,
  fetchDocumentsForSource,
  setVisibility,
  selectSource,
  selectDocument,
  clearSelection,
  updateDocumentMetadata as updateDocMetadataAction,
  markDocumentAsReindexing,
} from "./knowledgeSlice";
import { knowledgeService } from "./knowledgeService";
import type { KnowledgeDocument } from "./types/knowledgeModels";
import { useNavigate } from "react-router-dom";

export function useKnowledge() {
  const dispatch = useAppDispatch();
  const state = useAppSelector((s) => s.knowledge);
  const navigate = useNavigate();

  const loadSources = (force = false) => {
    if (force || (!state.sourcesLoaded && !state.sourcesLoading)) {
      dispatch(fetchKnowledgeSources());
    }
  };

  const loadDocuments = (sourceId: string, force = false) => {
    if (
      !sourceId ||
      state.selectedSourceId !== sourceId ||
      force ||
      (!state.documentsLoaded && !state.documentsLoading)
    ) {
      dispatch(fetchDocumentsForSource(sourceId));
    }
  };

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

  const resetSelection = () => dispatch(clearSelection());

  const updateDocumentMetadata = async (
    id: string,
    changes: Partial<Pick<KnowledgeDocument, "display_name" | "description">>
  ) => {
    await knowledgeService.updateDocumentMetadata(id, changes);
    dispatch(updateDocMetadataAction({ id, changes }));
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
    resetSelection,
    updateDocumentMetadata,
    reindexDocument,
  };
}
