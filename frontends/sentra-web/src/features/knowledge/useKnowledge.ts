// features/knowledge/useKnowledge.ts
import { useAppDispatch, useAppSelector } from '@store/hooks';
import {
  fetchKnowledgeSources,
  fetchDocumentsForSource,
  setVisibility,
  selectSource,
  selectDocument,
  clearSelection,
} from './knowledgeSlice';

export function useKnowledge() {
  const dispatch = useAppDispatch();
  const state = useAppSelector((s) => s.knowledge);

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

  const selectSourceById = (id: string | null) =>
    dispatch(selectSource(id));

  const selectDocumentById = (id: string | null) =>
    dispatch(selectDocument(id));

  const resetSelection = () => dispatch(clearSelection());

  return {
    ...state,
    loadSources,
    loadDocuments,
    changeVisibility,
    selectSourceById,
    selectDocumentById,
    resetSelection,
  };
}
