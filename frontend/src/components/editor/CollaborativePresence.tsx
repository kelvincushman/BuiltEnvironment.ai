import React from 'react'
import { Badge } from '@/components/ui'
import { Users, Circle } from 'lucide-react'

export interface ActiveUser {
  id: string
  name: string
  role: string
  color: string
  isTyping?: boolean
  lastSeen: string
}

interface CollaborativePresenceProps {
  activeUsers: ActiveUser[]
  currentUserId: string
  className?: string
}

export function CollaborativePresence({
  activeUsers,
  currentUserId,
  className = '',
}: CollaborativePresenceProps) {
  const otherUsers = activeUsers.filter((user) => user.id !== currentUserId)
  const typingUsers = otherUsers.filter((user) => user.isTyping)

  if (otherUsers.length === 0) {
    return null
  }

  return (
    <div className={`flex items-center gap-4 ${className}`}>
      {/* Active users avatars */}
      <div className="flex items-center">
        <Users className="h-4 w-4 text-gray-500 dark:text-gray-400 mr-2" />
        <div className="flex -space-x-2">
          {otherUsers.slice(0, 5).map((user) => (
            <div
              key={user.id}
              className="relative group"
              title={`${user.name} (${user.role})`}
            >
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-semibold border-2 border-white dark:border-gray-800 shadow-sm relative z-10"
                style={{ backgroundColor: user.color }}
              >
                {user.name
                  .split(' ')
                  .map((n) => n[0])
                  .join('')
                  .toUpperCase()
                  .slice(0, 2)}
              </div>
              {/* Online indicator */}
              <div
                className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border-2 border-white dark:border-gray-800 z-20"
                style={{ backgroundColor: '#22C55E' }}
              ></div>

              {/* Tooltip */}
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 dark:bg-gray-700 text-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity z-30">
                {user.name}
                <div className="text-gray-300 dark:text-gray-400">{user.role}</div>
                {user.isTyping && (
                  <div className="text-primary-400">typing...</div>
                )}
              </div>
            </div>
          ))}
          {otherUsers.length > 5 && (
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs font-semibold border-2 border-white dark:border-gray-800 shadow-sm"
              title={`${otherUsers.length - 5} more`}
            >
              +{otherUsers.length - 5}
            </div>
          )}
        </div>
      </div>

      {/* Typing indicator */}
      {typingUsers.length > 0 && (
        <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
          <div className="flex space-x-1">
            <Circle className="h-2 w-2 fill-current animate-bounce" />
            <Circle
              className="h-2 w-2 fill-current animate-bounce"
              style={{ animationDelay: '0.2s' }}
            />
            <Circle
              className="h-2 w-2 fill-current animate-bounce"
              style={{ animationDelay: '0.4s' }}
            />
          </div>
          <span>
            {typingUsers.length === 1
              ? `${typingUsers[0].name} is typing`
              : `${typingUsers.length} people are typing`}
          </span>
        </div>
      )}

      {/* Active count badge */}
      <Badge variant="secondary" className="bg-success-100 dark:bg-success-900/20 text-success-700 dark:text-success-300">
        {otherUsers.length} {otherUsers.length === 1 ? 'viewer' : 'viewers'}
      </Badge>
    </div>
  )
}
