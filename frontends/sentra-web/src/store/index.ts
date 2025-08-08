// src/store/index.ts
import { configureStore } from '@reduxjs/toolkit'

import authReducer from '../features/auth/authSlice'
import chatReducer from '../features/chat/chatSlice'
import stepsReducer from '../features/chat/stepsSlice'
import conversationReducer from '../features/conversations/conversationSlice'
import knowledgeReducer from '../features/knowledge/knowledgeSlice'
// import settingsReducer from '../features/settings/settingsSlice'
import uiReducer from './slices/uiSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    chat: chatReducer,
    steps: stepsReducer,
    conversation: conversationReducer,
    knowledge: knowledgeReducer,
    // settings: settingsReducer,
    ui: uiReducer
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
