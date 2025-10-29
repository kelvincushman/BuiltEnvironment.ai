import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Button,
  Badge,
  ComplianceBadge,
  Tabs,
  EmptyState,
} from '@/components/ui'
import {
  ArrowLeft,
  Edit,
  FileText,
  AlertTriangle,
  Download,
  Upload,
  MoreVertical,
  Calendar,
  User,
  Building2,
} from 'lucide-react'

// Mock data
const mockProject = {
  id: '1',
  name: 'Royal Hospital Extension',
  description: 'Major extension to existing hospital facility with new emergency department',
  status: 'active' as const,
  compliance: 92,
  location: 'London, UK',
  client: 'NHS Trust London',
  projectManager: 'John Smith',
  startDate: '2025-01-15',
  targetDate: '2026-06-30',
  budget: '£45,000,000',
  documents: [
    {
      id: '1',
      name: 'Architectural Plans - Ground Floor.pdf',
      size: '12.4 MB',
      uploadedAt: '2025-02-15',
      uploadedBy: 'Sarah Johnson',
      status: 'processed',
    },
    {
      id: '2',
      name: 'Fire Safety Assessment.pdf',
      size: '3.2 MB',
      uploadedAt: '2025-02-14',
      uploadedBy: 'John Smith',
      status: 'processing',
    },
    {
      id: '3',
      name: 'Structural Calculations.xlsx',
      size: '1.8 MB',
      uploadedAt: '2025-02-13',
      uploadedBy: 'Mike Brown',
      status: 'processed',
    },
  ],
  findings: [
    {
      id: '1',
      severity: 'red' as const,
      title: 'Fire safety compliance issue in stairwell design',
      category: 'Part B - Fire Safety',
      status: 'open',
      createdAt: '2025-02-10',
    },
    {
      id: '2',
      severity: 'amber' as const,
      title: 'Ventilation requirements not fully specified',
      category: 'Part F - Ventilation',
      status: 'in-review',
      createdAt: '2025-02-12',
    },
    {
      id: '3',
      severity: 'green' as const,
      title: 'Structural calculations verified and approved',
      category: 'Part A - Structure',
      status: 'resolved',
      createdAt: '2025-02-08',
    },
    {
      id: '4',
      severity: 'amber' as const,
      title: 'Accessibility requirements need clarification',
      category: 'Part M - Access',
      status: 'open',
      createdAt: '2025-02-14',
    },
    {
      id: '5',
      severity: 'red' as const,
      title: 'Energy performance calculations incomplete',
      category: 'Part L - Conservation',
      status: 'open',
      createdAt: '2025-02-15',
    },
  ],
}

