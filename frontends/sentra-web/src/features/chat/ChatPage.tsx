// features/chat/ChatPage.tsx
import { useAppSelector } from '@store/hooks'
import ChatHeader from './components/ChatHeader'
import ChatContent from './components/ChatContent'
import ChatFooter from './components/ChatFooter'
import ChatInputContainer from './components/ChatInputContainer'

import { useEffect } from 'react'
import { useAppDispatch } from '@store/hooks'
import { fetchConversationById } from '@features/conversations/conversationSlice'


export default function ChatPage() {
  const dispatch = useAppDispatch()
  const currentConversationId = useAppSelector(
    (state) => state.conversation.currentConversationId
  )

  useEffect(() => {
    if (currentConversationId) {
      dispatch(fetchConversationById(currentConversationId))
    }
  }, [currentConversationId, dispatch])

  const isConversationActive = !!currentConversationId

  return (
    <div className="flex flex-col h-full w-full">
      {isConversationActive ? (
        <>
          <ChatHeader />
          <ChatContent />
          <ChatFooter>
            <ChatInputContainer />
          </ChatFooter>
        </>
      ) : (
        <div className="flex-1 flex items-center justify-center px-4">
          <ChatInputContainer />
        </div>
      )}
    </div>
  )
}
