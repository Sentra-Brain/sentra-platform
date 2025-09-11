import { createSlice, type PayloadAction, createSelector } from '@reduxjs/toolkit'
import { SentraEventType, type SentraEvent } from '@features/chat/types/events'
import type { ConversationMode } from '@features/chat/types/mode'

export interface SelectedContext {
  sourceIds: string[]
  documentIds: string[]
  useRag: boolean
}

export interface EventsState {
  sessionId: string | null
  eventsById: Record<string, SentraEvent>
  order: string[]
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
  eventsById: {},
  order: [],
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
    addEvent(state, action: PayloadAction<SentraEvent>) {
      const evt = action.payload
      if (!state.eventsById[evt.id]) {
        state.eventsById[evt.id] = evt
        state.order.push(evt.id)
      }
    },
    updateEvent(state, action: PayloadAction<SentraEvent>) {
      const evt = action.payload
      const existing = state.eventsById[evt.id]
      if (!existing) {
        state.eventsById[evt.id] = evt
        state.order.push(evt.id)
        return
      }
      if (
        evt.type === SentraEventType.MESSAGE_DELTA &&
        existing.content &&
        evt.content
      ) {
        existing.content.parts = [
          ...existing.content.parts,
          ...evt.content.parts,
        ]
      } else {
        state.eventsById[evt.id] = { ...existing, ...evt }
      }
    },
    resetEvents(state) {
      state.eventsById = {}
      state.order = []
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

// Selectors
export const selectAllEvents = (state: { events: EventsState }): SentraEvent[] =>
  state.events.order.map(id => state.events.eventsById[id])

export const selectMessages = createSelector(selectAllEvents, events =>
  events.filter(e =>
    e.type === SentraEventType.MESSAGE_DELTA ||
    e.type === SentraEventType.MESSAGE_FINAL
  )
)

export const selectSteps = createSelector(selectAllEvents, events =>
  events.filter(e =>
    e.type === SentraEventType.STEP_START ||
    e.type === SentraEventType.STEP_END ||
    e.type === SentraEventType.CONTEXT_BUILT ||
    e.type === SentraEventType.LLM_CALLED
  )
)

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

