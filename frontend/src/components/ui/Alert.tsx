import React from 'react'
import { AlertCircle, CheckCircle, Info, XCircle, X } from 'lucide-react'
import { clsx } from 'clsx'

export interface AlertProps {
  variant?: 'info' | 'success' | 'warning' | 'danger'
  title?: string
  children: React.ReactNode
  onClose?: () => void
  className?: string
}

export function Alert({
  variant = 'info',
  title,
  children,
  onClose,
  className,
}: AlertProps) {
  const variantConfig = {
    info: {
      container: 'bg-primary-50 border-primary-200 dark:bg-primary-950 dark:border-primary-800',
      icon: Info,
      iconColor: 'text-primary-600 dark:text-primary-400',
      title: 'text-primary-900 dark:text-primary-100',
      text: 'text-primary-800 dark:text-primary-200',
    },
    success: {
      container: 'bg-secondary-50 border-secondary-200 dark:bg-secondary-950 dark:border-secondary-800',
      icon: CheckCircle,
      iconColor: 'text-secondary-600 dark:text-secondary-400',
      title: 'text-secondary-900 dark:text-secondary-100',
      text: 'text-secondary-800 dark:text-secondary-200',
    },
    warning: {
      container: 'bg-accent-50 border-accent-200 dark:bg-accent-950 dark:border-accent-800',
      icon: AlertCircle,
      iconColor: 'text-accent-600 dark:text-accent-400',
      title: 'text-accent-900 dark:text-accent-100',
      text: 'text-accent-800 dark:text-accent-200',
    },
    danger: {
      container: 'bg-danger-50 border-danger-200 dark:bg-danger-950 dark:border-danger-800',
      icon: XCircle,
      iconColor: 'text-danger-600 dark:text-danger-400',
      title: 'text-danger-900 dark:text-danger-100',
      text: 'text-danger-800 dark:text-danger-200',
    },
  }

  const config = variantConfig[variant]
  const Icon = config.icon

  return (
    <div
      className={clsx(
        'flex gap-3 p-4 rounded-lg border',
        config.container,
        className
      )}
      role="alert"
    >
      <div className="flex-shrink-0">
        <Icon className={clsx('h-5 w-5', config.iconColor)} />
      </div>

      <div className="flex-1 space-y-1">
        {title && (
          <h4 className={clsx('font-semibold text-sm', config.title)}>{title}</h4>
        )}
        <div className={clsx('text-sm', config.text)}>{children}</div>
      </div>

      {onClose && (
        <button
          onClick={onClose}
          className={clsx(
            'flex-shrink-0 p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 transition-colors',
            config.iconColor
          )}
          aria-label="Close alert"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  )
}
