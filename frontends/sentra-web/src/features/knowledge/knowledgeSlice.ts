// 🧠 Redux Slice: knowledgeSlice.ts
import {
  createSlice,
  createAsyncThunk,
  type PayloadAction,
} from "@reduxjs/toolkit";
import { knowledgeService } from "./knowledgeService";
import type {
  KnowledgeSource,
  KnowledgeDocument,
  KnowledgeSourceVisibility,
} from "./types/knowledgeModels";

interface KnowledgeState {
  visibility: KnowledgeSourceVisibility;

  sources: KnowledgeSource[];
  sourcesLoaded: boolean;
  sourcesLoading: boolean;

  documents: KnowledgeDocument[];
  documentsLoaded: boolean;
  documentsLoading: boolean;

  selectedSourceId: string | null;
  selectedDocumentId: string | null;

  error?: string;
}

const initialState: KnowledgeState = {
  visibility: "private",

  sources: [],
  sourcesLoaded: false,
  sourcesLoading: false,

  documents: [],
  documentsLoaded: false,
  documentsLoading: false,

  selectedSourceId: null,
  selectedDocumentId: null,

  error: undefined,
};

// ───────────────────────────────────────────────────────
// Thunks
// ───────────────────────────────────────────────────────
export const fetchKnowledgeSources = createAsyncThunk(
  "knowledge/fetchSources",
  async () => knowledgeService.listSources()
);

export const fetchDocumentsForSource = createAsyncThunk(
  "knowledge/fetchDocumentsForSource",
  async (sourceId: string) => knowledgeService.listDocumentsBySource(sourceId)
);

// ───────────────────────────────────────────────────────
// Slice
// ───────────────────────────────────────────────────────
const knowledgeSlice = createSlice({
  name: "knowledge",
  initialState,
  reducers: {
    setVisibility(state, action: PayloadAction<KnowledgeSourceVisibility>) {
      state.visibility = action.payload;
      state.selectedSourceId = null;
      state.selectedDocumentId = null;
      state.sourcesLoaded = false;
      state.sources = [];
      state.documents = [];
      state.documentsLoaded = false;
    },
    selectSource(state, action: PayloadAction<string | null>) {
      state.selectedSourceId = action.payload;
      state.selectedDocumentId = null;
      state.documents = [];
      state.documentsLoaded = false;
    },
    selectDocument(state, action: PayloadAction<string | null>) {
      state.selectedDocumentId = action.payload;
    },
    clearSelection(state) {
      state.selectedSourceId = null;
      state.selectedDocumentId = null;
      state.documents = [];
      state.documentsLoaded = false;
    },
    updateDocumentMetadata(
      state,
      action: PayloadAction<{
        id: string;
        changes: Partial<Pick<KnowledgeDocument, "display_name" | "description">>;
      }>
    ) {
      const doc = state.documents.find((d) => d.id === action.payload.id);
      if (doc) Object.assign(doc, action.payload.changes);
    },
    markDocumentAsReindexing(
      state,
      action: PayloadAction<string> // documentId
    ) {
      const doc = state.documents.find((d) => d.id === action.payload);
      if (doc) {
        doc.status = "queued";
        doc.status_message = "Reindex requested";
        doc.error = undefined;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchKnowledgeSources.pending, (state) => {
        state.sourcesLoading = true;
        state.error = undefined;
      })
      .addCase(fetchKnowledgeSources.fulfilled, (state, action) => {
        state.sources = action.payload.sources;
        state.sourcesLoaded = true;
        state.sourcesLoading = false;
      })
      .addCase(fetchKnowledgeSources.rejected, (state, action) => {
        state.sourcesLoading = false;
        state.error = action.error.message;
      })
      .addCase(fetchDocumentsForSource.pending, (state) => {
        state.documentsLoading = true;
        state.documentsLoaded = false;
        state.error = undefined;
      })
      .addCase(fetchDocumentsForSource.fulfilled, (state, action) => {
        state.documents = action.payload.documents;
        state.documentsLoaded = true;
        state.documentsLoading = false;
      })
      .addCase(fetchDocumentsForSource.rejected, (state, action) => {
        state.documentsLoading = false;
        state.documentsLoaded = false;
        state.error = action.error.message;
      });
  },
});

export const {
  setVisibility,
  selectSource,
  selectDocument,
  clearSelection,
  updateDocumentMetadata,
  markDocumentAsReindexing,
} = knowledgeSlice.actions;

export default knowledgeSlice.reducer;
