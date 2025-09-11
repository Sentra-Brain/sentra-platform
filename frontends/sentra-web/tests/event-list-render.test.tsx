import React from 'react'
import { describe, it, expect } from 'vitest'
import { renderToString } from 'react-dom/server'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import EventList from '../src/features/chat/components/EventList'
import eventsReducer from '../src/features/chat/eventsSlice'
import { SentraEventType, type SentraEvent } from '../src/features/chat/types/events'

describe('EventList rendering', () => {
  it('renders messages, steps, and errors', () => {
    const store = configureStore({ reducer: { events: eventsReducer } })
    const events: SentraEvent[] = [
      {
        id: '1',
        type: SentraEventType.MESSAGE_FINAL,
        author: 'user',
        content: { role: 'user', parts: [{ text: 'hi' }] },
        timestamp: '2025-01-01T00:00:00Z',
      },
      {
        id: '2',
        type: SentraEventType.STEP_START,
        author: 'system',
        content: { role: 'system', parts: [{ text: 'process' }] },
        timestamp: '2025-01-01T00:00:01Z',
        meta: { label: 'Step' },
      },
      {
        id: '3',
        type: SentraEventType.ERROR,
        author: 'system',
        content: { role: 'system', parts: [{ text: 'oops' }] },
        timestamp: '2025-01-01T00:00:02Z',
      },
    ]

    const html = renderToString(
      <Provider store={store}>
        <EventList events={events} />
      </Provider>
    )

    expect(html).toContain('hi')
    expect(html).toContain('process')
    expect(html).toContain('oops')
  })
})
