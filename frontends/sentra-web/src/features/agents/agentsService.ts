import apiClient from "@shared/api/apiClient";
import type { AgentListResponse } from "./types/agentModels";

/**
 * Service for interacting with Sentra agents API.
 * Currently supports listing all registered agent templates.
 */
export const agentsService = {
  /**
   * Retrieve all available agents from the API.
   * Endpoint: GET /agents
   */
  listAgents(): Promise<AgentListResponse> {
    return apiClient.get("/agents").then((res) => res.data);
  },
};
