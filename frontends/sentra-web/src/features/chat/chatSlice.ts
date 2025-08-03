// ✅ 1. New chatSlice.ts — add message support
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { ChatMessage } from "@features/conversations/types/conversationModels";

interface ChatState {
  waitingForAnswer: boolean;
  isStreaming: boolean;
  inputDisabled: boolean;
  messages: ChatMessage[];
}

const initialState: ChatState = {
  waitingForAnswer: false,
  isStreaming: false,
  inputDisabled: false,
  messages: [],
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
} = chatSlice.actions;

export default chatSlice.reducer;
