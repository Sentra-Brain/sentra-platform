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

describe('Steps Timeline', () => {
  let store: ReturnType<typeof createTestStore>;

  beforeEach(() => {
    store = createTestStore();
  });

  it('should have initial empty steps state', () => {
    const state = store.getState().steps;
    expect(state.steps).toEqual([]);
  });

  it('should add a new step when stepStarted is dispatched', () => {
    store.dispatch(stepStarted({ stepId: 'rag_search', label: 'Searching knowledge base' }));
    
    const state = store.getState().steps;
    expect(state.steps).toHaveLength(1);
    expect(state.steps[0]).toEqual({
      id: 'rag_search',
      label: 'Searching knowledge base',
      status: 'running'
    });
  });

  it('should update existing step status', () => {
    // Start a step
    store.dispatch(stepStarted({ stepId: 'rag_search', label: 'Searching knowledge base' }));
    
    // Update the step
    store.dispatch(stepUpdated({ 
      stepId: 'rag_search', 
      status: 'done', 
      meta: { num_chunks: 5 } 
    }));
    
    const state = store.getState().steps;
    expect(state.steps[0]).toEqual({
      id: 'rag_search',
      label: 'Searching knowledge base',
      status: 'done',
      meta: { num_chunks: 5 }
    });
  });

  it('should handle step error status', () => {
    store.dispatch(stepStarted({ stepId: 'rag_search', label: 'Searching knowledge base' }));
    store.dispatch(stepUpdated({ stepId: 'rag_search', status: 'error' }));
    
    const state = store.getState().steps;
    expect(state.steps[0].status).toBe('error');
  });

  it('should clear all steps', () => {
    // Add multiple steps
    store.dispatch(stepStarted({ stepId: 'step1', label: 'Step 1' }));
    store.dispatch(stepStarted({ stepId: 'step2', label: 'Step 2' }));
    
    expect(store.getState().steps.steps).toHaveLength(2);
    
    // Clear steps
    store.dispatch(clearSteps());
    
    expect(store.getState().steps.steps).toEqual([]);
  });

  it('should update existing step instead of creating duplicate', () => {
    // Start step
    store.dispatch(stepStarted({ stepId: 'rag_search', label: 'Searching' }));
    
    // Start again with same ID but different label
    store.dispatch(stepStarted({ stepId: 'rag_search', label: 'Searching knowledge base' }));
    
    const state = store.getState().steps;
    expect(state.steps).toHaveLength(1);
    expect(state.steps[0].label).toBe('Searching knowledge base');
  });

  it('should ignore update for non-existent step', () => {
    store.dispatch(stepUpdated({ stepId: 'non_existent', status: 'done' }));
    
    const state = store.getState().steps;
    expect(state.steps).toHaveLength(0);
  });
});