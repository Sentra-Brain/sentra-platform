// src/features/auth/SessionInitializer.tsx
import { useEffect } from 'react'
import { useAuth } from './useAuth'

export default function SessionInitializer() {
  const { restoreSession } = useAuth()

  useEffect(() => {
    restoreSession()
  }, [])

  return null
}
