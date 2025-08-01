// src/store/slices/authSlice.ts

import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

type AuthState = {
  token: string | null
  roles: string[]
}

const initialState: AuthState = {
  token: null,
  roles: [],
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginSuccess: (
      state,
      action: PayloadAction<{ token: string; roles: string[] }>
    ) => {
      state.token = action.payload.token
      state.roles = action.payload.roles
    },
    logout: (state) => {
      state.token = null
      state.roles = []
    },
  },
})

export const { loginSuccess, logout } = authSlice.actions
export default authSlice.reducer
