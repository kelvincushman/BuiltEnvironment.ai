import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card,
  Button,
  Input,
  Select,
  Badge,
  ComplianceBadge,
  EmptyState,
} from '@/components/ui'
import {
  AlertTriangle,
  Search,
  Filter,
  ChevronRight,
  CheckCircle,
  XCircle,
  Clock,
} from 'lucide-react'

interface Finding {
  id: string
  severity: 'red' | 'amber' | 'green' | 'gray'
  title: string
  description: string
  category: string
  regulation: string
  project: string
  document: string
  specialist: string
  status: 'open' | 'in-review' | 'resolved' | 'dismissed'
  confidence: number
  createdAt: string
  updatedAt: string
}

// Mock data
const mockFindings: Finding[] = [
  {
    id: '1',
    severity: 'red',
    title: 'Fire safety compliance issue in stairwell design',
    description: 'The stairwell design does not meet the minimum width requirements specified in Approved Document B for means of escape.',
    category: 'Part B - Fire Safety',
    regulation: 'B1 - Means of Warning and Escape',
    project: 'Royal Hospital Extension',
    document: 'Architectural Plans - Ground Floor.pdf',
    specialist: 'Fire Safety Specialist',
    status: 'open',
    confidence: 95,
    createdAt: '2025-02-15',
    updatedAt: '1 hour ago',
  },
  {
    id: '2',
    severity: 'amber',
    title: 'Ventilation requirements not fully specified',
    description: 'The ventilation strategy for the main hall lacks detailed calculations for air change rates.',
    category: 'Part F - Ventilation',
    regulation: 'F1 - Means of Ventilation',
    project: 'City Centre Office Block',
    document: 'MEP Specifications.pdf',
    specialist: 'Environmental Sustainability Specialist',
    status: 'in-review',
    confidence: 82,
    createdAt: '2025-02-14',
    updatedAt: '3 hours ago',
  },
  {
    id: '3',
    severity: 'green',
    title: 'Structural calculations verified and approved',
    description: 'All structural calculations have been reviewed and meet the requirements of Approved Document A.',
    category: 'Part A - Structure',
    regulation: 'A1 - Loading',
    project: 'Residential Tower Phase 2',
    document: 'Structural Calculations.xlsx',
    specialist: 'Structural Specialist',
    status: 'resolved',
    confidence: 98,
    createdAt: '2025-02-13',
    updatedAt: '1 day ago',
  },
  {
    id: '4',
    severity: 'amber',
    title: 'Accessibility requirements need clarification',
    description: 'The access routes to certain facilities require additional documentation to demonstrate compliance with accessibility standards.',
    category: 'Part M - Access',
    regulation: 'M1 - Access and Use',
    project: 'School Refurbishment',
    document: 'Access Statement.pdf',
    specialist: 'Accessibility Specialist',
    status: 'open',
    confidence: 78,
    createdAt: '2025-02-12',
    updatedAt: '2 days ago',
  },
  {
    id: '5',
    severity: 'red',
    title: 'Energy performance calculations incomplete',
    description: 'The SAP calculations are missing key data for glazing U-values and thermal bridging.',
    category: 'Part L - Conservation',
    regulation: 'L1 - Conservation of Fuel and Power',
    project: 'Royal Hospital Extension',
    document: 'Energy Assessment.pdf',
    specialist: 'Environmental Sustainability Specialist',
    status: 'open',
    confidence: 92,
    createdAt: '2025-02-11',
    updatedAt: '3 days ago',
  },
  {
    id: '6',
    severity: 'amber',
    title: 'Sound insulation details require verification',
    description: 'Acoustic testing specifications need to be provided for party wall constructions.',
    category: 'Part E - Sound',
    regulation: 'E1 - Protection Against Sound',
    project: 'Residential Tower Phase 2',
    document: 'Acoustic Report.pdf',
    specialist: 'Building Physics Specialist',
    status: 'in-review',
    confidence: 85,
    createdAt: '2025-02-10',
    updatedAt: '4 days ago',
  },
  {
    id: '7',
    severity: 'gray',
    title: 'Additional information requested for drainage system',
    description: 'Further details on the surface water drainage strategy would be beneficial for full assessment.',
    category: 'Part H - Drainage',
    regulation: 'H3 - Rainwater Drainage',
    project: 'City Centre Office Block',
    document: 'Drainage Strategy.pdf',
    specialist: 'MEP Specialist',
    status: 'open',
    confidence: 65,
    createdAt: '2025-02-09',
    updatedAt: '5 days ago',
  },
]

