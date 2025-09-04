import { useEffect } from 'react'
import { useSessions } from './useSessions'

export default function SessionsInitializer() {
  const { loadSessions } = useSessions()

  useEffect(() => {
    loadSessions()
  }, [])

  return null
}
