import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import type { Event } from '@features/chat/types/events'
import type { ConversationMode } from '@features/chat/types/mode'

export interface SelectedContext {
  sourceIds: string[]
  documentIds: string[]
  useRag: boolean
}

interface EventsState {
  sessionId: string | null
  events: Event[]
  waitingForAnswer: boolean
  isStreaming: boolean
  inputDisabled: boolean
  selectedContext: SelectedContext
  mode: ConversationMode
}

const storedMode =
  (typeof window !== 'undefined'
    ? (localStorage.getItem('sentra.chat.mode') as ConversationMode | null)
    : null) || 'fast'

const initialState: EventsState = {
  sessionId: null,
  events: [],
  waitingForAnswer: false,
  isStreaming: false,
  inputDisabled: false,
  selectedContext: {
    sourceIds: [],
    documentIds: [],
    useRag: true,
  },
  mode: storedMode,
}

const eventsSlice = createSlice({
  name: 'events',
  initialState,
  reducers: {
    setSessionId(state, action: PayloadAction<string | null>) {
      state.sessionId = action.payload
    },
    addEvent(state, action: PayloadAction<Event>) {
      state.events.push(action.payload)
    },
    updateEvent(state, action: PayloadAction<Event>) {
      const idx = state.events.findIndex(e => e.id === action.payload.id)
      if (idx === -1) {
        state.events.push(action.payload)
        return
      }
      const existing = state.events[idx] as any
      if (action.payload.type === 'message_delta') {
        existing.content = (existing.content || '') + (action.payload as any).content
      } else {
        state.events[idx] = { ...existing, ...action.payload }
      }
    },
    resetEvents(state) {
      state.events = []
      state.sessionId = null
    },
    setWaitingForAnswer(state, action: PayloadAction<boolean>) {
      state.waitingForAnswer = action.payload
    },
    setStreaming(state, action: PayloadAction<boolean>) {
      state.isStreaming = action.payload
    },
    setInputDisabled(state, action: PayloadAction<boolean>) {
      state.inputDisabled = action.payload
    },
    setSelectedContext(state, action: PayloadAction<SelectedContext>) {
      state.selectedContext = action.payload
    },
    updateUseRag(state, action: PayloadAction<boolean>) {
      state.selectedContext.useRag = action.payload
    },
    addContextSource(state, action: PayloadAction<string>) {
      if (!state.selectedContext.sourceIds.includes(action.payload)) {
        state.selectedContext.sourceIds.push(action.payload)
      }
    },
    removeContextSource(state, action: PayloadAction<string>) {
      state.selectedContext.sourceIds = state.selectedContext.sourceIds.filter(
        id => id !== action.payload
      )
    },
    addContextDocument(state, action: PayloadAction<string>) {
      if (!state.selectedContext.documentIds.includes(action.payload)) {
        state.selectedContext.documentIds.push(action.payload)
      }
    },
    removeContextDocument(state, action: PayloadAction<string>) {
      state.selectedContext.documentIds = state.selectedContext.documentIds.filter(
        id => id !== action.payload
      )
    },
    clearSelectedContext(state) {
      state.selectedContext = {
        sourceIds: [],
        documentIds: [],
        useRag: true,
      }
    },
    setMode(state, action: PayloadAction<ConversationMode>) {
      state.mode = action.payload
      try {
        localStorage.setItem('sentra.chat.mode', action.payload)
      } catch (err) {
        console.error('Failed to save chat mode', err)
      }
    },
  },
})

export const {
  setSessionId,
  addEvent,
  updateEvent,
  resetEvents,
  setWaitingForAnswer,
  setStreaming,
  setInputDisabled,
  setSelectedContext,
  updateUseRag,
  addContextSource,
  removeContextSource,
  addContextDocument,
  removeContextDocument,
  clearSelectedContext,
  setMode,
} = eventsSlice.actions

export default eventsSlice.reducer

