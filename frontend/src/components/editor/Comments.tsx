import React, { useState } from 'react'
import { Card, Button, Textarea, Badge } from '@/components/ui'
import { MessageSquare, X, Edit2, Trash2, Check, User } from 'lucide-react'

export interface Comment {
  id: string
  author: string
  authorRole: string
  content: string
  createdAt: string
  updatedAt?: string
  resolved: boolean
  highlightedText?: string
}

interface CommentsProps {
  comments: Comment[]
  onAddComment: (content: string, highlightedText?: string) => void
  onEditComment: (id: string, content: string) => void
  onDeleteComment: (id: string) => void
  onResolveComment: (id: string) => void
  className?: string
}

export function Comments({
  comments,
  onAddComment,
  onEditComment,
  onDeleteComment,
  onResolveComment,
  className = '',
}: CommentsProps) {
  const [newComment, setNewComment] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editContent, setEditContent] = useState('')
  const [showResolved, setShowResolved] = useState(false)

  const handleSubmitNew = () => {
    if (newComment.trim()) {
      onAddComment(newComment.trim())
      setNewComment('')
    }
  }

  const handleSaveEdit = (id: string) => {
    if (editContent.trim()) {
      onEditComment(id, editContent.trim())
      setEditingId(null)
      setEditContent('')
    }
  }

  const handleCancelEdit = () => {
    setEditingId(null)
    setEditContent('')
  }

  const activeComments = comments.filter((c) => !c.resolved)
  const resolvedComments = comments.filter((c) => c.resolved)

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5 text-primary-600 dark:text-primary-400" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Comments ({activeComments.length})
          </h3>
        </div>
        {resolvedComments.length > 0 && (
          <button
            onClick={() => setShowResolved(!showResolved)}
            className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
          >
            {showResolved ? 'Hide' : 'Show'} resolved ({resolvedComments.length})
          </button>
        )}
      </div>

      {/* New Comment Form */}
      <Card>
        <Card.Content className="p-4">
          <div className="space-y-3">
            <Textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Add a comment..."
              rows={3}
            />
            <div className="flex justify-end">
              <Button
                variant="primary"
                size="sm"
                onClick={handleSubmitNew}
                disabled={!newComment.trim()}
              >
                Add Comment
              </Button>
            </div>
          </div>
        </Card.Content>
      </Card>

      {/* Active Comments */}
      <div className="space-y-3">
        {activeComments.length === 0 && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
            No comments yet. Add one above!
          </div>
        )}

        {activeComments.map((comment) => (
          <Card key={comment.id} className="border-l-4 border-l-primary-500">
            <Card.Content className="p-4">
              <div className="flex items-start gap-3">
                {/* Avatar */}
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/20 flex items-center justify-center">
                    <User className="h-4 w-4 text-primary-600 dark:text-primary-400" />
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">
                        {comment.author}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {comment.authorRole} • {comment.createdAt}
                        {comment.updatedAt && ' (edited)'}
                      </p>
                    </div>
                    <div className="flex gap-1">
                      <button
                        onClick={() => {
                          setEditingId(comment.id)
                          setEditContent(comment.content)
                        }}
                        className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                        title="Edit comment"
                      >
                        <Edit2 className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => onResolveComment(comment.id)}
                        className="p-1 text-gray-400 hover:text-success-600 dark:hover:text-success-400 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                        title="Resolve comment"
                      >
                        <Check className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => onDeleteComment(comment.id)}
                        className="p-1 text-gray-400 hover:text-danger-600 dark:hover:text-danger-400 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                        title="Delete comment"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>

                  {/* Highlighted Text */}
                  {comment.highlightedText && (
                    <div className="mb-2 p-2 bg-amber-50 dark:bg-amber-900/20 border-l-2 border-amber-400 dark:border-amber-600 rounded">
                      <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                        Referring to:
                      </p>
                      <p className="text-sm text-gray-700 dark:text-gray-300 italic">
                        "{comment.highlightedText}"
                      </p>
                    </div>
                  )}

                  {/* Comment Content */}
                  {editingId === comment.id ? (
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
                          onClick={() => handleSaveEdit(comment.id)}
                          disabled={!editContent.trim()}
                        >
                          Save
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={handleCancelEdit}
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                      {comment.content}
                    </p>
                  )}
                </div>
              </div>
            </Card.Content>
          </Card>
        ))}
      </div>

      {/* Resolved Comments */}
      {showResolved && resolvedComments.length > 0 && (
        <>
          <div className="border-t border-gray-200 dark:border-gray-700 my-4"></div>
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Resolved Comments
            </h4>
            {resolvedComments.map((comment) => (
              <Card
                key={comment.id}
                className="border-l-4 border-l-success-500 opacity-60"
              >
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
                            {comment.author}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {comment.authorRole} • {comment.createdAt}
                          </p>
                        </div>
                        <Badge variant="secondary" className="bg-success-100 dark:bg-success-900/20 text-success-700 dark:text-success-300">
                          Resolved
                        </Badge>
                      </div>
                      {comment.highlightedText && (
                        <div className="mb-2 p-2 bg-amber-50 dark:bg-amber-900/20 border-l-2 border-amber-400 dark:border-amber-600 rounded">
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            "{comment.highlightedText}"
                          </p>
                        </div>
                      )}
                      <p className="text-sm text-gray-700 dark:text-gray-300">
                        {comment.content}
                      </p>
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
