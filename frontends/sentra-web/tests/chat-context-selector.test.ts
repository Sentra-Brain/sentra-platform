import { describe, it, expect, beforeEach } from 'vitest';
import { configureStore } from '@reduxjs/toolkit';
import chatReducer, { 
  setSelectedContext, 
  addContextSource, 
  removeContextSource,
  addContextDocument,
  removeContextDocument,
  clearSelectedContext,
  updateUseRag
} from '../src/features/chat/chatSlice';

// Create a test store
const createTestStore = () => {
  return configureStore({
    reducer: {
      chat: chatReducer
    }
  });
};

describe('Chat Context Selector', () => {
  let store: ReturnType<typeof createTestStore>;

  beforeEach(() => {
    store = createTestStore();
  });

  it('should have default selectedContext state', () => {
    const state = store.getState().chat.selectedContext;
    expect(state).toEqual({
      sourceIds: [],
      documentIds: [],
      useRag: true
    });
  });

  it('should set selected context', () => {
    const context = {
      sourceIds: ['source1', 'source2'],
      documentIds: ['doc1', 'doc2'],
      useRag: true
    };

    store.dispatch(setSelectedContext(context));
    const state = store.getState().chat.selectedContext;
    expect(state).toEqual(context);
  });

  it('should add and remove context sources', () => {
    // Add source
    store.dispatch(addContextSource('source1'));
    expect(store.getState().chat.selectedContext.sourceIds).toEqual(['source1']);

    // Add another source
    store.dispatch(addContextSource('source2'));
    expect(store.getState().chat.selectedContext.sourceIds).toEqual(['source1', 'source2']);

    // Don't add duplicate
    store.dispatch(addContextSource('source1'));
    expect(store.getState().chat.selectedContext.sourceIds).toEqual(['source1', 'source2']);

    // Remove source
    store.dispatch(removeContextSource('source1'));
    expect(store.getState().chat.selectedContext.sourceIds).toEqual(['source2']);
  });

  it('should add and remove context documents', () => {
    // Add document
    store.dispatch(addContextDocument('doc1'));
    expect(store.getState().chat.selectedContext.documentIds).toEqual(['doc1']);

    // Add another document
    store.dispatch(addContextDocument('doc2'));
    expect(store.getState().chat.selectedContext.documentIds).toEqual(['doc1', 'doc2']);

    // Don't add duplicate
    store.dispatch(addContextDocument('doc1'));
    expect(store.getState().chat.selectedContext.documentIds).toEqual(['doc1', 'doc2']);

    // Remove document
    store.dispatch(removeContextDocument('doc1'));
    expect(store.getState().chat.selectedContext.documentIds).toEqual(['doc2']);
  });

  it('should toggle useRag flag', () => {
    expect(store.getState().chat.selectedContext.useRag).toBe(true);

    store.dispatch(updateUseRag(false));
    expect(store.getState().chat.selectedContext.useRag).toBe(false);

    store.dispatch(updateUseRag(true));
    expect(store.getState().chat.selectedContext.useRag).toBe(true);
  });

  it('should clear all selected context', () => {
    // Set some context
    store.dispatch(setSelectedContext({
      sourceIds: ['source1'],
      documentIds: ['doc1'],
      useRag: false
    }));

    // Clear it
    store.dispatch(clearSelectedContext());
    expect(store.getState().chat.selectedContext).toEqual({
      sourceIds: [],
      documentIds: [],
      useRag: true
    });
  });
});