export function ProjectDetails() {
  const { id } = useParams()
  const navigate = useNavigate()

  // In real app, fetch project data using the ID
  const project = mockProject

  const statusColors = {
    active: { bg: 'bg-success-100 dark:bg-success-900/20', text: 'text-success-700 dark:text-success-300', label: 'Active' },
    completed: { bg: 'bg-primary-100 dark:bg-primary-900/20', text: 'text-primary-700 dark:text-primary-300', label: 'Completed' },
    'on-hold': { bg: 'bg-amber-100 dark:bg-amber-900/20', text: 'text-amber-700 dark:text-amber-300', label: 'On Hold' },
  }

  const findingStatusColors = {
    open: 'bg-danger-100 dark:bg-danger-900/20 text-danger-700 dark:text-danger-300',
    'in-review': 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300',
    resolved: 'bg-success-100 dark:bg-success-900/20 text-success-700 dark:text-success-300',
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Button
          variant="ghost"
          size="sm"
          leftIcon={<ArrowLeft className="h-4 w-4" />}
          onClick={() => navigate('/projects')}
          className="mb-4"
        >
          Back to Projects
        </Button>
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                {project.name}
              </h1>
              <Badge
                variant="secondary"
                className={`${statusColors[project.status].bg} ${statusColors[project.status].text}`}
              >
                {statusColors[project.status].label}
              </Badge>
            </div>
            <p className="text-gray-600 dark:text-gray-400">{project.description}</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" leftIcon={<Edit className="h-4 w-4" />}>
              Edit
            </Button>
            <Button variant="ghost">
              <MoreVertical className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>

      {/* Project Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <Card.Content className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary-100 dark:bg-primary-900/20 rounded-lg">
                <Building2 className="h-5 w-5 text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Client</p>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {project.client}
                </p>
              </div>
            </div>
          </Card.Content>
        </Card>
        <Card>
          <Card.Content className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary-100 dark:bg-primary-900/20 rounded-lg">
                <User className="h-5 w-5 text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Project Manager</p>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {project.projectManager}
                </p>
              </div>
            </div>
          </Card.Content>
        </Card>
        <Card>
          <Card.Content className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary-100 dark:bg-primary-900/20 rounded-lg">
                <Calendar className="h-5 w-5 text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Target Date</p>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {project.targetDate}
                </p>
              </div>
            </div>
          </Card.Content>
        </Card>
        <Card>
          <Card.Content className="p-4">
            <ComplianceBadge
              status={
                project.compliance >= 90 ? 'green' : project.compliance >= 70 ? 'amber' : 'red'
              }
            >
              {project.compliance}% Compliant
            </ComplianceBadge>
          </Card.Content>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview">
        <Tabs.List>
          <Tabs.Trigger value="overview">Overview</Tabs.Trigger>
          <Tabs.Trigger value="documents">
            Documents ({project.documents.length})
          </Tabs.Trigger>
          <Tabs.Trigger value="findings">
            Findings ({project.findings.length})
          </Tabs.Trigger>
        </Tabs.List>

        {/* Overview Tab */}
        <Tabs.Content value="overview" className="mt-6 space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <Card.Header>
                <Card.Title>Project Details</Card.Title>
              </Card.Header>
              <Card.Content>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Location</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {project.location}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Budget</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {project.budget}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Start Date</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {project.startDate}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Target Completion</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {project.targetDate}
                    </p>
                  </div>
                </div>
              </Card.Content>
            </Card>

            <Card>
              <Card.Header>
                <Card.Title>Compliance Summary</Card.Title>
              </Card.Header>
              <Card.Content>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Overall Score
                      </span>
                      <span className="text-sm font-medium">{project.compliance}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-success-600 h-2 rounded-full"
                        style={{ width: `${project.compliance}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-4 pt-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-success-600 dark:text-success-400">
                        {project.findings.filter((f) => f.severity === 'green').length}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Compliant</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                        {project.findings.filter((f) => f.severity === 'amber').length}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Needs Review</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-danger-600 dark:text-danger-400">
                        {project.findings.filter((f) => f.severity === 'red').length}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Critical</p>
                    </div>
                  </div>
                </div>
              </Card.Content>
            </Card>
          </div>
        </Tabs.Content>

        {/* Documents Tab */}
        <Tabs.Content value="documents" className="mt-6">
          <Card>
            <Card.Header>
              <Card.Title>Documents</Card.Title>
              <Button variant="primary" size="sm" leftIcon={<Upload className="h-4 w-4" />}>
                Upload
              </Button>
            </Card.Header>
            <Card.Content className="p-0">
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {project.documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3 flex-1">
                      <FileText className="h-10 w-10 text-primary-600 dark:text-primary-400" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {doc.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {doc.size} • Uploaded by {doc.uploadedBy} on {doc.uploadedAt}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge
                        variant="secondary"
                        className={
                          doc.status === 'processed'
                            ? 'bg-success-100 dark:bg-success-900/20 text-success-700 dark:text-success-300'
                            : 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300'
                        }
                      >
                        {doc.status === 'processed' ? 'Processed' : 'Processing'}
                      </Badge>
                      <Button variant="ghost" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </Card.Content>
          </Card>
        </Tabs.Content>

        {/* Findings Tab */}
        <Tabs.Content value="findings" className="mt-6">
          <Card>
            <Card.Header>
              <Card.Title>Findings</Card.Title>
            </Card.Header>
            <Card.Content className="p-0">
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {project.findings.map((finding) => (
                  <div
                    key={finding.id}
                    className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer"
                    onClick={() => navigate(`/findings/${finding.id}`)}
                  >
                    <div className="flex items-start gap-3">
                      <ComplianceBadge status={finding.severity}>
                        {finding.severity.toUpperCase()}
                      </ComplianceBadge>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                          {finding.title}
                        </p>
                        <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                          <span>{finding.category}</span>
                          <span>•</span>
                          <Badge
                            variant="secondary"
                            className={findingStatusColors[finding.status]}
                            style={{ fontSize: '0.625rem', padding: '0.125rem 0.5rem' }}
                          >
                            {finding.status === 'in-review' ? 'In Review' : finding.status}
                          </Badge>
                          <span>•</span>
                          <span>{finding.createdAt}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card.Content>
          </Card>
        </Tabs.Content>
      </Tabs>
    </div>
  )
}
