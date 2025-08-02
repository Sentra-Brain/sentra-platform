import { useState, useRef } from 'react'
import { Plus, Settings, Mic, Send, X, ChevronDown } from 'lucide-react'
import { useAppDispatch, useAppSelector } from '@store/hooks'
import {
  setStreaming,
  setWaitingForAnswer,
} from '@features/chat/chatSlice'
import { chatService } from './chatService'
import './MessageInput.css'

const MessageInput = () => {
  const [value, setValue] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const dispatch = useAppDispatch()
  const isStreaming = useAppSelector((s) => s.chat.isStreaming)
  const conversationId = useAppSelector(
    (s) => s.conversation.currentConversationId
  )

  const handleSend = async () => {
    const content = value.trim()
    if (!content || !conversationId || isStreaming) return

    dispatch(setStreaming(true))
    dispatch(setWaitingForAnswer(true))

    try {
      await chatService.sendMessageStream(
        { conversation_id: conversationId, content },
        (chunk) => {
          console.log('Received chunk:', chunk)
        },
        (error) => {
          console.error('Streaming error:', error)
        }
      )
      setValue('')
    } catch (err) {
      console.error('Failed to send message:', err)
      // optionally dispatch(setChatError(...))
    } finally {
      dispatch(setStreaming(false))
      dispatch(setWaitingForAnswer(false))
    }
  }

  const handleStop = () => {
    // TODO: add abort logic if needed
    dispatch(setStreaming(false))
  }

  const handleKeyDown = async (
    e: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      await handleSend()
    }
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    // TODO: Implement file upload
    e.target.value = ''
  }

  return (
    <div className="message-input-container">
      <button className="icon-btn" disabled title="Coming soon">
        <Plus size={18} />
      </button>

      <button className="icon-btn" disabled title="Tools (coming soon)">
        <Settings size={18} />
      </button>

      <div className="message-input-wrapper">
        <textarea
          className="message-input"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            conversationId
              ? 'Type a message...'
              : 'Ask anything to start a new conversation...'
          }
          rows={1}
          disabled={isStreaming}
        />
      </div>

      <input
        type="file"
        ref={fileInputRef}
        hidden
        onChange={handleFileUpload}
      />

      <button className="icon-btn" disabled title="Dictate (coming soon)">
        <Mic size={18} />
      </button>

      {isStreaming ? (
        <button className="icon-btn" onClick={handleStop} title="Stop">
          <X size={18} />
        </button>
      ) : (
        <button
          className="icon-btn send"
          onClick={handleSend}
          title="Send"
          disabled={!value.trim() || isStreaming}
        >
          <Send size={18} />
        </button>
      )}

      <button className="scroll-to-bottom-btn" title="Scroll to bottom">
        <ChevronDown size={20} />
      </button>
    </div>
  )
}

export default MessageInput
