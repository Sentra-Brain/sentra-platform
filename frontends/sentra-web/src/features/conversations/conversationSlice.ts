// src/features/conversations/conversationSlice.ts

import {
  createSlice,
  createAsyncThunk,
  type PayloadAction,
} from '@reduxjs/toolkit'
import { conversationService } from '../../services/conversationService'
import type {
  ConversationDetails,
  ConversationListItem,
  CreateConversationRequest,
} from '../../models/conversationModels'

interface ConversationsState {
  conversations: ConversationListItem[]
  currentConversationId: string | null
  
  selectedConversationDetails: ConversationDetails | null
  loading: boolean
  error: string | null
}

const initialState: ConversationsState = {
  conversations: [],
  currentConversationId: null,
  selectedConversationDetails: null,
  loading: false,
  error: null,
}

// 🔄 Fetch all conversations
export const fetchConversations = createAsyncThunk(
  'conversations/fetchAll',
  async () => {
    return await conversationService.list()
  }
)

// ➕ Create a new conversation
export const createConversation = createAsyncThunk(
  'conversations/create',
  async (data: CreateConversationRequest) => {
    return await conversationService.create(data)
  }
)

// 🔍 Fetch single conversation by ID
export const fetchConversationById = createAsyncThunk(
  'conversations/fetchById',
  async (id: string) => {
    return await conversationService.get(id)
  }
)


const conversationSlice = createSlice({
  name: 'conversations',
  initialState,
  reducers: {
    selectConversation(state, action: PayloadAction<string>) {
      state.currentConversationId = action.payload
    },
    clearConversation(state) {
      state.currentConversationId = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchConversations.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchConversations.fulfilled, (state, action) => {
        state.loading = false
        state.conversations = action.payload
      })
      .addCase(fetchConversations.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message ?? 'Error fetching conversations'
      })

      // fetchConversationById
      .addCase(fetchConversationById.pending, (state) => {
        state.loading = true
        state.selectedConversationDetails = null
      })
      .addCase(fetchConversationById.fulfilled, (state, action) => {
        state.loading = false
        state.selectedConversationDetails = action.payload
      })
      .addCase(fetchConversationById.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message ?? 'Error loading conversation'
      })



      .addCase(createConversation.fulfilled, (state, action) => {
        const newConv: ConversationListItem = {
          id: action.payload.id,
          title: 'Untitled',
          created_at: new Date().toISOString(), // temporary; ideally return full object
        }
        state.conversations.unshift(newConv)
        state.currentConversationId = newConv.id
      })
  },
})

export const { selectConversation, clearConversation } = conversationSlice.actions
export default conversationSlice.reducer
