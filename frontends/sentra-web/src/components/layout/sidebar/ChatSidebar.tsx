import SidebarSection from './Shared/SidebarSection'
import SidebarItem from './Shared/SidebarItem'
import { PlusCircle, MessageSquare } from 'lucide-react'
import { useConversations } from '../../../hooks/useConversations'
import { useNavigate, useLocation } from 'react-router-dom'

export default function ChatSidebar() {
  const {
    conversations,
    currentConversationId,
    select,
    clear,
    loading,
  } = useConversations()

  const navigate = useNavigate()
  const { pathname } = useLocation()

  const handleNewChat = () => {
    // If we're already in `/c`, just reset state
    if (pathname === '/c') {
      clear()
      // Input and UI will already react to this
    } else {
      clear()
      navigate('/c')
    }
  }

  const handleSelect = (id: string) => {
    select(id)
    navigate(`/c/${id}`)
  }

  return (
    <SidebarSection title="Conversations">
      <SidebarItem
        icon={PlusCircle}
        label="New chat"
        onClick={handleNewChat}
      />

      {loading && (
        <div className="px-3 py-2 text-sm text-gray-400">Loading...</div>
      )}

      {conversations.map((conv) => (
        <SidebarItem
          key={conv.id}
          label={conv.title || 'Untitled'}
          onClick={() => handleSelect(conv.id)}
          icon={MessageSquare}
          active={conv.id === currentConversationId}
        />
      ))}
    </SidebarSection>
  )
}
