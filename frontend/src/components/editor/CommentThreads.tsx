import React, { useState } from 'react'
import { Card, Button, Textarea, Badge } from '@/components/ui'
import { MessageSquare, X, Edit2, Trash2, Check, User, Reply, ChevronDown, ChevronRight } from 'lucide-react'

export interface CommentReply {
  id: string
  author: string
  authorRole: string
  content: string
  createdAt: string
  updatedAt?: string
}

export interface CommentThread {
  id: string
  author: string
  authorRole: string
  content: string
  createdAt: string
  updatedAt?: string
  resolved: boolean
  highlightedText?: string
  replies: CommentReply[]
}

interface CommentThreadsProps {
  threads: CommentThread[]
  onAddThread: (content: string, highlightedText?: string) => void
  onEditThread: (id: string, content: string) => void
  onDeleteThread: (id: string) => void
  onResolveThread: (id: string) => void
  onAddReply: (threadId: string, content: string) => void
  onEditReply: (threadId: string, replyId: string, content: string) => void
  onDeleteReply: (threadId: string, replyId: string) => void
  className?: string
}

export function CommentThreads({
  threads,
  onAddThread,
  onEditThread,
  onDeleteThread,
  onResolveThread,
  onAddReply,
  onEditReply,
  onDeleteReply,
  className = '',
}: CommentThreadsProps) {
  const [newThread, setNewThread] = useState('')
  const [editingThreadId, setEditingThreadId] = useState<string | null>(null)
  const [editContent, setEditContent] = useState('')
  const [replyingToThreadId, setReplyingToThreadId] = useState<string | null>(null)
  const [replyContent, setReplyContent] = useState('')
  const [editingReply, setEditingReply] = useState<{ threadId: string; replyId: string } | null>(null)
  const [editReplyContent, setEditReplyContent] = useState('')
  const [expandedThreads, setExpandedThreads] = useState<Set<string>>(new Set())
  const [showResolved, setShowResolved] = useState(false)

  const toggleThread = (threadId: string) => {
    const newExpanded = new Set(expandedThreads)
    if (newExpanded.has(threadId)) {
      newExpanded.delete(threadId)
    } else {
      newExpanded.add(threadId)
    }
    setExpandedThreads(newExpanded)
  }

  const handleSubmitNew = () => {
    if (newThread.trim()) {
      onAddThread(newThread.trim())
      setNewThread('')
    }
  }

  const handleSaveEdit = (id: string) => {
    if (editContent.trim()) {
      onEditThread(id, editContent.trim())
      setEditingThreadId(null)
      setEditContent('')
    }
  }

  const handleSubmitReply = (threadId: string) => {
    if (replyContent.trim()) {
      onAddReply(threadId, replyContent.trim())
      setReplyingToThreadId(null)
      setReplyContent('')
      expandedThreads.add(threadId)
      setExpandedThreads(new Set(expandedThreads))
    }
  }

  const handleSaveReplyEdit = (threadId: string, replyId: string) => {
    if (editReplyContent.trim()) {
      onEditReply(threadId, replyId, editReplyContent.trim())
      setEditingReply(null)
      setEditReplyContent('')
    }
  }

  const activeThreads = threads.filter((t) => !t.resolved)
  const resolvedThreads = threads.filter((t) => t.resolved)

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5 text-primary-600 dark:text-primary-400" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Discussion ({activeThreads.length})
          </h3>
        </div>
        {resolvedThreads.length > 0 && (
          <button
            onClick={() => setShowResolved(!showResolved)}
            className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
          >
            {showResolved ? 'Hide' : 'Show'} resolved ({resolvedThreads.length})
          </button>
        )}
      </div>

      {/* New Thread Form */}
      <Card>
        <Card.Content className="p-4">
          <div className="space-y-3">
            <Textarea
              value={newThread}
              onChange={(e) => setNewThread(e.target.value)}
              placeholder="Start a new discussion..."
              rows={3}
            />
            <div className="flex justify-end">
              <Button
                variant="primary"
                size="sm"
                onClick={handleSubmitNew}
                disabled={!newThread.trim()}
              >
                Start Discussion
              </Button>
            </div>
          </div>
        </Card.Content>
      </Card>

      {/* Active Threads */}
      <div className="space-y-3">
        {activeThreads.length === 0 && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
            No discussions yet. Start one above!
          </div>
        )}

        {activeThreads.map((thread) => {
          const isExpanded = expandedThreads.has(thread.id)
          const replyCount = thread.replies.length

          return (
            <Card key={thread.id} className="border-l-4 border-l-primary-500">
              <Card.Content className="p-4">
                {/* Main comment */}
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/20 flex items-center justify-center">
                      <User className="h-4 w-4 text-primary-600 dark:text-primary-400" />
                    </div>
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div>
                        <p className="text-sm font-semibold text-gray-900 dark:text-white">
                          {thread.author}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {thread.authorRole} • {thread.createdAt}
                          {thread.updatedAt && ' (edited)'}
                        </p>
                      </div>
                      <div className="flex gap-1">
                        <button
                          onClick={() => {
                            setEditingThreadId(thread.id)
                            setEditContent(thread.content)
                          }}
                          className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                          title="Edit"
                        >
                          <Edit2 className="h-3.5 w-3.5" />
                        </button>
                        <button
                          onClick={() => onResolveThread(thread.id)}
                          className="p-1 text-gray-400 hover:text-success-600 dark:hover:text-success-400 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                          title="Resolve"
                        >
                          <Check className="h-3.5 w-3.5" />
                        </button>
                        <button
                          onClick={() => onDeleteThread(thread.id)}
                          className="p-1 text-gray-400 hover:text-danger-600 dark:hover:text-danger-400 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                          title="Delete"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>

                    {/* Highlighted Text */}
                    {thread.highlightedText && (
                      <div className="mb-2 p-2 bg-amber-50 dark:bg-amber-900/20 border-l-2 border-amber-400 dark:border-amber-600 rounded">
                        <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                          Referring to:
                        </p>
                        <p className="text-sm text-gray-700 dark:text-gray-300 italic">
                          "{thread.highlightedText}"
                        </p>
                      </div>
                    )}

                    {/* Thread Content */}
                    {editingThreadId === thread.id ? (
                      <div className="space-y-2">
                        <Textarea
                          value={editContent}
                          onChange={(e) => setEditContent(e.target.value)}
                          rows={2}
                          autoFocus
                        />
                        <div className="flex gap-2">
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => handleSaveEdit(thread.id)}
                            disabled={!editContent.trim()}
                          >
                            Save
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingThreadId(null)
                              setEditContent('')
                            }}
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap mb-3">
                        {thread.content}
                      </p>
                    )}

                    {/* Thread actions */}
                    <div className="flex items-center gap-3 text-xs">
                      <button
                        onClick={() => setReplyingToThreadId(thread.id)}
                        className="flex items-center gap-1 text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
                      >
                        <Reply className="h-3 w-3" />
                        Reply
                      </button>
                      {replyCount > 0 && (
                        <button
                          onClick={() => toggleThread(thread.id)}
                          className="flex items-center gap-1 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                        >
                          {isExpanded ? (
                            <ChevronDown className="h-3 w-3" />
                          ) : (
                            <ChevronRight className="h-3 w-3" />
                          )}
                          {replyCount} {replyCount === 1 ? 'reply' : 'replies'}
                        </button>
                      )}
                    </div>

                    {/* Replies */}
                    {isExpanded && thread.replies.length > 0 && (
                      <div className="mt-4 pl-4 border-l-2 border-gray-200 dark:border-gray-700 space-y-3">
                        {thread.replies.map((reply) => (
                          <div key={reply.id} className="flex items-start gap-2">
                            <div className="flex-shrink-0">
                              <div className="w-6 h-6 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                                <User className="h-3 w-3 text-gray-600 dark:text-gray-400" />
                              </div>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-start justify-between gap-2 mb-1">
                                <div>
                                  <p className="text-xs font-semibold text-gray-900 dark:text-white">
                                    {reply.author}
                                  </p>
                                  <p className="text-xs text-gray-500 dark:text-gray-400">
                                    {reply.authorRole} • {reply.createdAt}
                                    {reply.updatedAt && ' (edited)'}
                                  </p>
                                </div>
                                <div className="flex gap-1">
                                  <button
                                    onClick={() => {
                                      setEditingReply({ threadId: thread.id, replyId: reply.id })
                                      setEditReplyContent(reply.content)
                                    }}
                                    className="p-0.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                                    title="Edit reply"
                                  >
                                    <Edit2 className="h-3 w-3" />
                                  </button>
                                  <button
                                    onClick={() => onDeleteReply(thread.id, reply.id)}
                                    className="p-0.5 text-gray-400 hover:text-danger-600 dark:hover:text-danger-400"
                                    title="Delete reply"
                                  >
                                    <Trash2 className="h-3 w-3" />
                                  </button>
                                </div>
                              </div>
                              {editingReply?.threadId === thread.id &&
                              editingReply?.replyId === reply.id ? (
                                <div className="space-y-2">
                                  <Textarea
                                    value={editReplyContent}
                                    onChange={(e) => setEditReplyContent(e.target.value)}
                                    rows={2}
                                    autoFocus
                                  />
                                  <div className="flex gap-2">
                                    <Button
                                      variant="primary"
                                      size="sm"
                                      onClick={() => handleSaveReplyEdit(thread.id, reply.id)}
                                      disabled={!editReplyContent.trim()}
                                    >
                                      Save
                                    </Button>
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      onClick={() => {
                                        setEditingReply(null)
                                        setEditReplyContent('')
                                      }}
                                    >
                                      Cancel
                                    </Button>
                                  </div>
                                </div>
                              ) : (
                                <p className="text-xs text-gray-700 dark:text-gray-300">
                                  {reply.content}
                                </p>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Reply form */}
                    {replyingToThreadId === thread.id && (
                      <div className="mt-3 pl-4 border-l-2 border-primary-300 dark:border-primary-700">
                        <div className="space-y-2">
                          <Textarea
                            value={replyContent}
                            onChange={(e) => setReplyContent(e.target.value)}
                            placeholder="Write a reply..."
                            rows={2}
                            autoFocus
                          />
                          <div className="flex gap-2">
                            <Button
                              variant="primary"
                              size="sm"
                              onClick={() => handleSubmitReply(thread.id)}
                              disabled={!replyContent.trim()}
                            >
                              Reply
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                setReplyingToThreadId(null)
                                setReplyContent('')
                              }}
                            >
                              Cancel
                            </Button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </Card.Content>
            </Card>
          )
        })}
      </div>

      {/* Resolved Threads */}
      {showResolved && resolvedThreads.length > 0 && (
        <>
          <div className="border-t border-gray-200 dark:border-gray-700 my-4"></div>
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Resolved Discussions
            </h4>
            {resolvedThreads.map((thread) => (
              <Card key={thread.id} className="border-l-4 border-l-success-500 opacity-60">
                <Card.Content className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-success-100 dark:bg-success-900/20 flex items-center justify-center">
                        <Check className="h-4 w-4 text-success-600 dark:text-success-400" />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <div>
                          <p className="text-sm font-semibold text-gray-900 dark:text-white">
                            {thread.author}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {thread.authorRole} • {thread.createdAt}
                          </p>
                        </div>
                        <Badge
                          variant="secondary"
                          className="bg-success-100 dark:bg-success-900/20 text-success-700 dark:text-success-300"
                        >
                          Resolved
                        </Badge>
                      </div>
                      {thread.highlightedText && (
                        <div className="mb-2 p-2 bg-amber-50 dark:bg-amber-900/20 border-l-2 border-amber-400 dark:border-amber-600 rounded">
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            "{thread.highlightedText}"
                          </p>
                        </div>
                      )}
                      <p className="text-sm text-gray-700 dark:text-gray-300">{thread.content}</p>
                      {thread.replies.length > 0 && (
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                          {thread.replies.length} {thread.replies.length === 1 ? 'reply' : 'replies'}
                        </p>
                      )}
                    </div>
                  </div>
                </Card.Content>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
