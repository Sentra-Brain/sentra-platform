// src/components/SessionInitializer.tsx
import { useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'

export default function SessionInitializer() {
  const { restoreSession } = useAuth()

  useEffect(() => {
    restoreSession()
  }, [])

  return null
}
