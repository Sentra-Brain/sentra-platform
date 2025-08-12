// src/features/chat/steps/StepsTimeline.tsx
import { useAppSelector, useAppDispatch } from '@store/hooks'
import { selectStepsByOrder, toggleStepOpen } from './stepsSlice'
import StepPanel from './StepPanel'

interface StepsTimelineProps {
  conversationId: string
}

export default function StepsTimeline({ conversationId }: StepsTimelineProps) {
  const dispatch = useAppDispatch()
  const steps = useAppSelector(state => selectStepsByOrder(state, conversationId))

  if (steps.length === 0) {
    return null
  }

  return (
    <div className="space-y-2 mb-4">
      {steps.map(step => (
        <StepPanel
          key={step.taskRunId}
          entry={step}
          onToggle={(isOpen) => {
            dispatch(toggleStepOpen({
              conversationId,
              taskRunId: step.taskRunId,
              isOpen
            }))
          }}
        />
      ))}
    </div>
  )
}