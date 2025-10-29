import { createSlice, createAsyncThunk, type PayloadAction } from "@reduxjs/toolkit";
import { agentsService } from "./agentsService";
import type { AgentInfo } from "./types/agentModels";

export interface AgentsState {
  agents: AgentInfo[];
  loading: boolean;
  error: string | null;
  selected?: AgentInfo | null;
}

const initialState: AgentsState = {
  agents: [],
  loading: false,
  error: null,
  selected: null,
};

// ─────────────────────────────────────────────
// Async thunk: load agents from API
// ─────────────────────────────────────────────
export const fetchAgents = createAsyncThunk("agents/fetch", async () => {
  const res = await agentsService.listAgents();
  return res.agents;
});

// ─────────────────────────────────────────────
// Slice definition
// ─────────────────────────────────────────────
const agentsSlice = createSlice({
  name: "agents",
  initialState,
  reducers: {
    selectAgent(state, action: PayloadAction<AgentInfo | null>) {
      state.selected = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAgents.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAgents.fulfilled, (state, action) => {
        state.loading = false;
        state.agents = action.payload;

        // Auto-select default agent if none selected
        if (!state.selected && action.payload.length > 0) {
          const defaultAgent =
            action.payload.find((a) => a.key === "default_agent") || action.payload[0];
          state.selected = defaultAgent;
        }
      })
      .addCase(fetchAgents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to load agents";
      });
  },
});

export const { selectAgent } = agentsSlice.actions;
export default agentsSlice.reducer;
