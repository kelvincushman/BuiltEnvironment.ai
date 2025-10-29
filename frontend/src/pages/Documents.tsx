import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card,
  Button,
  Input,
  Select,
  Badge,
  EmptyState,
  Modal,
} from '@/components/ui'
import {
  FileText,
  Upload,
  Search,
  Filter,
  Download,
  Eye,
  Trash2,
  MoreVertical,
  File,
  FileSpreadsheet,
  FileImage,
  FilePdf,
} from 'lucide-react'

interface Document {
  id: string
  name: string
  type: 'pdf' | 'xlsx' | 'docx' | 'dwg' | 'image'
  size: string
  project: string
  uploadedBy: string
  uploadedAt: string
  status: 'processed' | 'processing' | 'failed'
  findings: number
}

// Mock data
const mockDocuments: Document[] = [
  {
    id: '1',
    name: 'Architectural Plans - Ground Floor.pdf',
    type: 'pdf',
    size: '12.4 MB',
    project: 'Royal Hospital Extension',
    uploadedBy: 'Sarah Johnson',
    uploadedAt: '2025-02-15',
    status: 'processed',
    findings: 3,
  },
  {
    id: '2',
    name: 'Fire Safety Assessment.pdf',
    type: 'pdf',
    size: '3.2 MB',
    project: 'City Centre Office Block',
    uploadedBy: 'John Smith',
    uploadedAt: '2025-02-14',
    status: 'processing',
    findings: 0,
  },
  {
    id: '3',
    name: 'Structural Calculations.xlsx',
    type: 'xlsx',
    size: '1.8 MB',
    project: 'Royal Hospital Extension',
    uploadedBy: 'Mike Brown',
    uploadedAt: '2025-02-13',
    status: 'processed',
    findings: 1,
  },
  {
    id: '4',
    name: 'MEP Drawings.dwg',
    type: 'dwg',
    size: '8.5 MB',
    project: 'Residential Tower Phase 2',
    uploadedBy: 'Lisa Chen',
    uploadedAt: '2025-02-12',
    status: 'processed',
    findings: 5,
  },
  {
    id: '5',
    name: 'Site Photos - Week 1.zip',
    type: 'image',
    size: '45.2 MB',
    project: 'School Refurbishment',
    uploadedBy: 'Tom Wilson',
    uploadedAt: '2025-02-11',
    status: 'processed',
    findings: 0,
  },
]

const fileIcons = {
  pdf: FilePdf,
  xlsx: FileSpreadsheet,
  docx: FileText,
  dwg: FileText,
  image: FileImage,
}

const statusColors = {
  processed: { bg: 'bg-success-100 dark:bg-success-900/20', text: 'text-success-700 dark:text-success-300', label: 'Processed' },
  processing: { bg: 'bg-amber-100 dark:bg-amber-900/20', text: 'text-amber-700 dark:text-amber-300', label: 'Processing' },
  failed: { bg: 'bg-danger-100 dark:bg-danger-900/20', text: 'text-danger-700 dark:text-danger-300', label: 'Failed' },
}

