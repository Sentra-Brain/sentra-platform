import { createSlice, type PayloadAction, createSelector } from '@reduxjs/toolkit'
import type { BaseEvent as AGUIEvent, Role } from '@ag-ui/core'
import { EventType } from '@ag-ui/core'
import type { ConversationMode } from '@features/chat/types/mode'

export interface SelectedContext {
  sourceIds: string[]
  documentIds: string[]
  useRag: boolean
}

export interface EventsState {
  sessionId: string | null
  events: AGUIEvent[]
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
    addEvent(state, action: PayloadAction<AGUIEvent>) {
      state.events.push(action.payload)
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

export const selectAllEvents = (state: { events: EventsState }): AGUIEvent[] =>
  state.events.events

export type RenderableEvent =
  | {
      id: string
      type: 'message_delta' | 'final'
      role: Role
      content: string
    }
  | {
      id: string
      type: 'error'
      content: string
    }

const buildRenderableEvents = (events: AGUIEvent[]): RenderableEvent[] => {
  const orderedKeys: string[] = []
  const entries = new Map<string, RenderableEvent>()
  const ensureMessageEntry = (messageId: string, role?: Role) => {
    const existing = entries.get(messageId) as RenderableEvent | undefined
    if (!existing) {
      const entry: RenderableEvent = {
        id: messageId,
        type: 'message_delta',
        role: (role ?? 'assistant') as Role,
        content: '',
      }
      entries.set(messageId, entry)
      orderedKeys.push(messageId)
      return entry
    }
    if (role && 'role' in existing) {
      existing.role = role
    }
    return existing
  }

  let errorCount = 0

  for (const event of events) {
    switch (event.type) {
      case EventType.TEXT_MESSAGE_START: {
        ensureMessageEntry(event.messageId, event.role)
        break
      }
      case EventType.TEXT_MESSAGE_CONTENT: {
        const entry = ensureMessageEntry(event.messageId)
        if ('role' in entry) {
          entry.content = `${entry.content}${event.delta}`
          entry.type = 'message_delta'
        }
        break
      }
      case EventType.TEXT_MESSAGE_END: {
        const entry = ensureMessageEntry(event.messageId)
        if ('role' in entry) {
          entry.type = 'final'
        }
        break
      }
      case EventType.RUN_ERROR: {
        const errorId = `error-${errorCount++}`
        entries.set(errorId, {
          id: errorId,
          type: 'error',
          content: event.message,
        })
        orderedKeys.push(errorId)
        break
      }
      default:
        break
    }
  }

  return orderedKeys
    .map(key => entries.get(key))
    .filter((entry): entry is RenderableEvent => Boolean(entry))
}

export const selectRenderableEvents = createSelector(
  selectAllEvents,
  buildRenderableEvents,
)

export const {
  setSessionId,
  addEvent,
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

