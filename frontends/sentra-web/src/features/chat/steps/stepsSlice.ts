// src/features/chat/steps/stepsSlice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import type { ConversationEvent } from '@features/chat/types/events'
import type { ChatMessage } from '@features/conversations/types/conversationModels'

export type StepStatus = 'running' | 'searching' | 'completed' | 'error'

export type StepEntry = {
  taskRunId: string
  taskType?: string
  label?: string
  status: StepStatus
  startedAt?: number // epoch ms
  endedAt?: number
  progress?: number // 0..1 if available
  details?: string // last content/summary
  meta?: Record<string, unknown>
  isOpen: boolean // UI state
}

export type StepsStatePerConversation = {
  order: string[] // taskRunId insertion order
  items: Record<string, StepEntry> // by taskRunId
  seenEventIds: Record<string, true> // idempotency per event_id
}

export type StepsState = {
  byConversationId: Record<string, StepsStatePerConversation>
}

const initialState: StepsState = {
  byConversationId: {}
}

const getConversationState = (
  state: StepsState,
  conversationId: string
): StepsStatePerConversation => {
  if (!state.byConversationId[conversationId]) {
    state.byConversationId[conversationId] = {
      order: [],
      items: {},
      seenEventIds: {}
    }
  }
  return state.byConversationId[conversationId]
}

