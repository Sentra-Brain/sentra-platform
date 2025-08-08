// sentra-web/src/features/chat/chatService.ts
import { tokenStorage } from "@shared/utils/tokenStorage";

type ChatSendPayload = {
  user_id?: string;
  conversation_id: string;
  message_id: string;
  response_message_id: string;
  content: string;
  context_source_ids?: string[];
  context_document_ids?: string[];
};

type StreamedMessage = {
  role: "assistant";
  content: string;
  final: boolean;
};

type ConversationEvent = {
  type: "message_delta" | "message_final" | "step_start" | "step_progress" | "step_end" | "step_error";
  step_id?: string;
  label?: string;
  status?: string;
  content?: string;
  meta?: any;
  timestamp?: string;
};

type OnMessageCallback = (chunk: StreamedMessage) => void;
type OnStepCallback = (event: ConversationEvent) => void;
type OnErrorCallback = (error: Error) => void;

export const chatService = {
  sendMessageStream(
    payload: ChatSendPayload,
    onMessage: OnMessageCallback,
    onStep?: OnStepCallback,
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
              const event: ConversationEvent = JSON.parse(json);
              
              // Route message_* events to existing chat message logic
              if (event.type === "message_delta" || event.type === "message_final") {
                const messageEvent: StreamedMessage = {
                  role: "assistant",
                  content: event.content || "",
                  final: event.type === "message_final"
                };
                onMessage(messageEvent);
              }
              
              // Route step_* events to steps callback
              if ((event.type === "step_start" || event.type === "step_progress" || 
                   event.type === "step_end" || event.type === "step_error") && onStep) {
                onStep(event);
              }
            } catch (err) {
              // Fallback: try to parse as old StreamedMessage format for backward compatibility
              try {
                const parsed: StreamedMessage = JSON.parse(json);
                onMessage(parsed);
              } catch (fallbackErr) {
                console.error("Failed to parse JSON chunk:", json, err);
              }
            }
          }
        }
      })
      .catch((err) => {
        if (onError && !controller.signal.aborted) {
          onError(err);
        }
      });

    return () => controller.abort();
  },
};
