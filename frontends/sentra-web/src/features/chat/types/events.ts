// src/features/chat/types/events.ts

// METADATA TYPES FOR CHAT EVENTS

export type StepStartMeta = {
  stage?: string;
  [key: string]: unknown;
};

export type StepProgressMeta = {
  progress?: number;
  stage?: string;
  [key: string]: unknown;
};

export type StepEndMeta = {
  chunks_found?: number;
  source_ids?: string[];
  document_ids?: string[];
};

export type MessageDeltaEvent = {
  event_id: string;
  type: "message_delta";
  content: string;
  timestamp: string;
};

export type StepErrorMeta = {
  error?: string;
  code?: string;
  [key: string]: unknown;
};

export type ToolCallEvent = {
  event_id: string;
  type: "tool_call";
  label?: string;
  content?: string;
  timestamp: string;
};

export type UserMessageEvent = {
  event_id: string;
  type: "user_message";
  content: string;
  timestamp: string;
};

// Chat event types

export type MessageFinalEvent = {
  event_id: string;
  type: "message_final";
  content?: string;
  timestamp: string;
};

export type StepStartEvent = {
  event_id: string;
  type: "step_start";
  task_type?: string;
  task_run_id?: string;
  step_id?: string;
  label?: string;
  status?: string;
  content?: string;
  meta?: StepStartMeta;
  timestamp: string;
};

export type StepEndEvent = {
  event_id: string;
  type: "step_end";
  task_type?: string;
  task_run_id?: string;
  step_id?: string;
  label?: string;
  status?: string;
  content?: string;
  meta?: StepEndMeta;
  timestamp: string;
};


export type StepProgressEvent = {
  event_id: string;
  type: "step_progress";
  task_type?: string;
  task_run_id?: string;
  step_id?: string;
  label?: string;
  status?: string;
  content?: string;
  meta?: StepProgressMeta;
  timestamp: string;
};

export type StepErrorEvent = {
  event_id: string;
  type: "step_error";
  task_type?: string;
  task_run_id?: string;
  step_id?: string;
  label?: string;
  status?: string;
  content?: string;
  meta?: StepErrorMeta;
  timestamp: string;
};

export type SentraEvent =
  | MessageDeltaEvent
  | MessageFinalEvent
  | StepStartEvent
  | StepEndEvent
  | StepProgressEvent
  | StepErrorEvent
  | ToolCallEvent
  | UserMessageEvent;

