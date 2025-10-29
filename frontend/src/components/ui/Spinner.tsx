import React from 'react'
import { Loader2 } from 'lucide-react'
import { clsx } from 'clsx'

export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
  label?: string
}

export function Spinner({ size = 'md', className, label }: SpinnerProps) {
  const sizeStyles = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12',
  }

  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <Loader2
        className={clsx('animate-spin text-primary-600 dark:text-primary-400', sizeStyles[size], className)}
      />
      {label && (
        <p className="text-sm text-gray-600 dark:text-gray-400">{label}</p>
      )}
    </div>
  )
}

// Full page loading spinner
export function PageSpinner({ label = 'Loading...' }: { label?: string }) {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <Spinner size="xl" label={label} />
    </div>
  )
}
