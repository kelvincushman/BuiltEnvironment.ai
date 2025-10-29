import React, { useState } from 'react'
import { Card, Button, Badge } from '@/components/ui'
import { GitBranch, Check, X, Eye, User, Clock } from 'lucide-react'

export interface Change {
  id: string
  type: 'insertion' | 'deletion' | 'formatting'
  author: string
  authorColor: string
  content: string
  originalContent?: string
  timestamp: string
  status: 'pending' | 'accepted' | 'rejected'
  location: string
}

interface TrackChangesProps {
  changes: Change[]
  onAcceptChange: (changeId: string) => void
  onRejectChange: (changeId: string) => void
  onAcceptAll: () => void
  onRejectAll: () => void
  isEnabled: boolean
  onToggle: () => void
  className?: string
}

export function TrackChanges({
  changes,
  onAcceptChange,
  onRejectChange,
  onAcceptAll,
  onRejectAll,
  isEnabled,
  onToggle,
  className = '',
}: TrackChangesProps) {
  const [filter, setFilter] = useState<'all' | 'pending' | 'accepted' | 'rejected'>('pending')

  const filteredChanges = changes.filter((change) => {
    if (filter === 'all') return true
    return change.status === filter
  })

  const pendingCount = changes.filter((c) => c.status === 'pending').length

  const getChangeIcon = (type: Change['type']) => {
    switch (type) {
      case 'insertion':
        return <span className="text-success-600 dark:text-success-400 font-bold">+</span>
      case 'deletion':
        return <span className="text-danger-600 dark:text-danger-400 font-bold">−</span>
      case 'formatting':
        return <span className="text-primary-600 dark:text-primary-400 font-bold">~</span>
    }
  }

  const getChangeLabel = (type: Change['type']) => {
    switch (type) {
      case 'insertion':
        return 'Added'
      case 'deletion':
        return 'Deleted'
      case 'formatting':
        return 'Formatted'
    }
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <GitBranch className="h-5 w-5 text-primary-600 dark:text-primary-400" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Track Changes
          </h3>
          {pendingCount > 0 && (
            <Badge variant="secondary" className="bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300">
              {pendingCount} pending
            </Badge>
          )}
        </div>
        <button
          onClick={onToggle}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            isEnabled
              ? 'bg-success-100 dark:bg-success-900/20 text-success-700 dark:text-success-300'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
          }`}
        >
          {isEnabled ? 'Enabled' : 'Disabled'}
        </button>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
        {(['all', 'pending', 'accepted', 'rejected'] as const).map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              filter === status
                ? 'border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
            {status === 'pending' && pendingCount > 0 && (
              <span className="ml-1 px-1.5 py-0.5 rounded-full bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 text-xs">
                {pendingCount}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Bulk actions */}
      {pendingCount > 0 && filter === 'pending' && (
        <div className="flex gap-2">
          <Button variant="success" size="sm" onClick={onAcceptAll}>
            Accept All ({pendingCount})
          </Button>
          <Button variant="danger" size="sm" onClick={onRejectAll}>
            Reject All
          </Button>
        </div>
      )}

      {/* Changes list */}
      <div className="space-y-3">
        {filteredChanges.length === 0 && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
            No {filter !== 'all' ? filter : ''} changes
          </div>
        )}

        {filteredChanges.map((change) => (
          <Card
            key={change.id}
            className={`border-l-4 ${
              change.type === 'insertion'
                ? 'border-l-success-500'
                : change.type === 'deletion'
                ? 'border-l-danger-500'
                : 'border-l-primary-500'
            }`}
          >
            <Card.Content className="p-4">
              <div className="flex items-start gap-3">
                {/* Change icon */}
                <div className="flex-shrink-0">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      change.type === 'insertion'
                        ? 'bg-success-100 dark:bg-success-900/20'
                        : change.type === 'deletion'
                        ? 'bg-danger-100 dark:bg-danger-900/20'
                        : 'bg-primary-100 dark:bg-primary-900/20'
                    }`}
                  >
                    {getChangeIcon(change.type)}
                  </div>
                </div>

                <div className="flex-1 min-w-0">
                  {/* Change header */}
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                          style={{
                            backgroundColor: `${change.authorColor}20`,
                            color: change.authorColor,
                          }}
                        >
                          <User className="h-3 w-3 mr-1" />
                          {change.author}
                        </span>
                        <Badge
                          variant="secondary"
                          className={
                            change.status === 'pending'
                              ? 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300'
                              : change.status === 'accepted'
                              ? 'bg-success-100 dark:bg-success-900/20 text-success-700 dark:text-success-300'
                              : 'bg-danger-100 dark:bg-danger-900/20 text-danger-700 dark:text-danger-300'
                          }
                        >
                          {change.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {getChangeLabel(change.type)} • {change.location} • {change.timestamp}
                      </p>
                    </div>

                    {change.status === 'pending' && (
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onAcceptChange(change.id)}
                          title="Accept change"
                          className="text-success-600 hover:text-success-700 hover:bg-success-50 dark:hover:bg-success-900/20"
                        >
                          <Check className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onRejectChange(change.id)}
                          title="Reject change"
                          className="text-danger-600 hover:text-danger-700 hover:bg-danger-50 dark:hover:bg-danger-900/20"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* Change content */}
                  <div className="space-y-2">
                    {change.type === 'deletion' && change.originalContent && (
                      <div className="p-2 bg-danger-50 dark:bg-danger-900/20 rounded">
                        <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                          Original:
                        </p>
                        <p className="text-sm text-danger-700 dark:text-danger-300 line-through">
                          {change.originalContent}
                        </p>
                      </div>
                    )}
                    {change.type === 'insertion' && (
                      <div className="p-2 bg-success-50 dark:bg-success-900/20 rounded">
                        <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                          New content:
                        </p>
                        <p className="text-sm text-success-700 dark:text-success-300">
                          {change.content}
                        </p>
                      </div>
                    )}
                    {change.type === 'formatting' && (
                      <div className="p-2 bg-primary-50 dark:bg-primary-900/20 rounded">
                        <p className="text-sm text-primary-700 dark:text-primary-300">
                          {change.content}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </Card.Content>
          </Card>
        ))}
      </div>

      {/* Info */}
      {!isEnabled && (
        <Card>
          <Card.Content className="p-4">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 p-2 bg-amber-100 dark:bg-amber-900/20 rounded-lg">
                <GitBranch className="h-5 w-5 text-amber-600 dark:text-amber-400" />
              </div>
              <div className="flex-1">
                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                  Track Changes is Disabled
                </h4>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                  Enable track changes to see all edits made by collaborators. You can review,
                  accept, or reject each change individually.
                </p>
                <Button variant="primary" size="sm" onClick={onToggle}>
                  Enable Track Changes
                </Button>
              </div>
            </div>
          </Card.Content>
        </Card>
      )}
    </div>
  )
}
