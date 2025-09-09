// sentra-web/src/features/chat/chatService.ts
import { tokenStorage } from "@shared/utils/tokenStorage";
import type { Event } from "@features/chat/types/events";
import type { ConversationMode } from "@features/chat/types/mode";

  type ChatSendPayload = {
    user_id?: string;
    session_id: string;
    id: string;
    response_id: string;
    content: string;
    context_source_ids?: string[];
    context_document_ids?: string[];
    mode?: ConversationMode;
  };

  // NEW: event callback uses Event
  type OnEventCallback = (event: Event) => void;
type OnErrorCallback = (error: Error) => void;

export const chatService = {
  sendMessageStream(
    payload: ChatSendPayload,
    onEvent: OnEventCallback,
    onError?: OnErrorCallback
  ): () => void {
    const token = tokenStorage.getAccessToken();
    const controller = new AbortController();

    const url = `${
      import.meta.env.VITE_API_URL || "http://127.0.0.1:8100"
    }/chat/send`;

    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok || !response.body) {
          throw new Error(`HTTP error ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            const clean = line.trim();
            if (!clean.startsWith("data:")) continue;

            const json = clean.slice(5).trim();
            if (!json) continue;

            try {
                const evt: Event = JSON.parse(json);
                onEvent(evt);
            } catch (err) {
              console.error("Failed to parse Event:", json, err);
            }
          }
        }
      })
      .catch((err) => {
        if (onError && !controller.signal.aborted) onError(err);
      });

    return () => controller.abort();
  },
};
