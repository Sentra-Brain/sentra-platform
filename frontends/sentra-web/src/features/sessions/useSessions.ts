import { useAppDispatch, useAppSelector } from '@store/hooks'
import {
  fetchSessions,
  fetchSessionById,
  selectSession,
  clearSession,
  createSession,
} from './sessionsSlice'

export function useSessions() {
  const dispatch = useAppDispatch()
  const {
    sessions,
    currentSessionId,
    selectedSessionDetails,
    loadingList,
    loadingSession,
    error,
  } = useAppSelector((state) => state.session)

  return {
    sessions,
    currentSessionId,
    selectedSessionDetails,
    loadingList,
    loadingSession,
    error,
    loadSessions: () => dispatch(fetchSessions()),
    loadSessionDetails: (id: string) => dispatch(fetchSessionById(id)),
    select: (id: string) => dispatch(selectSession(id)),
    clear: () => dispatch(clearSession()),
    create: (initial_prompt?: string) =>
      dispatch(createSession({ initial_prompt: initial_prompt ?? '' })),
  }
}
