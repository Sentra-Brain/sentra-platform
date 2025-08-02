import { useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useConversations } from '@features/conversations/useConversations'
import { useAppSelector } from '@store/hooks'
import MesssageInput from './MessageInput'
import './ChatPage.css'

export default function ChatPage() {
  const { id } = useParams<{ id: string }>()
  const {
    selectedConversationDetails,
    loadConversationDetails,
    loadingConversation,
    error,
  } = useConversations()

  const waitingForAnswer = useAppSelector((s) => s.chat.waitingForAnswer)
  const user = useAppSelector((s) => s.auth.user)

  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (id) loadConversationDetails(id)
  }, [id])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [selectedConversationDetails?.messages.length])

  const getFirstName = () => {
    if (user?.full_name) return user.full_name.split(' ')[0]
    if (user?.username) return user.username[0].toUpperCase() + user.username.slice(1)
    return 'there'
  }

  if (loadingConversation) {
    return <div className="p-4 text-sm text-[var(--sentra-neutral)]">Loading conversation...</div>
  }

  if (error) {
    return <div className="p-4 text-sm text-red-500">{error}</div>
  }

  if (!id || !selectedConversationDetails) {
    return (
      <div className="empty-state">
        <div className="empty-state-content">
          <h2>Welcome back, {getFirstName()}.</h2>
          <p>Ask anything to start a new conversation.</p>          
        </div>
      </div>
    )
  }

  const messages = selectedConversationDetails.messages

  return (
    <main className="chat-area">
      <div className="messages">
        {messages.map((msg) => (
          <div
            key={msg.timestamp.toString()}
            className={`message-bubble ${msg.role}`}
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {msg.content}
            </ReactMarkdown>
          </div>
        ))}

        {waitingForAnswer && (
          <div className="waiting-bubble">Waiting...</div>
        )}

        <div ref={endRef} />
        <MesssageInput />
      </div>
    </main>
  )
}
