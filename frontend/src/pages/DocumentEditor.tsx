import React, { useState, useRef, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { RichTextEditor, Comments, type Comment } from '@/components/editor'
import { Card, Button, Badge } from '@/components/ui'
import {
  ArrowLeft,
  Save,
  Download,
  Share2,
  Clock,
  FileText,
  CheckCircle,
  AlertTriangle,
  FileDown,
  Copy,
  FileType,
} from 'lucide-react'
import { toast } from 'sonner'
import {
  exportToPDF,
  exportToMarkdown,
  exportToHTML,
  exportToDOCX,
  copyToClipboard,
} from '@/utils/exportUtils'

// Mock document data - will be replaced with API
const mockDocument = {
  id: '1',
  name: 'Fire Safety Assessment Report - Royal Hospital Extension',
  type: 'compliance-report',
  project: 'Royal Hospital Extension',
  generatedBy: 'Fire Safety Specialist AI',
  generatedAt: '2025-02-15 14:30',
  status: 'draft' as const,
  version: 1,
  findings: 3,
  content: `
<h1>Fire Safety Assessment Report</h1>
<p><strong>Project:</strong> Royal Hospital Extension</p>
<p><strong>Date:</strong> February 15, 2025</p>
<p><strong>Assessment Type:</strong> Building Regulations Part B Compliance Check</p>

<h2>Executive Summary</h2>
<p>This report presents the findings of a comprehensive fire safety assessment conducted on the Royal Hospital Extension project. The assessment evaluated compliance with Approved Document B (Fire Safety) of the Building Regulations 2010 (as amended).</p>

<h3>Key Findings</h3>
<ul>
  <li><mark style="background-color: #FECACA;">Critical Issue: Stairwell width does not meet minimum requirements</mark></li>
  <li><mark style="background-color: #FED7AA;">Warning: Fire door specifications require clarification</mark></li>
  <li><mark style="background-color: #BBF7D0;">Compliant: Emergency lighting system properly specified</mark></li>
</ul>

<h2>1. Means of Escape</h2>
<p>The means of escape provisions have been reviewed against the requirements of Section B1 of Approved Document B.</p>

<h3>1.1 Travel Distances</h3>
<p>Travel distances from all points within the building to the nearest exit have been calculated and compared against the maximum permitted distances:</p>
<ul>
  <li>Ground floor: Maximum 18m (Permitted: 18m) - <strong>Compliant</strong></li>
  <li>First floor: Maximum 15m (Permitted: 18m) - <strong>Compliant</strong></li>
  <li>Second floor: Maximum 12m (Permitted: 18m) - <strong>Compliant</strong></li>
</ul>

<h3>1.2 Stairwell Requirements</h3>
<p><mark style="background-color: #FECACA;"><strong>Critical Finding:</strong> The main escape stairwell width measures 950mm. This does not meet the minimum requirement of 1100mm for a building of this occupancy and height (B1: Section 3).</mark></p>

<blockquote>
<p><strong>Recommendation:</strong> The stairwell design must be revised to provide a minimum clear width of 1100mm to ensure safe evacuation during an emergency.</p>
</blockquote>

<h2>2. Fire Doors and Compartmentation</h2>
<p>Fire doors and compartmentation elements are critical to containing fire spread and protecting means of escape.</p>

<h3>2.1 Fire Door Specifications</h3>
<p><mark style="background-color: #FED7AA;"><strong>Warning:</strong> Fire door specifications on drawing A-101 reference "FD30S" doors but do not specify fire door hardware requirements including self-closing devices and intumescent seals.</mark></p>

<h2>3. Emergency Lighting</h2>
<p><mark style="background-color: #BBF7D0;">The emergency lighting design complies with BS 5266-1:2016 and provides adequate illumination along all escape routes and at fire alarm call points.</mark></p>

<h2>4. Recommendations</h2>
<ol>
  <li><strong>Immediate Action Required:</strong> Revise stairwell design to achieve 1100mm minimum width</li>
  <li><strong>Clarification Needed:</strong> Provide complete fire door specification including hardware schedule</li>
  <li><strong>Best Practice:</strong> Consider additional emergency lighting at floor level for smoke conditions</li>
</ol>

<h2>5. Conclusion</h2>
<p>While the majority of fire safety provisions are compliant with Building Regulations Part B, the identified critical issue with stairwell width must be addressed before proceeding to construction. The fire door specifications require clarification to ensure full compliance.</p>

<p><strong>Report prepared by:</strong> AI Fire Safety Specialist<br>
<strong>Report version:</strong> 1.0 (Draft)<br>
<strong>Next review:</strong> Pending design revisions</p>
  `,
}

const statusInfo = {
  draft: { color: 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300', label: 'Draft', icon: Clock },
  review: { color: 'bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300', label: 'In Review', icon: AlertTriangle },
  approved: { color: 'bg-success-100 dark:bg-success-900/20 text-success-700 dark:text-success-300', label: 'Approved', icon: CheckCircle },
}

export function DocumentEditor() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [document] = useState(mockDocument)
  const [content, setContent] = useState(document.content)
  const [isSaving, setIsSaving] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const [showExportMenu, setShowExportMenu] = useState(false)
  const [comments, setComments] = useState<Comment[]>([
    {
      id: '1',
      author: 'Sarah Johnson',
      authorRole: 'Fire Safety Engineer',
      content: 'The stairwell width issue needs immediate attention before proceeding to construction phase.',
      createdAt: '2025-02-15 15:45',
      resolved: false,
      highlightedText: 'The main escape stairwell width measures 950mm',
    },
    {
      id: '2',
      author: 'Mike Brown',
      authorRole: 'Project Manager',
      content: 'Can we get clarification on the fire door hardware requirements from the supplier?',
      createdAt: '2025-02-15 16:20',
      resolved: false,
      highlightedText: 'fire door hardware requirements',
    },
  ])

  const exportMenuRef = useRef<HTMLDivElement>(null)

  const StatusIcon = statusInfo[document.status].icon

  // Close export menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (exportMenuRef.current && !exportMenuRef.current.contains(event.target as Node)) {
        setShowExportMenu(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSave = async () => {
    setIsSaving(true)
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setLastSaved(new Date())
    setIsSaving(false)
    toast.success('Document saved successfully')
  }

  const handleExport = async (format: 'pdf' | 'docx' | 'markdown' | 'html' | 'copy') => {
    setIsExporting(true)
    setShowExportMenu(false)

    try {
      const fileName = document.name.replace(/\.[^/.]+$/, '') // Remove extension if present

      switch (format) {
        case 'pdf':
          await exportToPDF(content, fileName)
          toast.success('Document exported as PDF')
          break
        case 'docx':
          exportToDOCX(content, fileName)
          toast.success('Document exported as DOCX')
          break
        case 'markdown':
          exportToMarkdown(content, fileName)
          toast.success('Document exported as Markdown')
          break
        case 'html':
          exportToHTML(content, fileName)
          toast.success('Document exported as HTML')
          break
        case 'copy':
          // Copy plain text version
          const tempDiv = document.createElement('div')
          tempDiv.innerHTML = content
          await copyToClipboard(tempDiv.textContent || '')
          toast.success('Content copied to clipboard')
          break
      }
    } catch (error) {
      toast.error('Failed to export document')
      console.error('Export error:', error)
    } finally {
      setIsExporting(false)
    }
  }

  const handleShare = () => {
    toast.info('Share functionality coming soon')
  }

  // Comment handlers
  const handleAddComment = (content: string, highlightedText?: string) => {
    const newComment: Comment = {
      id: Date.now().toString(),
      author: 'Current User', // In real app, get from AuthContext
      authorRole: 'Reviewer',
      content,
      createdAt: new Date().toLocaleString(),
      resolved: false,
      highlightedText,
    }
    setComments([...comments, newComment])
    toast.success('Comment added')
  }

  const handleEditComment = (id: string, newContent: string) => {
    setComments(
      comments.map((comment) =>
        comment.id === id
          ? { ...comment, content: newContent, updatedAt: new Date().toLocaleString() }
          : comment
      )
    )
    toast.success('Comment updated')
  }

  const handleDeleteComment = (id: string) => {
    setComments(comments.filter((comment) => comment.id !== id))
    toast.success('Comment deleted')
  }

  const handleResolveComment = (id: string) => {
    setComments(
      comments.map((comment) =>
        comment.id === id ? { ...comment, resolved: true } : comment
      )
    )
    toast.success('Comment resolved')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Button
          variant="ghost"
          size="sm"
          leftIcon={<ArrowLeft className="h-4 w-4" />}
          onClick={() => navigate('/documents')}
          className="mb-4"
        >
          Back to Documents
        </Button>

        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <FileText className="h-6 w-6 text-primary-600 dark:text-primary-400" />
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                {document.name}
              </h1>
            </div>
            <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
              <Badge variant="secondary" className={statusInfo[document.status].color}>
                <StatusIcon className="h-3 w-3 mr-1" />
                {statusInfo[document.status].label}
              </Badge>
              <span>Project: {document.project}</span>
              <span>•</span>
              <span>Version {document.version}</span>
              <span>•</span>
              <span>Generated {document.generatedAt}</span>
              {lastSaved && (
                <>
                  <span>•</span>
                  <span className="text-success-600 dark:text-success-400">
                    Saved {lastSaved.toLocaleTimeString()}
                  </span>
                </>
              )}
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              leftIcon={<Share2 className="h-4 w-4" />}
              onClick={handleShare}
            >
              Share
            </Button>

            {/* Export Dropdown */}
            <div className="relative" ref={exportMenuRef}>
              <Button
                variant="outline"
                leftIcon={<Download className="h-4 w-4" />}
                onClick={() => setShowExportMenu(!showExportMenu)}
                disabled={isExporting}
                isLoading={isExporting}
              >
                Export
              </Button>

              {showExportMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50">
                  <button
                    onClick={() => handleExport('pdf')}
                    className="w-full flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <FileDown className="h-4 w-4 mr-3 text-danger-600 dark:text-danger-400" />
                    Export as PDF
                  </button>
                  <button
                    onClick={() => handleExport('docx')}
                    className="w-full flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <FileType className="h-4 w-4 mr-3 text-primary-600 dark:text-primary-400" />
                    Export as DOCX
                  </button>
                  <button
                    onClick={() => handleExport('markdown')}
                    className="w-full flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <FileText className="h-4 w-4 mr-3 text-gray-600 dark:text-gray-400" />
                    Export as Markdown
                  </button>
                  <button
                    onClick={() => handleExport('html')}
                    className="w-full flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <FileText className="h-4 w-4 mr-3 text-accent-600 dark:text-accent-400" />
                    Export as HTML
                  </button>
                  <div className="border-t border-gray-200 dark:border-gray-700 my-1"></div>
                  <button
                    onClick={() => handleExport('copy')}
                    className="w-full flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <Copy className="h-4 w-4 mr-3 text-gray-600 dark:text-gray-400" />
                    Copy to Clipboard
                  </button>
                </div>
              )}
            </div>

            <Button
              variant="primary"
              leftIcon={<Save className="h-4 w-4" />}
              onClick={handleSave}
              isLoading={isSaving}
            >
              Save
            </Button>
          </div>
        </div>
      </div>

      {/* Info Banner */}
      <Card>
        <Card.Content className="p-4">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 p-2 bg-primary-100 dark:bg-primary-900/20 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                AI-Generated Document - Review Required
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                This document was generated by the <strong>{document.generatedBy}</strong>. Please review
                all content carefully, especially highlighted sections. You can edit, add comments, and
                highlight areas that need attention.
              </p>
            </div>
          </div>
        </Card.Content>
      </Card>

      {/* Editor and Comments - Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Editor (2/3 width on large screens) */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <Card.Content className="p-0">
              <RichTextEditor
                content={content}
                onChange={setContent}
                placeholder="Start editing the document..."
                minHeight="600px"
              />
            </Card.Content>
          </Card>

          {/* Quick Tips */}
          <Card>
            <Card.Header>
              <Card.Title>Editor Tips</Card.Title>
            </Card.Header>
            <Card.Content>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="font-medium text-gray-900 dark:text-white mb-1">Highlighting</p>
                  <p className="text-gray-600 dark:text-gray-400">
                    Use the highlight tool to mark areas that need attention or review
                  </p>
                </div>
                <div>
                  <p className="font-medium text-gray-900 dark:text-white mb-1">Commenting</p>
                  <p className="text-gray-600 dark:text-gray-400">
                    Add comments to specific sections for collaborative review
                  </p>
                </div>
                <div>
                  <p className="font-medium text-gray-900 dark:text-white mb-1">Text Formatting</p>
                  <p className="text-gray-600 dark:text-gray-400">
                    Bold, italic, underline, and color options available in the toolbar
                  </p>
                </div>
                <div>
                  <p className="font-medium text-gray-900 dark:text-white mb-1">Keyboard Shortcuts</p>
                  <p className="text-gray-600 dark:text-gray-400">
                    Ctrl+B (Bold), Ctrl+I (Italic), Ctrl+U (Underline), Ctrl+Z (Undo)
                  </p>
                </div>
              </div>
            </Card.Content>
          </Card>
        </div>

        {/* Comments Panel (1/3 width on large screens) */}
        <div className="lg:col-span-1">
          <Comments
            comments={comments}
            onAddComment={handleAddComment}
            onEditComment={handleEditComment}
            onDeleteComment={handleDeleteComment}
            onResolveComment={handleResolveComment}
          />
        </div>
      </div>
    </div>
  )
}
