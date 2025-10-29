import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Button, Input, Select, Badge, ComplianceBadge, EmptyState } from '@/components/ui'
import { FolderKanban, Plus, Search, Filter, MoreVertical, Trash2, Edit } from 'lucide-react'

interface Project {
  id: string
  name: string
  description: string
  status: 'active' | 'completed' | 'on-hold' | 'archived'
  compliance: number
  documents: number
  findings: number
  createdAt: string
  updatedAt: string
}

// Mock data - will be replaced with API calls
const mockProjects: Project[] = [
  {
    id: '1',
    name: 'Royal Hospital Extension',
    description: 'Major extension to existing hospital facility with new emergency department',
    status: 'active',
    compliance: 92,
    documents: 28,
    findings: 5,
    createdAt: '2025-01-15',
    updatedAt: '2 hours ago',
  },
  {
    id: '2',
    name: 'City Centre Office Block',
    description: 'Grade A office development with retail ground floor',
    status: 'active',
    compliance: 78,
    documents: 15,
    findings: 12,
    createdAt: '2025-02-01',
    updatedAt: '1 day ago',
  },
  {
    id: '3',
    name: 'Residential Tower Phase 2',
    description: '25-storey residential tower with amenities',
    status: 'completed',
    compliance: 95,
    documents: 42,
    findings: 2,
    createdAt: '2024-11-20',
    updatedAt: '3 days ago',
  },
  {
    id: '4',
    name: 'School Refurbishment',
    description: 'Complete renovation of primary school building',
    status: 'on-hold',
    compliance: 65,
    documents: 8,
    findings: 18,
    createdAt: '2025-01-10',
    updatedAt: '1 week ago',
  },
]

const statusColors: Record<Project['status'], { bg: string; text: string; label: string }> = {
  active: { bg: 'bg-success-100 dark:bg-success-900/20', text: 'text-success-700 dark:text-success-300', label: 'Active' },
  completed: { bg: 'bg-primary-100 dark:bg-primary-900/20', text: 'text-primary-700 dark:text-primary-300', label: 'Completed' },
  'on-hold': { bg: 'bg-amber-100 dark:bg-amber-900/20', text: 'text-amber-700 dark:text-amber-300', label: 'On Hold' },
  archived: { bg: 'bg-gray-100 dark:bg-gray-900/20', text: 'text-gray-700 dark:text-gray-300', label: 'Archived' },
}

export function Projects() {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [projects] = useState<Project[]>(mockProjects)

  const filteredProjects = projects.filter((project) => {
    const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter
    return matchesSearch && matchesStatus
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Projects</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage and track your compliance projects
          </p>
        </div>
        <Button
          variant="primary"
          leftIcon={<Plus className="h-5 w-5" />}
          onClick={() => navigate('/projects/new')}
        >
          New Project
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <Card.Content className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search projects..."
                leftIcon={<Search className="h-4 w-4" />}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="w-full sm:w-48">
              <Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                leftIcon={<Filter className="h-4 w-4" />}
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="on-hold">On Hold</option>
                <option value="archived">Archived</option>
              </Select>
            </div>
          </div>
        </Card.Content>
      </Card>

      {/* Projects List */}
      {filteredProjects.length === 0 ? (
        <Card>
          <Card.Content className="py-12">
            <EmptyState
              icon={<FolderKanban className="h-12 w-12" />}
              title="No projects found"
              description={
                searchTerm || statusFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Get started by creating your first project'
              }
              action={
                !searchTerm && statusFilter === 'all'
                  ? {
                      label: 'Create Project',
                      onClick: () => navigate('/projects/new'),
                      variant: 'primary',
                      leftIcon: <Plus className="h-4 w-4" />,
                    }
                  : undefined
              }
            />
          </Card.Content>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredProjects.map((project) => (
            <Card key={project.id} className="hover:shadow-md transition-shadow">
              <Card.Content className="p-6">
                <div className="flex items-start justify-between">
                  <div
                    className="flex-1 cursor-pointer"
                    onClick={() => navigate(`/projects/${project.id}`)}
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-12 h-12 bg-primary-100 dark:bg-primary-900/20 rounded-lg flex items-center justify-center">
                        <FolderKanban className="h-6 w-6 text-primary-600 dark:text-primary-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                          {project.name}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                          {project.description}
                        </p>
                        <div className="flex flex-wrap items-center gap-3">
                          <Badge
                            variant="secondary"
                            className={`${statusColors[project.status].bg} ${statusColors[project.status].text}`}
                          >
                            {statusColors[project.status].label}
                          </Badge>
                          <ComplianceBadge
                            status={
                              project.compliance >= 90
                                ? 'green'
                                : project.compliance >= 70
                                ? 'amber'
                                : 'red'
                            }
                          >
                            {project.compliance}% Compliant
                          </ComplianceBadge>
                          <span className="text-sm text-gray-500 dark:text-gray-400">
                            {project.documents} documents
                          </span>
                          <span className="text-sm text-gray-500 dark:text-gray-400">
                            {project.findings} findings
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex-shrink-0 ml-4">
                    <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
                      <MoreVertical className="h-5 w-5" />
                    </button>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                    <span>Created {project.createdAt}</span>
                    <span>Updated {project.updatedAt}</span>
                  </div>
                </div>
              </Card.Content>
            </Card>
          ))}
        </div>
      )}

      {/* Stats summary */}
      <Card>
        <Card.Content className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Projects</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{projects.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Active</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {projects.filter((p) => p.status === 'active').length}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Documents</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {projects.reduce((sum, p) => sum + p.documents, 0)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Avg Compliance</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {Math.round(projects.reduce((sum, p) => sum + p.compliance, 0) / projects.length)}%
              </p>
            </div>
          </div>
        </Card.Content>
      </Card>
    </div>
  )
}
