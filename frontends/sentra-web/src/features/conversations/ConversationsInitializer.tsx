import { useEffect } from 'react'
import { useConversations } from './useConversations' 

export default function ConversationsInitializer() {
  const { loadConversations } = useConversations()

  useEffect(() => {
    loadConversations()
  }, [])

  return null
}
