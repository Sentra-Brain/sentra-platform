// src/features/chat/types/events.ts

export const SentraEventType = {
  MESSAGE_DELTA: 'message_delta',
  MESSAGE_FINAL: 'message_final',
  ERROR: 'error',
  AGENT_STARTED: 'agent_started',
  AGENT_COMPLETED: 'agent_completed',
  STEP_START: 'step_start',
  STEP_END: 'step_end',
  CONTEXT_BUILT: 'context_built',
  LLM_CALLED: 'llm_called',
} as const;

export type SentraEventType =
  typeof SentraEventType[keyof typeof SentraEventType];

export type SentraEventContentPart = {
  text?: string;
  function_call?: Record<string, unknown>;
  function_response?: Record<string, unknown>;
};

export type SentraEventContent = {
  role: string;
  parts: SentraEventContentPart[];
};

export interface BaseEvent {
  id: string;
  timestamp: string;
  author: string;
  task_run_id?: string;
  status?: string;
  meta?: Record<string, unknown>;
  content?: SentraEventContent;
}

export interface MessageDeltaEvent extends BaseEvent {
  type: typeof SentraEventType.MESSAGE_DELTA;
  content: SentraEventContent;
}

export interface MessageFinalEvent extends BaseEvent {
  type: typeof SentraEventType.MESSAGE_FINAL;
  content: SentraEventContent;
}

export interface ErrorEvent extends BaseEvent {
  type: typeof SentraEventType.ERROR;
}

export interface StepStartEvent extends BaseEvent {
  type: typeof SentraEventType.STEP_START;
}

export interface StepEndEvent extends BaseEvent {
  type: typeof SentraEventType.STEP_END;
}

export interface ContextBuiltEvent extends BaseEvent {
  type: typeof SentraEventType.CONTEXT_BUILT;
}

export interface LlmCalledEvent extends BaseEvent {
  type: typeof SentraEventType.LLM_CALLED;
}

export interface AgentStartedEvent extends BaseEvent {
  type: typeof SentraEventType.AGENT_STARTED;
}

export interface AgentCompletedEvent extends BaseEvent {
  type: typeof SentraEventType.AGENT_COMPLETED;
}

export type SentraEvent =
  | MessageDeltaEvent
  | MessageFinalEvent
  | ErrorEvent
  | StepStartEvent
  | StepEndEvent
  | ContextBuiltEvent
  | LlmCalledEvent
  | AgentStartedEvent
  | AgentCompletedEvent;
