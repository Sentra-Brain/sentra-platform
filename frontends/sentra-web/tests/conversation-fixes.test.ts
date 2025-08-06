// Test for conversation creation and rendering flow fixes
import { describe, it, expect } from 'vitest'
import { configureStore } from '@reduxjs/toolkit'
import chatReducer, { setWaitingForAnswer, addMessage } from '../src/features/chat/chatSlice'
import conversationReducer, { updateConversationTitle } from '../src/features/conversations/conversationSlice'

describe('Conversation Creation and Rendering Flow Fixes', () => {
  it('should update conversation title in Redux state', () => {
    const store = configureStore({
      reducer: {
        conversation: conversationReducer,
      },
      preloadedState: {
        conversation: {
          conversations: [
            { id: 'test-conv-1', title: 'Untitled', created_at: '2025-01-01' }
          ],
          currentConversationId: null,
          selectedConversationDetails: null,
          loadingList: false,
          loadingConversation: false,
          error: null,
        }
      }
    })

    // Simulate title update after LLM generation
    store.dispatch(updateConversationTitle({ 
      id: 'test-conv-1', 
      title: 'Updated LLM Generated Title' 
    }))

    const state = store.getState()
    const conversation = state.conversation.conversations.find(c => c.id === 'test-conv-1')
    
    expect(conversation?.title).toBe('Updated LLM Generated Title')
  })

  it('should handle waiting for answer state correctly', () => {
    const store = configureStore({
      reducer: {
        chat: chatReducer,
      },
    })

    // Initially not waiting
    expect(store.getState().chat.waitingForAnswer).toBe(false)

    // Set waiting for answer
    store.dispatch(setWaitingForAnswer(true))
    expect(store.getState().chat.waitingForAnswer).toBe(true)

    // Clear waiting state
    store.dispatch(setWaitingForAnswer(false))
    expect(store.getState().chat.waitingForAnswer).toBe(false)
  })

  it('should handle messages correctly', () => {
    const store = configureStore({
      reducer: {
        chat: chatReducer,
      },
    })

    // Add user message
    const userMessage = {
      id: 'msg-1',
      role: 'user' as const,
      content: 'Test message',
      timestamp: Date.now(),
    }

    store.dispatch(addMessage(userMessage))
    
    const state = store.getState()
    expect(state.chat.messages).toHaveLength(1)
    expect(state.chat.messages[0].role).toBe('user')
    expect(state.chat.messages[0].content).toBe('Test message')
  })
})