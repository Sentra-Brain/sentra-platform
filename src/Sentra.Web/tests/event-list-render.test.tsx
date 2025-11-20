import React from 'react'
import { describe, it, expect } from 'vitest'
import { renderToString } from 'react-dom/server'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import EventList from '../src/features/chat/components/EventList'
import eventsReducer, { type RenderableEvent } from '../src/features/chat/eventsSlice'

describe('EventList rendering', () => {
  it('renders messages and errors', () => {
    const store = configureStore({ reducer: { events: eventsReducer } })
    const events: RenderableEvent[] = [
      {
        id: '1',
        type: 'final',
        role: 'user',
        content: 'hi',
      },
      {
        id: '2',
        type: 'message_delta',
        role: 'assistant',
        content: 'thinking...',
      },
      {
        id: '3',
        type: 'error',
        content: 'oops',
      },
    ]

    const html = renderToString(
      <Provider store={store}>
        <EventList events={events} />
      </Provider>
    )

    expect(html).toContain('hi')
    expect(html).toContain('thinking...')
    expect(html).toContain('oops')
  })
})
