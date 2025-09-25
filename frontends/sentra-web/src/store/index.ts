// src/store/index.ts
import { configureStore } from '@reduxjs/toolkit'

import authReducer from '../features/auth/authSlice'
import eventsReducer from '../features/chat/eventsSlice'
import agentsReducer from '../features/agents/agentsSlice'
import conversationReducer from '../features/conversations/conversationsSlice'
import knowledgeReducer from '../features/knowledge/knowledgeSlice'
// import settingsReducer from '../features/settings/settingsSlice'
import uiReducer from './slices/uiSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
      events: eventsReducer,
    conversation: conversationReducer,
    agents: agentsReducer,
    knowledge: knowledgeReducer,
    // settings: settingsReducer,
    ui: uiReducer
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
