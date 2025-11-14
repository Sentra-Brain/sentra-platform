import { describe, it, expect } from 'vitest'
import { configureStore } from '@reduxjs/toolkit'
import eventsReducer, { addEvent, selectRenderableEvents } from '../src/features/chat/eventsSlice'
import { EventType } from '@ag-ui/core'

const createStore = () =>
  configureStore({ reducer: { events: eventsReducer } })

describe('events reducer', () => {
  it('aggregates streaming message events', () => {
    const store = createStore()
    const messageId = 'evt1'

    store.dispatch(addEvent({
      type: EventType.TEXT_MESSAGE_START,
      messageId,
      role: 'assistant',
    }))
    store.dispatch(addEvent({
      type: EventType.TEXT_MESSAGE_CONTENT,
      messageId,
      delta: 'Hel',
    }))
    store.dispatch(addEvent({
      type: EventType.TEXT_MESSAGE_CONTENT,
      messageId,
      delta: 'lo',
    }))

    let renderable = selectRenderableEvents(store.getState())
    expect(renderable).toHaveLength(1)
    expect(renderable[0]).toMatchObject({
      id: messageId,
      type: 'message_delta',
      content: 'Hello',
      role: 'assistant',
    })

    store.dispatch(addEvent({
      type: EventType.TEXT_MESSAGE_END,
      messageId,
    }))

    renderable = selectRenderableEvents(store.getState())
    expect(renderable[0].type).toBe('final')
  })

  it('records error events from the runtime', () => {
    const store = createStore()
    store.dispatch(addEvent({
      type: EventType.RUN_ERROR,
      message: 'boom',
    }))

    const renderable = selectRenderableEvents(store.getState())
    expect(renderable).toHaveLength(1)
    expect(renderable[0]).toEqual({
      id: 'error-0',
      type: 'error',
      content: 'boom',
    })
  })
})
