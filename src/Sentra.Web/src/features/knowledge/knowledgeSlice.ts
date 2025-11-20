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
  CreateKnowledgeSourceRequest,
  DocumentUploadRequest,
} from "./types/knowledgeModels";

interface KnowledgeState {
  visibility: KnowledgeSourceVisibility;

  sources: KnowledgeSource[];
  sourcesLoaded: boolean;
  sourcesLoading: boolean;

  documentsBySource: Record<string, KnowledgeDocument[]>;
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

  documentsBySource: {},
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
  async (sourceId: string) => {
    const res = await knowledgeService.listDocumentsBySource(sourceId);
    return { sourceId, documents: res.documents };
  }
);

export const createKnowledgeSource = createAsyncThunk(
  "knowledge/createSource",
  async (data: CreateKnowledgeSourceRequest) => {
    return knowledgeService.createSource(data);
  }
);

export const fetchSourcesWithDocuments = createAsyncThunk(
  "knowledge/fetchSourcesWithDocuments",
  async () => {
    const { sources } = await knowledgeService.listSources();
    const documentsBySource: Record<string, KnowledgeDocument[]> = {};

    for (const source of sources) {
      const { documents } = await knowledgeService.listDocumentsBySource(
        source.id
      );
      documentsBySource[source.id] = documents;
    }

    return { sources, documentsBySource };
  }
);

export const uploadDocumentToSource = createAsyncThunk(
  "knowledge/uploadDocument",
  async ({
    sourceId,
    file,
    payload,
  }: {
    sourceId: string;
    file: File;
    payload: DocumentUploadRequest;
  }) => {
    return knowledgeService.uploadDocument(sourceId, file, payload);
  }
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
      state.documentsBySource = {};
      state.documentsLoaded = false;
    },
    selectSource(state, action: PayloadAction<string | null>) {
      state.selectedSourceId = action.payload;
      state.selectedDocumentId = null;
    },
    selectDocument(state, action: PayloadAction<string | null>) {
      state.selectedDocumentId = action.payload;
    },
    clearSelection(state) {
      state.selectedSourceId = null;
      state.selectedDocumentId = null;
    },
    updateSourceMetadata(
      state,
      action: PayloadAction<{
        id: string;
        changes: Partial<
          Pick<KnowledgeSource, "name" | "description" | "auto_index">
        >;
      }>
    ) {
      const s = state.sources.find((src) => src.id === action.payload.id);
      if (s) Object.assign(s, action.payload.changes);
    },
    updateDocumentMetadata(
      state,
      action: PayloadAction<{
        id: string;
        changes: Partial<
          Pick<KnowledgeDocument, "display_name" | "description">
        >;
      }>
    ) {
      const sourceId = state.selectedSourceId;
      if (!sourceId) return;

      const docList = state.documentsBySource[sourceId];
      const doc = docList?.find((d) => d.id === action.payload.id);
      if (doc) Object.assign(doc, action.payload.changes);
    },
    markDocumentAsReindexing(state, action: PayloadAction<string>) {
      const sourceId = state.selectedSourceId;
      if (!sourceId) return;

      const docList = state.documentsBySource[sourceId];
      const doc = docList?.find((d) => d.id === action.payload);
      if (doc) {
        doc.status = "processing";
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
        state.documentsBySource[action.payload.sourceId] =
          action.payload.documents;
        state.documentsLoaded = true;
        state.documentsLoading = false;
      })
      .addCase(fetchDocumentsForSource.rejected, (state, action) => {
        state.documentsLoading = false;
        state.documentsLoaded = false;
        state.error = action.error.message;
      })
      .addCase(createKnowledgeSource.fulfilled, (state, action) => {
        state.sources.push(action.payload);
        state.sourcesLoaded = true;
      })
      .addCase(uploadDocumentToSource.fulfilled, (state, action) => {
        const sourceId = action.payload.knowledge_source_id;
        if (!state.documentsBySource[sourceId]) {
          state.documentsBySource[sourceId] = [];
        }
        state.documentsBySource[sourceId].push(action.payload);
      })
      .addCase(fetchSourcesWithDocuments.pending, (state) => {
        state.sourcesLoading = true;
        state.documentsLoading = true;
        state.error = undefined;
      })
      .addCase(fetchSourcesWithDocuments.fulfilled, (state, action) => {
        state.sources = action.payload.sources;
        state.sourcesLoaded = true;
        state.sourcesLoading = false;

        state.documentsBySource = action.payload.documentsBySource;
        state.documentsLoaded = true;
        state.documentsLoading = false;
      })
      .addCase(fetchSourcesWithDocuments.rejected, (state, action) => {
        state.sourcesLoading = false;
        state.documentsLoading = false;
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
  updateSourceMetadata,
  markDocumentAsReindexing,
} = knowledgeSlice.actions;

export default knowledgeSlice.reducer;
