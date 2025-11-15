import { HttpAgent } from "@ag-ui/client";
import type { BaseEvent as AGUIEvent, RunAgentInput } from "@ag-ui/core";
import { tokenStorage } from "@shared/utils/tokenStorage";
import { v4 as uuidv4 } from "uuid";

type ChatSendPayload = {
  threadId: string;
  messageId: string;
  content: string;
  contextSourceIds: string[];
  contextDocumentIds: string[];
  mode: string;
  agent?: string;
};

type OnEventCallback = (event: AGUIEvent) => void;
type OnErrorCallback = (error: Error) => void;

const apiBaseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8100";

export const chatService = {
  sendMessageStream(
    payload: ChatSendPayload,
    onEvent: OnEventCallback,
    onError?: OnErrorCallback
  ): () => void {
    const token = tokenStorage.getAccessToken();

    const agent = new HttpAgent({
      url: `${apiBaseUrl}/chat/agui/stream`,
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      threadId: payload.threadId,
    });

    const runInput: RunAgentInput = {
      threadId: payload.threadId,
      runId: uuidv4(), // ✅ required
      messages: [
        {
          id: payload.messageId,
          role: "user",
          content: payload.content,
        },
      ],
      tools: [], // ✅ required (even if not used)
      context: [], // ✅ required (even if empty)
      forwardedProps: {
        mode: payload.mode,
        agent: payload.agent,
        context_source_ids: payload.contextSourceIds,
        context_document_ids: payload.contextDocumentIds,
      },
    };

    const subscription = agent.run(runInput).subscribe({
      next: onEvent,
      error: (err) => {
        const normalized = err instanceof Error ? err : new Error(String(err));
        onError?.(normalized);
      },
    });

    return () => {
      subscription.unsubscribe();
      agent.abortRun();
    };
  },
};
