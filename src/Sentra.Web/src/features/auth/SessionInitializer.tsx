import { useEffect } from 'react'
import { useAuth } from './useAuth'

export default function SessionInitializer() {
  const { restoreSession } = useAuth()

  useEffect(() => {
    // Ensure restoreSession is awaited
    (async () => {
      await restoreSession()
    })()
  }, [])

  return null
}