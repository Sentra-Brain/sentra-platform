// ✅ 1. New chatSlice.ts — add message support
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { ChatMessage } from "@features/conversations/types/conversationModels";
import type { ConversationMode } from "@features/chat/types/mode";

export interface SelectedContext {
  sourceIds: string[];
  documentIds: string[];
  useRag: boolean;
}

interface ChatState {
  waitingForAnswer: boolean;
  isStreaming: boolean;
  inputDisabled: boolean;
  messages: ChatMessage[];
  selectedContext: SelectedContext;
  mode: ConversationMode;
}
const storedMode = (typeof window !== "undefined"
  ? (localStorage.getItem("sentra.chat.mode") as ConversationMode | null)
  : null) || "fast";

const initialState: ChatState = {
  waitingForAnswer: false,
  isStreaming: false,
  inputDisabled: false,
  messages: [],
  selectedContext: {
    sourceIds: [],
    documentIds: [],
    useRag: true,
  },
  mode: storedMode,
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    setWaitingForAnswer(state, action: PayloadAction<boolean>) {
      state.waitingForAnswer = action.payload;
    },
    setStreaming(state, action: PayloadAction<boolean>) {
      state.isStreaming = action.payload;
    },
    setInputDisabled(state, action: PayloadAction<boolean>) {
      state.inputDisabled = action.payload;
    },
    resetChatState(state) {
      state.waitingForAnswer = false;
      state.inputDisabled = false;
      state.isStreaming = false;
      state.messages = [];
      state.selectedContext = {
        sourceIds: [],
        documentIds: [],
        useRag: true,
      };
    },
    setMessages(state, action: PayloadAction<ChatMessage[]>) {
      state.messages = action.payload;
    },
    addMessage(state, action: PayloadAction<ChatMessage>) {
      state.messages.push(action.payload);
    },
    updateLastAssistantMessage(state, action: PayloadAction<string>) {
      for (let i = state.messages.length - 1; i >= 0; i--) {
        if (state.messages[i].role === "assistant") {
          state.messages[i].content += action.payload;
          break;
        }
      }
    },
    setSelectedContext(state, action: PayloadAction<SelectedContext>) {
      state.selectedContext = action.payload;
    },
    updateUseRag(state, action: PayloadAction<boolean>) {
      state.selectedContext.useRag = action.payload;
    },
    addContextSource(state, action: PayloadAction<string>) {
      if (!state.selectedContext.sourceIds.includes(action.payload)) {
        state.selectedContext.sourceIds.push(action.payload);
      }
    },
    removeContextSource(state, action: PayloadAction<string>) {
      state.selectedContext.sourceIds = state.selectedContext.sourceIds.filter(
        id => id !== action.payload
      );
    },
    addContextDocument(state, action: PayloadAction<string>) {
      if (!state.selectedContext.documentIds.includes(action.payload)) {
        state.selectedContext.documentIds.push(action.payload);
      }
    },
    removeContextDocument(state, action: PayloadAction<string>) {
      state.selectedContext.documentIds = state.selectedContext.documentIds.filter(
        id => id !== action.payload
      );
    },
    clearSelectedContext(state) {
      state.selectedContext = {
        sourceIds: [],
        documentIds: [],
        useRag: true,
      };
    },
    setMode(state, action: PayloadAction<ConversationMode>) {
      state.mode = action.payload;
      try { localStorage.setItem("sentra.chat.mode", action.payload); } catch {
        // Handle error
        console.error("Failed to save chat mode to localStorage");
      }
    },
  },
});

export const {
  setWaitingForAnswer,
  setStreaming,
  setInputDisabled,
  resetChatState,
  setMessages,
  addMessage,
  updateLastAssistantMessage,
  setSelectedContext,
  updateUseRag,
  addContextSource,
  removeContextSource,
  addContextDocument,
  removeContextDocument,
  clearSelectedContext,
  setMode, 
} = chatSlice.actions;

export default chatSlice.reducer;
