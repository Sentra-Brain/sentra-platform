import type { Role, TextMessageContentEvent, TextMessageEndEvent, TextMessageStartEvent } from "@ag-ui/core";
import { EventType } from "@ag-ui/core";

export type CompletedMessageEventTuple = [
  TextMessageStartEvent,
  TextMessageContentEvent,
  TextMessageEndEvent,
];
export function createCompletedMessageEvents(
  messageId: string,
  role: Role,
  content: string,
  timestamp?: number
): CompletedMessageEventTuple {
  const safeRole: Role = 
    role === "user" || role === "assistant" || role === "system" || role === "developer"
      ? role
      : "assistant";

  const start: TextMessageStartEvent = {
    type: EventType.TEXT_MESSAGE_START,
    messageId,
    role: safeRole,
    timestamp,
  };

  const contentEvent: TextMessageContentEvent = {
    type: EventType.TEXT_MESSAGE_CONTENT,
    messageId,
    delta: content,
    timestamp,
  };

  const end: TextMessageEndEvent = {
    type: EventType.TEXT_MESSAGE_END,
    messageId,
    timestamp,
  };

  return [start, contentEvent, end];
}
