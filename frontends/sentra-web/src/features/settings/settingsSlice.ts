import { createSlice } from '@reduxjs/toolkit'

const settingsSlice = createSlice({
  name: 'settings',
  initialState: {
    orgName: '',
    maintenanceMode: false,
  },
  reducers: {
    setOrgName(state, action) {
      state.orgName = action.payload
    },
    toggleMaintenance(state) {
      state.maintenanceMode = !state.maintenanceMode
    },
  },
})

export const { setOrgName, toggleMaintenance } = settingsSlice.actions
export default settingsSlice.reducer
