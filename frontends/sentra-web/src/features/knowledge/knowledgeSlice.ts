import { createSlice } from '@reduxjs/toolkit'

const knowledgeSlice = createSlice({
  name: 'knowledge',
  initialState: {
    sources: [],
    documents: [],
  },
  reducers: {
    setSources(state, action) {
      state.sources = action.payload
    },
    setDocuments(state, action) {
      state.documents = action.payload
    },
  },
})

export const { setSources, setDocuments } = knowledgeSlice.actions
export default knowledgeSlice.reducer
