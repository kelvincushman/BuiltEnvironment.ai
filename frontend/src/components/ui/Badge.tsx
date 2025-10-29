import React from 'react'
import { clsx } from 'clsx'

export interface BadgeProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'gray'
  size?: 'sm' | 'md' | 'lg'
  dot?: boolean
  className?: string
}

export function Badge({
  children,
  variant = 'primary',
  size = 'md',
  dot = false,
  className,
}: BadgeProps) {
  const variantStyles = {
    primary: 'bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300',
    secondary: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
    success: 'bg-secondary-100 text-secondary-800 dark:bg-secondary-900/30 dark:text-secondary-300',
    warning: 'bg-accent-100 text-accent-800 dark:bg-accent-900/30 dark:text-accent-300',
    danger: 'bg-danger-100 text-danger-800 dark:bg-danger-900/30 dark:text-danger-300',
    gray: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
  }

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-0.5 text-xs',
    lg: 'px-3 py-1 text-sm',
  }

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 rounded-full font-medium',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {dot && (
        <span
          className={clsx(
            'h-1.5 w-1.5 rounded-full',
            variant === 'primary' && 'bg-primary-600 dark:bg-primary-400',
            variant === 'secondary' && 'bg-gray-600 dark:bg-gray-400',
            variant === 'success' && 'bg-secondary-600 dark:bg-secondary-400',
            variant === 'warning' && 'bg-accent-600 dark:bg-accent-400',
            variant === 'danger' && 'bg-danger-600 dark:bg-danger-400',
            variant === 'gray' && 'bg-gray-500 dark:bg-gray-400'
          )}
        />
      )}
      {children}
    </span>
  )
}

// Compliance badges with traffic light colors
export interface ComplianceBadgeProps {
  status: 'green' | 'amber' | 'red' | 'gray'
  children: React.ReactNode
  className?: string
}

export function ComplianceBadge({ status, children, className }: ComplianceBadgeProps) {
  const statusStyles = {
    green: 'bg-compliance-green/10 text-compliance-green border border-compliance-green/20',
    amber: 'bg-compliance-amber/10 text-compliance-amber border border-compliance-amber/20',
    red: 'bg-compliance-red/10 text-compliance-red border border-compliance-red/20',
    gray: 'bg-compliance-gray/10 text-compliance-gray border border-compliance-gray/20',
  }

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium',
        statusStyles[status],
        className
      )}
    >
      <span
        className={clsx(
          'h-2 w-2 rounded-full',
          status === 'green' && 'bg-compliance-green',
          status === 'amber' && 'bg-compliance-amber',
          status === 'red' && 'bg-compliance-red',
          status === 'gray' && 'bg-compliance-gray'
        )}
      />
      {children}
    </span>
  )
}
