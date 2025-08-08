// src/features/chat/components/StepsTimeline.tsx
import { useAppSelector } from '@store/hooks'

export function StepsTimeline() {
  const steps = useAppSelector(state => state.steps.steps)

  if (steps.length === 0) {
    return null
  }

  return (
    <div className="mb-4 p-3 bg-gray-50 rounded-lg border">
      <div className="text-sm text-gray-600 mb-2">Processing Steps</div>
      <div className="space-y-2">
        {steps.map((step) => (
          <div key={step.id} className="flex items-center gap-2 text-sm">
            <div className="flex-shrink-0">
              {step.status === 'running' && (
                <span className="text-blue-500" title="Running">⏳</span>
              )}
              {step.status === 'done' && (
                <span className="text-green-500" title="Completed">✅</span>
              )}
              {step.status === 'error' && (
                <span className="text-red-500" title="Error">❌</span>
              )}
            </div>
            <div className="flex-1">
              <span className="text-gray-800">{step.label}</span>
              {step.status === 'done' && step.meta?.num_chunks && (
                <span className="text-gray-500 ml-1">
                  (Found {step.meta.num_chunks} documents)
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}