export function Documents() {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [documents] = useState<Document[]>(mockDocuments)
  const [showUploadModal, setShowUploadModal] = useState(false)

  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.project.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = typeFilter === 'all' || doc.type === typeFilter
    const matchesStatus = statusFilter === 'all' || doc.status === statusFilter
    return matchesSearch && matchesType && matchesStatus
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Documents</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Upload and manage project documents for compliance checking
          </p>
        </div>
        <Button
          variant="primary"
          leftIcon={<Upload className="h-5 w-5" />}
          onClick={() => setShowUploadModal(true)}
        >
          Upload Documents
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <Card.Content className="p-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="sm:col-span-1">
              <Input
                placeholder="Search documents..."
                leftIcon={<Search className="h-4 w-4" />}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              leftIcon={<Filter className="h-4 w-4" />}
            >
              <option value="all">All Types</option>
              <option value="pdf">PDF</option>
              <option value="xlsx">Excel</option>
              <option value="docx">Word</option>
              <option value="dwg">CAD</option>
              <option value="image">Images</option>
            </Select>
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              leftIcon={<Filter className="h-4 w-4" />}
            >
              <option value="all">All Status</option>
              <option value="processed">Processed</option>
              <option value="processing">Processing</option>
              <option value="failed">Failed</option>
            </Select>
          </div>
        </Card.Content>
      </Card>

      {/* Documents List */}
      {filteredDocuments.length === 0 ? (
        <Card>
          <Card.Content className="py-12">
            <EmptyState
              icon={<FileText className="h-12 w-12" />}
              title="No documents found"
              description={
                searchTerm || typeFilter !== 'all' || statusFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Upload your first document to get started with AI compliance checking'
              }
              action={
                !searchTerm && typeFilter === 'all' && statusFilter === 'all'
                  ? {
                      label: 'Upload Documents',
                      onClick: () => setShowUploadModal(true),
                      variant: 'primary',
                      leftIcon: <Upload className="h-4 w-4" />,
                    }
                  : undefined
              }
            />
          </Card.Content>
        </Card>
      ) : (
        <Card>
          <Card.Content className="p-0">
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredDocuments.map((doc) => {
                const FileIcon = fileIcons[doc.type]
                return (
                  <div
                    key={doc.id}
                    className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      {/* File Icon */}
                      <div className="flex-shrink-0">
                        <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/20 rounded-lg flex items-center justify-center">
                          <FileIcon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
                        </div>
                      </div>

                      {/* File Info */}
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {doc.name}
                        </h3>
                        <div className="flex items-center gap-3 mt-1 text-xs text-gray-500 dark:text-gray-400">
                          <span>{doc.size}</span>
                          <span>•</span>
                          <span>{doc.project}</span>
                          <span>•</span>
                          <span>
                            Uploaded by {doc.uploadedBy} on {doc.uploadedAt}
                          </span>
                        </div>
                      </div>

                      {/* Status and Actions */}
                      <div className="flex items-center gap-3">
                        {doc.findings > 0 && (
                          <Badge variant="secondary" className="bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300">
                            {doc.findings} finding{doc.findings !== 1 ? 's' : ''}
                          </Badge>
                        )}
                        <Badge
                          variant="secondary"
                          className={`${statusColors[doc.status].bg} ${statusColors[doc.status].text}`}
                        >
                          {statusColors[doc.status].label}
                        </Badge>
                        <div className="flex gap-1">
                          <Button variant="ghost" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Download className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </Card.Content>
        </Card>
      )}

      {/* Stats summary */}
      <Card>
        <Card.Content className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Documents</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {documents.length}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Processed</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {documents.filter((d) => d.status === 'processed').length}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Processing</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {documents.filter((d) => d.status === 'processing').length}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Findings</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {documents.reduce((sum, d) => sum + d.findings, 0)}
              </p>
            </div>
          </div>
        </Card.Content>
      </Card>

      {/* Upload Modal */}
      <Modal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        title="Upload Documents"
        size="lg"
      >
        <div className="space-y-4">
          <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-12 text-center">
            <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              Drag and drop files here, or click to browse
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-500">
              Supported formats: PDF, DOCX, XLSX, DWG, Images (Max 50MB)
            </p>
            <Button variant="outline" className="mt-4">
              Browse Files
            </Button>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select Project
            </label>
            <Select>
              <option>Royal Hospital Extension</option>
              <option>City Centre Office Block</option>
              <option>Residential Tower Phase 2</option>
              <option>School Refurbishment</option>
            </Select>
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="outline" onClick={() => setShowUploadModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={() => setShowUploadModal(false)}>
            Upload
          </Button>
        </div>
      </Modal>
    </div>
  )
}
