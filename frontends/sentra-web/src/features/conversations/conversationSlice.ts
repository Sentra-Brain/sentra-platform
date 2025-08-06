// src/features/conversations/conversationSlice.ts

import {
  createSlice,
  createAsyncThunk,
  type PayloadAction,
} from '@reduxjs/toolkit'
import { conversationService } from './conversationService'
import type {
  ConversationDetails,
  ConversationListItem,
  CreateConversationRequest,
} from './types/conversationModels'

interface ConversationsState {
  conversations: ConversationListItem[]
  currentConversationId: string | null
  
  selectedConversationDetails: ConversationDetails | null
  loadingList: boolean // for conversation list  
  loadingConversation: boolean // for chat page
  error: string | null
}

const initialState: ConversationsState = {
  conversations: [],
  currentConversationId: null,
  selectedConversationDetails: null,
  loadingList: false,
  loadingConversation: false, // for chat page
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
    updateConversationTitle(state, action: PayloadAction<{ id: string; title: string }>) {
      const conversation = state.conversations.find(conv => conv.id === action.payload.id)
      if (conversation) {
        conversation.title = action.payload.title
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchConversations.pending, (state) => {
        state.loadingList = true
        state.error = null
      })
      .addCase(fetchConversations.fulfilled, (state, action) => {
        state.loadingList = false
        state.conversations = action.payload
      })
      .addCase(fetchConversations.rejected, (state, action) => {
        state.loadingList = false
        state.error = action.error.message ?? 'Error fetching conversations'
      })

      // fetchConversationById
      .addCase(fetchConversationById.pending, (state) => {
        state.loadingConversation = true
        state.selectedConversationDetails = null
      })
      .addCase(fetchConversationById.fulfilled, (state, action) => {
        state.loadingConversation = false
        state.selectedConversationDetails = action.payload
      })
      .addCase(fetchConversationById.rejected, (state, action) => {
        state.loadingConversation = false
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

export const { selectConversation, clearConversation, updateConversationTitle } = conversationSlice.actions
export default conversationSlice.reducer
