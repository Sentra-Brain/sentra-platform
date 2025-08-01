import { createSlice } from '@reduxjs/toolkit'

const conversationSlice = createSlice({
  name: 'conversation',
  initialState: {
    list: [],
    selectedId: null,
  },
  reducers: {
    setConversations(state, action) {
      state.list = action.payload
    },
    selectConversation(state, action) {
      state.selectedId = action.payload
    },
  },
})

export const { setConversations, selectConversation } = conversationSlice.actions
export default conversationSlice.reducer
