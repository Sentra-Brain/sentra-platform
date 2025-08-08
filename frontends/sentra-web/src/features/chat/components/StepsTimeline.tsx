import { useAppSelector } from '@store/hooks'

const StatusIcon = ({ status }: { status: 'running' | 'done' | 'error' }) => {
  switch (status) {
    case 'running':
      return <span className="text-blue-500">⏳</span>
    case 'done':
      return <span className="text-green-500">✅</span>
    case 'error':
      return <span className="text-red-500">❌</span>
    default:
      return null
  }
}

export default function StepsTimeline() {
  const steps = useAppSelector((state) => state.steps.steps)

  if (steps.length === 0) {
    return null
  }

  return (
    <div className="mb-4 space-y-2">
      {steps.map((step) => (
        <div
          key={step.id}
          className="flex items-center gap-2 p-2 bg-gray-50 rounded-md text-sm"
        >
          <StatusIcon status={step.status} />
          <span className="text-gray-700">
            {step.label}
            {step.status === 'done' && step.meta?.num_chunks && (
              <span className="text-gray-500 ml-1">
                (Found {step.meta.num_chunks} documents)
              </span>
            )}
          </span>
        </div>
      ))}
    </div>
  )
}