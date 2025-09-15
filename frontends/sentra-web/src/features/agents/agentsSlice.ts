import { createSlice, createAsyncThunk, type PayloadAction } from '@reduxjs/toolkit';
import apiClient from '@shared/api/apiClient';

export interface AgentsState {
  available: string[];
  loading: boolean;
  error: string | null;
  selected: string | null; // agent chosen for next new session
}

const initialState: AgentsState = {
  available: [],
  loading: false,
  error: null,
  selected: 'default_agent',
};

export const fetchAgents = createAsyncThunk('agents/fetch', async () => {
  const res = await apiClient.get('/agents');
  return res.data.agents as string[];
});

const agentsSlice = createSlice({
  name: 'agents',
  initialState,
  reducers: {
    selectAgent(state, action: PayloadAction<string>) {
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
        state.available = action.payload;
        if (!state.selected && action.payload.length > 0) {
          state.selected = action.payload.includes('default_agent') ? 'default_agent' : action.payload[0];
        }
      })
      .addCase(fetchAgents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to load agents';
      });
  },
});

export const { selectAgent } = agentsSlice.actions;
export default agentsSlice.reducer;
