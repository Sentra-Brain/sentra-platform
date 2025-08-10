// features/chat/components/WaitingForAnswer.tsx
export default function WaitingForAnswer() {
  return (
    <div key={Math.random()} className="rounded-xl px-4 py-3 max-w-[768px] bg-[var(--sentra-primary-light)] self-start">
      <div className="flex items-center space-x-2">
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>
    </div>
  )
}