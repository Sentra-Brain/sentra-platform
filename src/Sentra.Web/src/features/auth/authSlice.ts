// src/store/slices/authSlice.ts
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { User } from "../user/types/user";

type AuthState = {
  token: string | null;
  roles: string[];
  user: User | null;
  rehydrated: boolean;
};

const initialState: AuthState = {
  token: null,
  roles: [],
  user: null,
  rehydrated: false,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    loginSuccess: (
      state,
      action: PayloadAction<{ token: string; roles: string[]; user: User }>
    ) => {
      state.token = action.payload.token;
      state.roles = action.payload.roles;
      state.user = action.payload.user;
      state.rehydrated = true;
    },

    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
    },
    logout: (state) => {
      state.token = null;
      state.roles = [];
      state.user = null;
      state.rehydrated = false;
    },
    markRehydrated: (state) => {
      state.rehydrated = true;
    },
  },
});

export const { loginSuccess, logout, markRehydrated, setUser } =
  authSlice.actions;
export default authSlice.reducer;
