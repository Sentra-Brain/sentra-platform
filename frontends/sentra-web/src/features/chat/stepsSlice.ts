// src/features/chat/stepsSlice.ts
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
    stepStarted(state, action: PayloadAction<{ id: string; label: string }>) {
      const { id, label } = action.payload;
      const existingStep = state.steps.find(step => step.id === id);
      if (existingStep) {
        existingStep.status = 'running';
        existingStep.label = label;
      } else {
        state.steps.push({
          id,
          label,
          status: 'running'
        });
      }
    },
    stepUpdated(state, action: PayloadAction<{ id: string; status: 'running' | 'done' | 'error'; meta?: any }>) {
      const { id, status, meta } = action.payload;
      const step = state.steps.find(step => step.id === id);
      if (step) {
        step.status = status;
        if (meta) {
          step.meta = meta;
        }
      }
    },
    clearSteps(state) {
      state.steps = [];
    },
  },
});

export const {
  stepStarted,
  stepUpdated,
  clearSteps,
} = stepsSlice.actions;

export default stepsSlice.reducer;