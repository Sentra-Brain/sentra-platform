import { describe, it, expect, beforeEach } from 'vitest';
import { configureStore } from '@reduxjs/toolkit';
import stepsReducer, {
  stepStarted,
  stepProgress,
  stepEnded,
  stepErrored,
  toggleStepOpen,
  rehydrateFromSystemMessages,
  resetStepsForConversation,
  selectStepsForConversation,
  selectStepsByOrder,
  type StepsState
} from '../src/features/chat/steps/stepsSlice';
import type { ConversationEvent } from '../src/features/chat/types/events';
import type { ChatMessage } from '../src/features/conversations/types/conversationModels';

// Create a test store
const createTestStore = () => {
  return configureStore({
    reducer: {
      steps: stepsReducer
    }
  });
};

describe('Steps Slice', () => {
  let store: ReturnType<typeof createTestStore>;
  const conversationId = 'test-conversation-123';

  beforeEach(() => {
    store = createTestStore();
  });

  it('should have initial empty state', () => {
    const state = store.getState().steps;
    expect(state.byConversationId).toEqual({});
  });

  it('should handle stepStarted action', () => {
    const event: ConversationEvent = {
      event_id: 'event-1',
      type: 'step_start',
      task_run_id: 'task-1',
      task_type: 'rag_search',
      label: 'Searching Knowledge Base',
      status: 'searching',
      content: 'Starting search...',
      timestamp: '2024-01-01T00:00:00Z'
    };

    store.dispatch(stepStarted({ conversationId, event }));

    const convState = selectStepsForConversation(store.getState(), conversationId);
    expect(convState.order).toEqual(['task-1']);
    expect(convState.items['task-1']).toEqual({
      taskRunId: 'task-1',
      taskType: 'rag_search',
      label: 'Searching Knowledge Base',
      status: 'searching',
      startedAt: Date.parse('2024-01-01T00:00:00Z'),
      details: 'Starting search...',
      meta: {},
      isOpen: true
    });
    expect(convState.seenEventIds['event-1']).toBe(true);
  });

  it('should handle stepProgress action', () => {
    // First start a step
    const startEvent: ConversationEvent = {
      event_id: 'event-1',
      type: 'step_start',
      task_run_id: 'task-1',
      label: 'Processing',
      status: 'running',
      content: 'Starting...',
      timestamp: '2024-01-01T00:00:00Z'
    };
    store.dispatch(stepStarted({ conversationId, event: startEvent }));

    // Then send progress
    const progressEvent: ConversationEvent = {
      event_id: 'event-2',
      type: 'step_progress',
      task_run_id: 'task-1',
      content: 'Making progress...',
      meta: { progress: 0.5 },
      timestamp: '2024-01-01T00:00:30Z'
    };
    store.dispatch(stepProgress({ conversationId, event: progressEvent }));

    const convState = selectStepsForConversation(store.getState(), conversationId);
    const step = convState.items['task-1'];
    expect(step.progress).toBe(0.5);
    expect(step.details).toBe('Making progress...');
    expect(step.isOpen).toBe(true);
    expect(convState.seenEventIds['event-2']).toBe(true);
  });

  it('should handle stepEnded action and auto-close', () => {
    // Start a step
    const startEvent: ConversationEvent = {
      event_id: 'event-1',
      type: 'step_start',
      task_run_id: 'task-1',
      timestamp: '2024-01-01T00:00:00Z'
    };
    store.dispatch(stepStarted({ conversationId, event: startEvent }));

    // End the step
    const endEvent: ConversationEvent = {
      event_id: 'event-2',
      type: 'step_end',
      task_run_id: 'task-1',
      content: 'Completed successfully',
      meta: { chunks_found: 5 },
      timestamp: '2024-01-01T00:01:00Z'
    };
    store.dispatch(stepEnded({ conversationId, event: endEvent }));

    const convState = selectStepsForConversation(store.getState(), conversationId);
    const step = convState.items['task-1'];
    expect(step.status).toBe('completed');
    expect(step.endedAt).toBe(Date.parse('2024-01-01T00:01:00Z'));
    expect(step.details).toBe('Completed successfully');
    expect(step.isOpen).toBe(false); // Auto-closed
    expect(step.meta?.chunks_found).toBe(5);
  });

  it('should handle stepErrored action and auto-close', () => {
    // Start a step
    const startEvent: ConversationEvent = {
      event_id: 'event-1',
      type: 'step_start',
      task_run_id: 'task-1',
      timestamp: '2024-01-01T00:00:00Z'
    };
    store.dispatch(stepStarted({ conversationId, event: startEvent }));

    // Error the step
    const errorEvent: ConversationEvent = {
      event_id: 'event-2',
      type: 'step_error',
      task_run_id: 'task-1',
      content: 'An error occurred',
      timestamp: '2024-01-01T00:00:30Z'
    };
    store.dispatch(stepErrored({ conversationId, event: errorEvent }));

    const convState = selectStepsForConversation(store.getState(), conversationId);
    const step = convState.items['task-1'];
    expect(step.status).toBe('error');
    expect(step.endedAt).toBe(Date.parse('2024-01-01T00:00:30Z'));
    expect(step.details).toBe('An error occurred');
    expect(step.isOpen).toBe(false); // Auto-closed
  });

  it('should handle toggleStepOpen action', () => {
    // Start and end a step (so it's closed)
    const startEvent: ConversationEvent = {
      event_id: 'event-1',
      type: 'step_start',
      task_run_id: 'task-1',
      timestamp: '2024-01-01T00:00:00Z'
    };
    store.dispatch(stepStarted({ conversationId, event: startEvent }));

    const endEvent: ConversationEvent = {
      event_id: 'event-2',
      type: 'step_end',
      task_run_id: 'task-1',
      timestamp: '2024-01-01T00:01:00Z'
    };
    store.dispatch(stepEnded({ conversationId, event: endEvent }));

    // Manually open it
    store.dispatch(toggleStepOpen({
      conversationId,
      taskRunId: 'task-1',
      isOpen: true
    }));

    const convState = selectStepsForConversation(store.getState(), conversationId);
    expect(convState.items['task-1'].isOpen).toBe(true);

    // Toggle it
    store.dispatch(toggleStepOpen({
      conversationId,
      taskRunId: 'task-1'
    }));

    const convState2 = selectStepsForConversation(store.getState(), conversationId);
    expect(convState2.items['task-1'].isOpen).toBe(false);
  });

  it('should ignore duplicate events (idempotency)', () => {
    const event: ConversationEvent = {
      event_id: 'event-1',
      type: 'step_start',
      task_run_id: 'task-1',
      content: 'First time',
      timestamp: '2024-01-01T00:00:00Z'
    };

    // Send the same event twice
    store.dispatch(stepStarted({ conversationId, event }));
    store.dispatch(stepStarted({ conversationId, event }));

    const convState = selectStepsForConversation(store.getState(), conversationId);
    expect(convState.order).toEqual(['task-1']); // Only one entry
    expect(convState.items['task-1'].details).toBe('First time');
  });

  it('should handle rehydrateFromSystemMessages', () => {
    const messages: ChatMessage[] = [
      {
        id: 'msg-1',
        role: 'user',
        content: 'Hello',
        timestamp: Date.now()
      },
      {
        id: 'event-1',
        role: 'system',
        content: 'Starting search...',
        timestamp: Date.parse('2024-01-01T00:00:00Z'),
        event_id: 'event-1',
        event_type: 'step_start',
        task_run_id: 'task-1',
        task_type: 'rag_search',
        label: 'Knowledge Search',
        status: 'searching'
      },
      {
        id: 'event-2',
        role: 'system',
        content: 'Search completed',
        timestamp: Date.parse('2024-01-01T00:01:00Z'),
        event_id: 'event-2',
        event_type: 'step_end',
        task_run_id: 'task-1',
        meta: { chunks_found: 3 }
      }
    ];

    store.dispatch(rehydrateFromSystemMessages({ conversationId, messages }));

    const steps = selectStepsByOrder(store.getState(), conversationId);
    expect(steps).toHaveLength(1);
    expect(steps[0].taskRunId).toBe('task-1');
    expect(steps[0].label).toBe('Knowledge Search');
    expect(steps[0].status).toBe('completed');
    expect(steps[0].isOpen).toBe(false); // Closed for rehydration
    expect(steps[0].meta?.chunks_found).toBe(3);
  });

  it('should handle resetStepsForConversation', () => {
    // Add some steps
    const event: ConversationEvent = {
      event_id: 'event-1',
      type: 'step_start',
      task_run_id: 'task-1',
      timestamp: '2024-01-01T00:00:00Z'
    };
    store.dispatch(stepStarted({ conversationId, event }));

    // Reset
    store.dispatch(resetStepsForConversation(conversationId));

    const convState = selectStepsForConversation(store.getState(), conversationId);
    expect(convState.order).toEqual([]);
    expect(convState.items).toEqual({});
    expect(convState.seenEventIds).toEqual({});
  });

  it('should handle multiple conversations independently', () => {
    const conv1 = 'conv-1';
    const conv2 = 'conv-2';

    const event1: ConversationEvent = {
      event_id: 'event-1',
      type: 'step_start',
      task_run_id: 'task-1',
      content: 'Conv 1 step',
      timestamp: '2024-01-01T00:00:00Z'
    };

    const event2: ConversationEvent = {
      event_id: 'event-2',
      type: 'step_start',
      task_run_id: 'task-2',
      content: 'Conv 2 step',
      timestamp: '2024-01-01T00:00:00Z'
    };

    store.dispatch(stepStarted({ conversationId: conv1, event: event1 }));
    store.dispatch(stepStarted({ conversationId: conv2, event: event2 }));

    const conv1State = selectStepsForConversation(store.getState(), conv1);
    const conv2State = selectStepsForConversation(store.getState(), conv2);

    expect(conv1State.order).toEqual(['task-1']);
    expect(conv2State.order).toEqual(['task-2']);
    expect(conv1State.items['task-1'].details).toBe('Conv 1 step');
    expect(conv2State.items['task-2'].details).toBe('Conv 2 step');
  });

  it('should ignore events without task_run_id', () => {
    const event: ConversationEvent = {
      event_id: 'event-1',
      type: 'step_start',
      // Missing task_run_id
      content: 'Should be ignored',
      timestamp: '2024-01-01T00:00:00Z'
    };

    store.dispatch(stepStarted({ conversationId, event }));

    const convState = selectStepsForConversation(store.getState(), conversationId);
    expect(convState.order).toEqual([]);
    expect(Object.keys(convState.items)).toHaveLength(0);
  });
});