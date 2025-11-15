// Test for session creation and rendering flow fixes
import { describe, it, expect } from "vitest";
import { configureStore } from "@reduxjs/toolkit";
import eventsReducer, {
  setWaitingForAnswer,
  addEvent,
  selectRenderableEvents,
} from "../src/features/chat/eventsSlice";
import { EventType } from "@ag-ui/core";
import conversationReducer, {
  updateConversationTitle,
} from "../src/features/conversations/conversationsSlice";

describe("Session Creation and Rendering Flow Fixes", () => {
  it("should update session title in Redux state", () => {
    const store = configureStore({
      reducer: {
        conversation: conversationReducer,
      },
      preloadedState: {
        conversation: {
          conversations: [
            { id: "test-conv-1", title: "Untitled", created_at: "2025-01-01" },
          ],
          currentConversationId: null,
          selectedConversationDetails: null,
          loadingList: false,
          loadingConversation: false,
          error: null,
        },
      },
    });

    // Simulate title update after LLM generation
    store.dispatch(
      updateConversationTitle({
        id: "test-conv-1",
        title: "Updated LLM Generated Title",
      })
    );

    const state = store.getState();
    const session = state.conversation.conversations.find((c) => c.id === "test-conv-1");

    expect(session?.title).toBe("Updated LLM Generated Title");
  });

  it("should handle waiting for answer state correctly", () => {
    const store = configureStore({
      reducer: {
        events: eventsReducer,
      },
    });

    // Initially not waiting
    expect(store.getState().events.waitingForAnswer).toBe(false);

    // Set waiting for answer
    store.dispatch(setWaitingForAnswer(true));
    expect(store.getState().events.waitingForAnswer).toBe(true);

    // Clear waiting state
    store.dispatch(setWaitingForAnswer(false));
    expect(store.getState().events.waitingForAnswer).toBe(false);
  });

  it("should aggregate chat messages for rendering", () => {
    const store = configureStore({
      reducer: {
        events: eventsReducer,
      },
    });

    store.dispatch(
      addEvent({
        type: EventType.TEXT_MESSAGE_START,
        messageId: "evt-1",
        role: "user",
      })
    );
    store.dispatch(
      addEvent({
        type: EventType.TEXT_MESSAGE_CONTENT,
        messageId: "evt-1",
        delta: "Test message",
      })
    );
    store.dispatch(
      addEvent({
        type: EventType.TEXT_MESSAGE_END,
        messageId: "evt-1",
      })
    );

    const renderable = selectRenderableEvents(store.getState());
    expect(renderable).toHaveLength(1);
    expect(renderable[0]).toMatchObject({
      id: "evt-1",
      type: "final",
      content: "Test message",
      role: "user",
    });
  });
});
