// stepsSlice.ts
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

export interface Step {
  id: string;
  label: string;
  status: 'running' | 'done' | 'error';
  meta?: any;
}

interface StepsState {
  steps: Step[];
}

const initialState: StepsState = {
  steps: [],
};

const stepsSlice = createSlice({
  name: "steps",
  initialState,
  reducers: {
    stepStarted(state, action: PayloadAction<{stepId: string; label: string}>) {
      const { stepId, label } = action.payload;
      const existingIndex = state.steps.findIndex(step => step.id === stepId);
      
      if (existingIndex >= 0) {
        // Update existing step
        state.steps[existingIndex] = {
          id: stepId,
          label,
          status: 'running'
        };
      } else {
        // Add new step
        state.steps.push({
          id: stepId,
          label,
          status: 'running'
        });
      }
    },
    stepUpdated(state, action: PayloadAction<{stepId: string; status: 'running' | 'done' | 'error'; meta?: any}>) {
      const { stepId, status, meta } = action.payload;
      const step = state.steps.find(step => step.id === stepId);
      
      if (step) {
        step.status = status;
        if (meta !== undefined) {
          step.meta = meta;
        }
      }
    },
    clearSteps(state) {
      state.steps = [];
    },
  },
});

export const { stepStarted, stepUpdated, clearSteps } = stepsSlice.actions;
export default stepsSlice.reducer;