import { useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useConversations } from '../../hooks/useConversations'

export default function ChatPage() {
  const { id } = useParams<{ id: string }>()
  const {
    selectedConversationDetails,
    loadConversationDetails,
    loadingConversation,
    error,
  } = useConversations()

  // 🧠 Load full conversation when an ID is present
  useEffect(() => {
    if (id) {
      loadConversationDetails(id)
    }
  }, [id])

  // === Render logic ===

  if (loadingConversation) {
    return (
      <div className="p-4 text-sm text-gray-400">
        Loading conversation...
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 text-sm text-red-400">
        {error}
      </div>
    )
  }

  if (!id) {
    return (
      <div className="p-4 text-gray-400 italic">
        Start a new conversation...
      </div>
    )
  }

  if (!selectedConversationDetails) {
    return (
      <div className="p-4 text-sm text-gray-400">
        Conversation not loaded.
      </div>
    )
  }

  return (
    <div className="p-4">
      <h1 className="text-xl font-semibold mb-4">
        💬 Chat: {selectedConversationDetails.title}
      </h1>

      <pre className="bg-sentra-primary-dark text-sm p-4 rounded shadow-inner overflow-x-auto">
        {JSON.stringify(selectedConversationDetails, null, 2)}
      </pre>
    </div>
  )
}
