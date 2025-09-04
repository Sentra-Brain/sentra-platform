// src/services/sessionService.ts

import apiClient from "@shared/api/apiClient";
import type {
  SessionListItem,
  SessionDetails,
  CreateSessionRequest,
  CreateSessionResponse,
  UpdateSessionRequest,
  UpdateSessionResponse,
  DeleteSessionResponse,
} from "./types/sessionModels";

export const sessionService = {
  list(): Promise<SessionListItem[]> {
    return apiClient.get("/sessions/").then((res) => res.data);
  },

  create(data: CreateSessionRequest): Promise<CreateSessionResponse> {
    return apiClient.post("/sessions/", data).then((res) => res.data);
  },

  get(id: string): Promise<SessionDetails> {
    return apiClient.get(`/sessions/${id}`).then((res) => res.data);
  },

  update(
    id: string,
    data: UpdateSessionRequest
  ): Promise<UpdateSessionResponse> {
    return apiClient.put(`/sessions/${id}`, data).then((res) => res.data);
  },

  generateTitle(sessionId: string): Promise<UpdateSessionResponse> {
    return apiClient
      .patch(`/sessions/${sessionId}/title`)
      .then((res) => res.data);
  },

  remove(id: string): Promise<DeleteSessionResponse> {
    return apiClient.delete(`/sessions/${id}`).then((res) => res.data);
  },
};
