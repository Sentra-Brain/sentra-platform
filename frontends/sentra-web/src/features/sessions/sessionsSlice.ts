// src/features/sessions/sessionSlice.ts

import {
  createSlice,
  createAsyncThunk,
  type PayloadAction,
} from '@reduxjs/toolkit'
import { sessionService } from './sessionService'
import type {
  SessionDetails,
  SessionListItem,
  CreateSessionRequest,
} from './types/sessionModels'

interface SessionsState {
  sessions: SessionListItem[]
  currentSessionId: string | null
  
  selectedSessionDetails: SessionDetails | null
  loadingList: boolean // for session list  
  loadingSession: boolean // for chat page
  error: string | null
}

const initialState: SessionsState = {
  sessions: [],
  currentSessionId: null,
  selectedSessionDetails: null,
  loadingList: false,
  loadingSession: false, // for chat page
  error: null,
}

// 🔄 Fetch all sessions
export const fetchSessions = createAsyncThunk(
  'sessions/fetchAll',
  async () => {
    return await sessionService.list()
  }
)

// ➕ Create a new session
export const createSession = createAsyncThunk(
  'sessions/create',
  async (data: CreateSessionRequest) => {
    return await sessionService.create(data)
  }
)

export const regenerateTitle = createAsyncThunk(
  'sessions/regenerateTitle',
  async (id: string) => {
    return await sessionService.generateTitle(id)
  }
)

// 🔍 Fetch single session by ID
export const fetchSessionById = createAsyncThunk(
  'sessions/fetchById',
  async (id: string) => {
    return await sessionService.get(id)
  }
)


const sessionSlice = createSlice({
  name: 'sessions',
  initialState,
  reducers: {
    selectSession(state, action: PayloadAction<string>) {
      state.currentSessionId = action.payload
    },
    clearSession(state) {
      state.currentSessionId = null
    },
    updateSessionTitle(state, action: PayloadAction<{ id: string; title: string }>) {
      const session = state.sessions.find(conv => conv.id === action.payload.id)
      if (session) {
        session.title = action.payload.title
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSessions.pending, (state) => {
        state.loadingList = true
        state.error = null
      })
      .addCase(fetchSessions.fulfilled, (state, action) => {
        state.loadingList = false
        state.sessions = action.payload
      })
      .addCase(fetchSessions.rejected, (state, action) => {
        state.loadingList = false
        state.error = action.error.message ?? 'Error fetching sessions'
      })

      // fetchSessionById
      .addCase(fetchSessionById.pending, (state) => {
        state.loadingSession = true
        state.selectedSessionDetails = null
      })
      .addCase(fetchSessionById.fulfilled, (state, action) => {
        state.loadingSession = false
        state.selectedSessionDetails = action.payload
      })
      .addCase(fetchSessionById.rejected, (state, action) => {
        state.loadingSession = false
        state.error = action.error.message ?? 'Error loading session'
      })

      .addCase(createSession.fulfilled, (state, action) => {
        const newConv: SessionListItem = {
          id: action.payload.id,
          title: action.payload.title,
          created_at: action.payload.created_at,
        }
        state.sessions.unshift(newConv)
        state.currentSessionId = newConv.id
      })
      .addCase(regenerateTitle.fulfilled, (state, action) => {
        if (action.payload.title) {
          const session = state.sessions.find(c => c.id === action.payload.session_id)
          if (session) session.title = action.payload.title
        }
      })
  },
})

export const { selectSession, clearSession, updateSessionTitle } = sessionSlice.actions
export default sessionSlice.reducer
