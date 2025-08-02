// src/store/slices/chatSlice.ts
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

type ChatState = {
  waitingForAnswer: boolean;
  isStreaming: boolean; // linked to streaming state
  inputDisabled: boolean;
};

const initialState: ChatState = {
  waitingForAnswer: false,
  isStreaming: false, // linked to streaming state
  inputDisabled: false, // optionally linked
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
    },
  },
});

export const {
  setWaitingForAnswer,
  setStreaming,
  setInputDisabled,
  resetChatState,
} = chatSlice.actions
export default chatSlice.reducer;
