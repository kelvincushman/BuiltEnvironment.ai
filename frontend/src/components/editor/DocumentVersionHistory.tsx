import React, { useState } from 'react'
import { Card, Button, Badge } from '@/components/ui'
import { History, RotateCcw, Eye, Download, ChevronDown, ChevronRight } from 'lucide-react'

export interface DocumentVersion {
  id: string
  version: number
  createdAt: string
  createdBy: string
  changes: string
  size: string
  isCurrent: boolean
}

interface DocumentVersionHistoryProps {
  versions: DocumentVersion[]
  onRestore: (versionId: string) => void
  onPreview: (versionId: string) => void
  onDownload: (versionId: string) => void
  className?: string
}

export function DocumentVersionHistory({
  versions,
  onRestore,
  onPreview,
  onDownload,
  className = '',
}: DocumentVersionHistoryProps) {
  const [expandedVersions, setExpandedVersions] = useState<Set<string>>(new Set())

  const toggleVersion = (versionId: string) => {
    const newExpanded = new Set(expandedVersions)
    if (newExpanded.has(versionId)) {
      newExpanded.delete(versionId)
    } else {
      newExpanded.add(versionId)
    }
    setExpandedVersions(newExpanded)
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center gap-2">
        <History className="h-5 w-5 text-primary-600 dark:text-primary-400" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Version History ({versions.length})
        </h3>
      </div>

      {/* Timeline */}
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"></div>

        {/* Versions */}
        <div className="space-y-4">
          {versions.map((version, index) => (
            <div key={version.id} className="relative">
              {/* Timeline dot */}
              <div
                className={`absolute left-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  version.isCurrent
                    ? 'bg-success-600 dark:bg-success-500'
                    : 'bg-gray-300 dark:bg-gray-600'
                }`}
              >
                {version.isCurrent ? (
                  <span className="text-white text-xs font-bold">NOW</span>
                ) : (
                  <span className="text-white text-xs font-bold">v{version.version}</span>
                )}
              </div>

              {/* Version card */}
              <Card className="ml-12">
                <Card.Content className="p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      {/* Version header */}
                      <div className="flex items-center gap-3 mb-2">
                        <button
                          onClick={() => toggleVersion(version.id)}
                          className="flex items-center gap-2 hover:text-primary-600 dark:hover:text-primary-400"
                        >
                          {expandedVersions.has(version.id) ? (
                            <ChevronDown className="h-4 w-4" />
                          ) : (
                            <ChevronRight className="h-4 w-4" />
                          )}
                          <h4 className="text-sm font-semibold text-gray-900 dark:text-white">
                            Version {version.version}
                            {version.isCurrent && (
                              <Badge
                                variant="secondary"
                                className="ml-2 bg-success-100 dark:bg-success-900/20 text-success-700 dark:text-success-300"
                              >
                                Current
                              </Badge>
                            )}
                          </h4>
                        </button>
                      </div>

                      {/* Version metadata */}
                      <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                        <span className="font-medium">{version.createdBy}</span>
                        <span className="mx-2">•</span>
                        <span>{version.createdAt}</span>
                        <span className="mx-2">•</span>
                        <span>{version.size}</span>
                      </div>

                      {/* Expandable changes */}
                      {expandedVersions.has(version.id) && (
                        <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                          <p className="text-sm text-gray-700 dark:text-gray-300">
                            <strong>Changes:</strong> {version.changes}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onPreview(version.id)}
                        title="Preview version"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onDownload(version.id)}
                        title="Download version"
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                      {!version.isCurrent && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onRestore(version.id)}
                          title="Restore this version"
                        >
                          <RotateCcw className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </Card.Content>
              </Card>
            </div>
          ))}
        </div>
      </div>

      {/* Info footer */}
      <Card>
        <Card.Content className="p-4">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 p-2 bg-primary-100 dark:bg-primary-900/20 rounded-lg">
              <History className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            </div>
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                Version Control
              </h4>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                All changes are automatically saved as versions. You can preview, download, or
                restore any previous version. Restoring creates a new version based on the
                selected one.
              </p>
            </div>
          </div>
        </Card.Content>
      </Card>
    </div>
  )
}