const statusInfo = {
  open: { icon: XCircle, color: 'text-danger-600 dark:text-danger-400', bg: 'bg-danger-100 dark:bg-danger-900/20', text: 'text-danger-700 dark:text-danger-300', label: 'Open' },
  'in-review': { icon: Clock, color: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-100 dark:bg-amber-900/20', text: 'text-amber-700 dark:text-amber-300', label: 'In Review' },
  resolved: { icon: CheckCircle, color: 'text-success-600 dark:text-success-400', bg: 'bg-success-100 dark:bg-success-900/20', text: 'text-success-700 dark:text-success-300', label: 'Resolved' },
  dismissed: { icon: XCircle, color: 'text-gray-600 dark:text-gray-400', bg: 'bg-gray-100 dark:bg-gray-900/20', text: 'text-gray-700 dark:text-gray-300', label: 'Dismissed' },
}

export function Findings() {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [severityFilter, setSeverityFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [findings] = useState<Finding[]>(mockFindings)

  const filteredFindings = findings.filter((finding) => {
    const matchesSearch = finding.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      finding.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      finding.project.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesSeverity = severityFilter === 'all' || finding.severity === severityFilter
    const matchesStatus = statusFilter === 'all' || finding.status === statusFilter
    const matchesCategory = categoryFilter === 'all' || finding.category === categoryFilter
    return matchesSearch && matchesSeverity && matchesStatus && matchesCategory
  })

  // Get unique categories for filter
  const categories = Array.from(new Set(findings.map((f) => f.category)))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Findings</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Review and manage compliance findings from AI analysis
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <Card.Content className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Critical</p>
                <p className="text-2xl font-bold text-danger-600 dark:text-danger-400">
                  {findings.filter((f) => f.severity === 'red').length}
                </p>
              </div>
              <div className="p-2 bg-danger-100 dark:bg-danger-900/20 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-danger-600 dark:text-danger-400" />
              </div>
            </div>
          </Card.Content>
        </Card>
        <Card>
          <Card.Content className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Needs Review</p>
                <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                  {findings.filter((f) => f.severity === 'amber').length}
                </p>
              </div>
              <div className="p-2 bg-amber-100 dark:bg-amber-900/20 rounded-lg">
                <Clock className="h-5 w-5 text-amber-600 dark:text-amber-400" />
              </div>
            </div>
          </Card.Content>
        </Card>
        <Card>
          <Card.Content className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Compliant</p>
                <p className="text-2xl font-bold text-success-600 dark:text-success-400">
                  {findings.filter((f) => f.severity === 'green').length}
                </p>
              </div>
              <div className="p-2 bg-success-100 dark:bg-success-900/20 rounded-lg">
                <CheckCircle className="h-5 w-5 text-success-600 dark:text-success-400" />
              </div>
            </div>
          </Card.Content>
        </Card>
        <Card>
          <Card.Content className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Open</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {findings.filter((f) => f.status === 'open').length}
                </p>
              </div>
              <div className="p-2 bg-primary-100 dark:bg-primary-900/20 rounded-lg">
                <XCircle className="h-5 w-5 text-primary-600 dark:text-primary-400" />
              </div>
            </div>
          </Card.Content>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <Card.Content className="p-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Input
              placeholder="Search findings..."
              leftIcon={<Search className="h-4 w-4" />}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              leftIcon={<Filter className="h-4 w-4" />}
            >
              <option value="all">All Severities</option>
              <option value="red">Critical</option>
              <option value="amber">Needs Review</option>
              <option value="green">Compliant</option>
              <option value="gray">Info</option>
            </Select>
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              leftIcon={<Filter className="h-4 w-4" />}
            >
              <option value="all">All Status</option>
              <option value="open">Open</option>
              <option value="in-review">In Review</option>
              <option value="resolved">Resolved</option>
              <option value="dismissed">Dismissed</option>
            </Select>
            <Select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              leftIcon={<Filter className="h-4 w-4" />}
            >
              <option value="all">All Categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </Select>
          </div>
        </Card.Content>
      </Card>

      {/* Findings List */}
      {filteredFindings.length === 0 ? (
        <Card>
          <Card.Content className="py-12">
            <EmptyState
              icon={<AlertTriangle className="h-12 w-12" />}
              title="No findings found"
              description={
                searchTerm || severityFilter !== 'all' || statusFilter !== 'all' || categoryFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Upload documents to start compliance checking'
              }
            />
          </Card.Content>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredFindings.map((finding) => {
            const StatusIcon = statusInfo[finding.status].icon
            return (
              <Card
                key={finding.id}
                className="hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => navigate(`/findings/${finding.id}`)}
              >
                <Card.Content className="p-6">
                  <div className="flex items-start gap-4">
                    {/* Severity Badge */}
                    <div className="flex-shrink-0 pt-1">
                      <ComplianceBadge status={finding.severity}>
                        {finding.severity.toUpperCase()}
                      </ComplianceBadge>
                    </div>

                    {/* Finding Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {finding.title}
                        </h3>
                        <ChevronRight className="h-5 w-5 text-gray-400 flex-shrink-0" />
                      </div>

                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                        {finding.description}
                      </p>

                      <div className="flex flex-wrap items-center gap-3 text-xs">
                        <Badge
                          variant="secondary"
                          className={`${statusInfo[finding.status].bg} ${statusInfo[finding.status].text}`}
                        >
                          <StatusIcon className="h-3 w-3 mr-1" />
                          {statusInfo[finding.status].label}
                        </Badge>
                        <span className="text-gray-500 dark:text-gray-400">
                          {finding.category}
                        </span>
                        <span className="text-gray-500 dark:text-gray-400">•</span>
                        <span className="text-gray-500 dark:text-gray-400">
                          {finding.project}
                        </span>
                        <span className="text-gray-500 dark:text-gray-400">•</span>
                        <span className="text-gray-500 dark:text-gray-400">
                          {finding.confidence}% confidence
                        </span>
                        <span className="text-gray-500 dark:text-gray-400">•</span>
                        <span className="text-gray-500 dark:text-gray-400">
                          Updated {finding.updatedAt}
                        </span>
                      </div>
                    </div>
                  </div>
                </Card.Content>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
