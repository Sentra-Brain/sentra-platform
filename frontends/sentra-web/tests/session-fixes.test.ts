// Test for session creation and rendering flow fixes
import { describe, it, expect } from 'vitest'
import { configureStore } from '@reduxjs/toolkit'
import eventsReducer, { setWaitingForAnswer, addEvent } from '../src/features/chat/eventsSlice'
import { SentraEventType } from '../src/features/chat/types/events'
import sessionReducer, { updateSessionTitle } from '../src/features/sessions/sessionsSlice'

describe('Session Creation and Rendering Flow Fixes', () => {
  it('should update session title in Redux state', () => {
    const store = configureStore({
      reducer: {
        session: sessionReducer,
      },
      preloadedState: {
        session: {
          sessions: [
            { id: 'test-conv-1', title: 'Untitled', created_at: '2025-01-01' }
          ],
          currentSessionId: null,
          selectedSessionDetails: null,
          loadingList: false,
          loadingSession: false,
          error: null,
        }
      }
    })

    // Simulate title update after LLM generation
    store.dispatch(updateSessionTitle({
      id: 'test-conv-1',
      title: 'Updated LLM Generated Title'
    }))

    const state = store.getState()
    const session = state.session.sessions.find(c => c.id === 'test-conv-1')

    expect(session?.title).toBe('Updated LLM Generated Title')
  })

  it('should handle waiting for answer state correctly', () => {
    const store = configureStore({
      reducer: {
        events: eventsReducer,
      },
    })

    // Initially not waiting
    expect(store.getState().events.waitingForAnswer).toBe(false)

    // Set waiting for answer
    store.dispatch(setWaitingForAnswer(true))
    expect(store.getState().events.waitingForAnswer).toBe(true)

    // Clear waiting state
    store.dispatch(setWaitingForAnswer(false))
    expect(store.getState().events.waitingForAnswer).toBe(false)
  })

  it('should handle messages correctly', () => {
    const store = configureStore({
      reducer: {
        events: eventsReducer,
      },
    })

    const userEvent = {
      id: 'evt-1',
      type: SentraEventType.MESSAGE_FINAL,
      author: 'user',
      content: { role: 'user', parts: [{ text: 'Test message' }] },
      timestamp: new Date().toISOString(),
    }

    store.dispatch(addEvent(userEvent))

    const state = store.getState()
    expect(state.events.order).toHaveLength(1)
    const stored = state.events.eventsById['evt-1']
    expect(stored.type).toBe(SentraEventType.MESSAGE_FINAL)
    expect(stored.content?.parts[0].text).toBe('Test message')
  })
})