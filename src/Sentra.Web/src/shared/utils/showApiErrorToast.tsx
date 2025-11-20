// src/utils/showApiErrorToast.tsx
import { toast } from 'react-toastify'
import type { SentraApiError } from '../models/apiError'

export const showApiErrorToast = (error: SentraApiError) => {
  const title = error.error.message || 'Unexpected error'
  const description = error.error.details ?? null

  toast.error(
    <div>
      <p className="font-semibold text-sm">{title}</p>
      {description && <p className="text-xs opacity-80 mt-1">{description}</p>}
    </div>,
    { autoClose: 8000 }
  )
}
