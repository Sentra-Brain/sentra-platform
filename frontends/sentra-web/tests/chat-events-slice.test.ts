import { describe, it, expect } from 'vitest'
import { configureStore } from '@reduxjs/toolkit'
import eventsReducer, { addEvent, updateEvent } from '../src/features/chat/eventsSlice'
import { SentraEventType } from '../src/features/chat/types/events'

const createStore = () =>
  configureStore({ reducer: { events: eventsReducer } })

describe('events reducer', () => {
  it('appends parts for message_delta', () => {
    const store = createStore()
    const id = 'evt1'
    store.dispatch(
      addEvent({
        id,
        type: SentraEventType.MESSAGE_DELTA,
        author: 'assistant',
        content: { role: 'assistant', parts: [{ text: 'Hel' }] },
        timestamp: new Date().toISOString(),
      })
    )
    store.dispatch(
      updateEvent({
        id,
        type: SentraEventType.MESSAGE_DELTA,
        author: 'assistant',
        content: { role: 'assistant', parts: [{ text: 'lo' }] },
        timestamp: new Date().toISOString(),
      })
    )
    const stored = store.getState().events.eventsById[id]
    expect(stored.content?.parts.map(p => p.text).join('')).toBe('Hello')
  })

  it('replaces parts on message_final', () => {
    const store = createStore()
    const id = 'evt2'
    store.dispatch(
      addEvent({
        id,
        type: SentraEventType.MESSAGE_DELTA,
        author: 'assistant',
        content: { role: 'assistant', parts: [{ text: 'Hel' }] },
        timestamp: new Date().toISOString(),
      })
    )
    store.dispatch(
      updateEvent({
        id,
        type: SentraEventType.MESSAGE_DELTA,
        author: 'assistant',
        content: { role: 'assistant', parts: [{ text: 'lo' }] },
        timestamp: new Date().toISOString(),
      })
    )
    store.dispatch(
      updateEvent({
        id,
        type: SentraEventType.MESSAGE_FINAL,
        author: 'assistant',
        content: { role: 'assistant', parts: [{ text: 'Hi' }] },
        timestamp: new Date().toISOString(),
      })
    )
    const stored = store.getState().events.eventsById[id]
    expect(stored.content?.parts.map(p => p.text).join('')).toBe('Hi')
  })

  it('stores error events', () => {
    const store = createStore()
    const id = 'err1'
    store.dispatch(
      updateEvent({
        id,
        type: SentraEventType.ERROR,
        author: 'system',
        content: { role: 'system', parts: [{ text: 'boom' }] },
        timestamp: new Date().toISOString(),
      })
    )
    const stored = store.getState().events.eventsById[id]
    expect(stored.type).toBe(SentraEventType.ERROR)
  })
})
