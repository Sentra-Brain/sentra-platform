// tests/steps-slice.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { configureStore } from '@reduxjs/toolkit';
import stepsReducer, { 
  stepStarted, 
  stepUpdated, 
  clearSteps 
} from '../src/features/chat/stepsSlice';

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

  beforeEach(() => {
    store = createTestStore();
  });

  it('should have empty steps initially', () => {
    const state = store.getState().steps;
    expect(state.steps).toEqual([]);
  });

  it('should add a new step when stepStarted is dispatched', () => {
    store.dispatch(stepStarted({ id: 'rag_search', label: 'Searching knowledge base' }));
    
    const state = store.getState().steps;
    expect(state.steps).toHaveLength(1);
    expect(state.steps[0]).toEqual({
      id: 'rag_search',
      label: 'Searching knowledge base',
      status: 'running'
    });
  });

  it('should update existing step when stepStarted is dispatched again', () => {
    // Add initial step
    store.dispatch(stepStarted({ id: 'rag_search', label: 'Searching knowledge base' }));
    
    // Update the same step
    store.dispatch(stepStarted({ id: 'rag_search', label: 'Updated label' }));
    
    const state = store.getState().steps;
    expect(state.steps).toHaveLength(1);
    expect(state.steps[0].label).toBe('Updated label');
    expect(state.steps[0].status).toBe('running');
  });

  it('should update step status and meta when stepUpdated is dispatched', () => {
    // Add initial step
    store.dispatch(stepStarted({ id: 'rag_search', label: 'Searching knowledge base' }));
    
    // Update step to done with meta
    store.dispatch(stepUpdated({ 
      id: 'rag_search', 
      status: 'done', 
      meta: { num_chunks: 5 } 
    }));
    
    const state = store.getState().steps;
    expect(state.steps[0].status).toBe('done');
    expect(state.steps[0].meta).toEqual({ num_chunks: 5 });
  });

  it('should update step status to error', () => {
    // Add initial step
    store.dispatch(stepStarted({ id: 'rag_search', label: 'Searching knowledge base' }));
    
    // Update step to error
    store.dispatch(stepUpdated({ id: 'rag_search', status: 'error' }));
    
    const state = store.getState().steps;
    expect(state.steps[0].status).toBe('error');
  });

  it('should clear all steps when clearSteps is dispatched', () => {
    // Add multiple steps
    store.dispatch(stepStarted({ id: 'step1', label: 'Step 1' }));
    store.dispatch(stepStarted({ id: 'step2', label: 'Step 2' }));
    
    // Clear steps
    store.dispatch(clearSteps());
    
    const state = store.getState().steps;
    expect(state.steps).toEqual([]);
  });

  it('should handle multiple steps independently', () => {
    // Add multiple steps
    store.dispatch(stepStarted({ id: 'rag_search', label: 'Searching knowledge base' }));
    store.dispatch(stepStarted({ id: 'mcp_call', label: 'Making MCP call' }));
    
    // Update only one step
    store.dispatch(stepUpdated({ id: 'rag_search', status: 'done', meta: { num_chunks: 3 } }));
    
    const state = store.getState().steps;
    expect(state.steps).toHaveLength(2);
    expect(state.steps[0].status).toBe('done');
    expect(state.steps[1].status).toBe('running');
  });

  it('should ignore stepUpdated for non-existent step', () => {
    store.dispatch(stepUpdated({ id: 'non_existent', status: 'done' }));
    
    const state = store.getState().steps;
    expect(state.steps).toEqual([]);
  });
});