const stepsSlice = createSlice({
  name: 'steps',
  initialState,
  reducers: {
    stepStarted: (
      state,
      action: PayloadAction<{ conversationId: string; event: ConversationEvent }>
    ) => {
      const { conversationId, event } = action.payload
      
      if (event.type !== 'step_start' || !event.task_run_id) return
      
      const convState = getConversationState(state, conversationId)
      
      // Idempotency check
      if (convState.seenEventIds[event.event_id]) return
      convState.seenEventIds[event.event_id] = true
      
      const taskRunId = event.task_run_id
      const isNewStep = !convState.items[taskRunId]
      
      convState.items[taskRunId] = {
        taskRunId,
        taskType: event.task_type,
        label: event.label,
        status: (event.status as StepStatus) ?? 'running',
        startedAt: event.timestamp ? Date.parse(event.timestamp) : Date.now(),
        details: event.content ?? '',
        meta: event.meta ?? {},
        isOpen: true
      }
      
      // Add to order if new
      if (isNewStep) {
        convState.order.push(taskRunId)
      }
    },

    stepProgress: (
      state,
      action: PayloadAction<{ conversationId: string; event: ConversationEvent }>
    ) => {
      const { conversationId, event } = action.payload
      
      if (event.type !== 'step_progress' || !event.task_run_id) return
      
      const convState = getConversationState(state, conversationId)
      
      // Idempotency check
      if (convState.seenEventIds[event.event_id]) return
      convState.seenEventIds[event.event_id] = true
      
      const taskRunId = event.task_run_id
      const entry = convState.items[taskRunId]
      
      if (entry) {
        entry.progress = (event.meta?.progress as number) ?? entry.progress
        entry.details = event.content ?? entry.details
        entry.meta = { ...entry.meta, ...event.meta }
        entry.isOpen = true // Keep open during progress
      }
    },

    stepEnded: (
      state,
      action: PayloadAction<{ conversationId: string; event: ConversationEvent }>
    ) => {
      const { conversationId, event } = action.payload
      
      if (event.type !== 'step_end' || !event.task_run_id) return
      
      const convState = getConversationState(state, conversationId)
      
      // Idempotency check
      if (convState.seenEventIds[event.event_id]) return
      convState.seenEventIds[event.event_id] = true
      
      const taskRunId = event.task_run_id
      const entry = convState.items[taskRunId]
      
      if (entry) {
        entry.status = 'completed'
        entry.endedAt = event.timestamp ? Date.parse(event.timestamp) : Date.now()
        entry.details = event.content ?? entry.details
        entry.meta = { ...entry.meta, ...event.meta }
        entry.isOpen = false // Auto-collapse on completion
      }
    },

    stepErrored: (
      state,
      action: PayloadAction<{ conversationId: string; event: ConversationEvent }>
    ) => {
      const { conversationId, event } = action.payload
      
      if (event.type !== 'step_error' || !event.task_run_id) return
      
      const convState = getConversationState(state, conversationId)
      
      // Idempotency check
      if (convState.seenEventIds[event.event_id]) return
      convState.seenEventIds[event.event_id] = true
      
      const taskRunId = event.task_run_id
      const entry = convState.items[taskRunId]
      
      if (entry) {
        entry.status = 'error'
        entry.endedAt = event.timestamp ? Date.parse(event.timestamp) : Date.now()
        entry.details = event.content ?? entry.details
        entry.meta = { ...entry.meta, ...event.meta }
        entry.isOpen = false // Auto-collapse on error
      }
    },

    toggleStepOpen: (
      state,
      action: PayloadAction<{ conversationId: string; taskRunId: string; isOpen?: boolean }>
    ) => {
      const { conversationId, taskRunId, isOpen } = action.payload
      const convState = getConversationState(state, conversationId)
      const entry = convState.items[taskRunId]
      
      if (entry) {
        entry.isOpen = isOpen ?? !entry.isOpen
      }
    },

    rehydrateFromSystemMessages: (
      state,
      action: PayloadAction<{ conversationId: string; messages: ChatMessage[] }>
    ) => {
      const { conversationId, messages } = action.payload
      
      // Filter system messages that are step events
      const stepMessages = messages.filter(
        msg => msg.role === 'system' && 
               msg.event_type && 
               ['step_start', 'step_progress', 'step_end', 'step_error'].includes(msg.event_type)
      )
      
      // Convert to synthetic events and process in order
      for (const msg of stepMessages) {
        if (!msg.event_type || !msg.event_id) continue
        
        const syntheticEvent: ConversationEvent = {
          event_id: msg.event_id,
          type: msg.event_type as any,
          task_run_id: msg.task_run_id,
          task_type: msg.task_type,
          label: msg.label,
          status: msg.status,
          content: msg.content,
          meta: msg.meta,
          timestamp: new Date(msg.timestamp).toISOString()
        }
        
        // Process through the appropriate reducer
        switch (msg.event_type) {
          case 'step_start':
            stepsSlice.caseReducers.stepStarted(state, {
              type: 'steps/stepStarted',
              payload: { conversationId, event: syntheticEvent }
            })
            break
          case 'step_progress':
            stepsSlice.caseReducers.stepProgress(state, {
              type: 'steps/stepProgress',
              payload: { conversationId, event: syntheticEvent }
            })
            break
          case 'step_end':
            stepsSlice.caseReducers.stepEnded(state, {
              type: 'steps/stepEnded',
              payload: { conversationId, event: syntheticEvent }
            })
            // For rehydration, keep completed steps closed
            if (syntheticEvent.task_run_id) {
              const convState = getConversationState(state, conversationId)
              const entry = convState.items[syntheticEvent.task_run_id]
              if (entry) entry.isOpen = false
            }
            break
          case 'step_error':
            stepsSlice.caseReducers.stepErrored(state, {
              type: 'steps/stepErrored',
              payload: { conversationId, event: syntheticEvent }
            })
            // For rehydration, keep error steps closed
            if (syntheticEvent.task_run_id) {
              const convState = getConversationState(state, conversationId)
              const entry = convState.items[syntheticEvent.task_run_id]
              if (entry) entry.isOpen = false
            }
            break
        }
      }
    },

    resetStepsForConversation: (
      state,
      action: PayloadAction<string>
    ) => {
      const conversationId = action.payload
      delete state.byConversationId[conversationId]
    }
  }
})

export const {
  stepStarted,
  stepProgress,
  stepEnded,
  stepErrored,
  toggleStepOpen,
  rehydrateFromSystemMessages,
  resetStepsForConversation
} = stepsSlice.actions

export default stepsSlice.reducer

// Selectors
export const selectStepsForConversation = (
  state: { steps: StepsState },
  conversationId: string
): StepsStatePerConversation => {
  return state.steps.byConversationId[conversationId] ?? {
    order: [],
    items: {},
    seenEventIds: {}
  }
}

export const selectStepsByOrder = (
  state: { steps: StepsState },
  conversationId: string
): StepEntry[] => {
  const convState = selectStepsForConversation(state, conversationId)
  return convState.order.map(taskRunId => convState.items[taskRunId]).filter(Boolean)
}