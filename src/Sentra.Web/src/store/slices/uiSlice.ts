// src/store/slices/uiSlice.ts

import { createSlice } from '@reduxjs/toolkit'

type UIState = {
  isSidebarCollapsed: boolean
  theme: 'light' | 'dark'
}

const initialState: UIState = {
  isSidebarCollapsed: false,
  theme: 'dark' // default theme
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.isSidebarCollapsed = !state.isSidebarCollapsed
    },
    toggleTheme: (state) => {
      state.theme = state.theme === 'dark' ? 'light' : 'dark'
    }
  }
})

export const { toggleSidebar, toggleTheme } = uiSlice.actions
export default uiSlice.reducer
