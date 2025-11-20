// src/features/agents/types/agentModels.ts
export interface AgentInfo {
  key: string;
  name: string;
  description?: string;
  model_id?: string;
  instructions?: string;
}

export interface AgentListResponse {
  agents: AgentInfo[];
}