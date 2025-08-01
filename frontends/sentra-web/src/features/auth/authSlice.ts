// src/store/slices/authSlice.ts

import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

type AuthState = {
  token: string | null
  roles: string[]
  rehydrated: boolean 
}

const initialState: AuthState = {
  token: null,
  roles: [],
  rehydrated: false, 
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
      state.rehydrated = true // Mark as rehydrated after login
    },
    logout: (state) => {
      state.token = null
      state.roles = []
      state.rehydrated = false // Mark as not rehydrated after logout
    },    
    markRehydrated: (state) => {
      state.rehydrated = true
    }
  },
})

export const { loginSuccess, logout, markRehydrated } = authSlice.actions
export default authSlice.reducer
