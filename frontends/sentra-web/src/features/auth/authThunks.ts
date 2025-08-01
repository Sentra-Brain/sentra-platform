// features/auth/authThunks.ts

import { createAsyncThunk } from '@reduxjs/toolkit'
import { userService } from '../../services/userService'
import type { User } from '../../models/user'
import type { RootState } from '../../store'

export const fetchCurrentUser = createAsyncThunk<User, void, { state: RootState }>(
  'auth/fetchCurrentUser',
  async (_, thunkAPI) => {
    const token = thunkAPI.getState().auth.token
    if (!token) throw new Error('No token available')
    const user = await userService.getCurrentUser()
    return user
  }
)
