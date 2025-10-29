import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { Card, Button, ComplianceBadge, EmptyState } from '@/components/ui'
import {
  FolderKanban,
  FileText,
  AlertTriangle,
  TrendingUp,
  Plus,
  ArrowRight,
  Clock,
} from 'lucide-react'

interface StatCardProps {
  title: string
  value: string | number
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
  icon: React.ReactNode
}

function StatCard({ title, value, change, changeType, icon }: StatCardProps) {
  return (
    <Card>
      <Card.Content className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{title}</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
            {change && (
              <p
                className={`text-sm mt-2 ${
                  changeType === 'positive'
                    ? 'text-success-600 dark:text-success-400'
                    : changeType === 'negative'
                    ? 'text-danger-600 dark:text-danger-400'
                    : 'text-gray-600 dark:text-gray-400'
                }`}
              >
                {change}
              </p>
            )}
          </div>
          <div className="p-3 bg-primary-100 dark:bg-primary-900/20 rounded-lg">
            {icon}
          </div>
        </div>
      </Card.Content>
    </Card>
  )
}

export function Dashboard() {
  const navigate = useNavigate()
  const { user } = useAuth()

  // Mock data - will be replaced with real API calls
  const stats = {
    projects: 12,
    documents: 48,
    findings: 23,
    compliance: 87,
  }

  const recentProjects = [
    {
      id: '1',
      name: 'Royal Hospital Extension',
      status: 'active',
      compliance: 92,
      lastUpdated: '2 hours ago',
    },
    {
      id: '2',
      name: 'City Centre Office Block',
      status: 'active',
      compliance: 78,
      lastUpdated: '1 day ago',
    },
    {
      id: '3',
      name: 'Residential Tower Phase 2',
      status: 'review',
      compliance: 85,
      lastUpdated: '3 days ago',
    },
  ]

  const recentFindings = [
    {
      id: '1',
      severity: 'red' as const,
      title: 'Fire safety compliance issue in stairwell design',
      project: 'Royal Hospital Extension',
      category: 'Part B - Fire Safety',
    },
    {
      id: '2',
      severity: 'amber' as const,
      title: 'Ventilation requirements not fully specified',
      project: 'City Centre Office Block',
      category: 'Part F - Ventilation',
    },
    {
      id: '3',
      severity: 'green' as const,
      title: 'Structural calculations verified and approved',
      project: 'Residential Tower Phase 2',
      category: 'Part A - Structure',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Welcome header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Welcome back, {user?.firstName}!
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Here's an overview of your compliance projects
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Active Projects"
          value={stats.projects}
          change="+2 this month"
          changeType="positive"
          icon={<FolderKanban className="h-6 w-6 text-primary-600 dark:text-primary-400" />}
        />
        <StatCard
          title="Documents"
          value={stats.documents}
          change="+8 this week"
          changeType="positive"
          icon={<FileText className="h-6 w-6 text-primary-600 dark:text-primary-400" />}
        />
        <StatCard
          title="Open Findings"
          value={stats.findings}
          change="-5 resolved"
          changeType="positive"
          icon={<AlertTriangle className="h-6 w-6 text-primary-600 dark:text-primary-400" />}
        />
        <StatCard
          title="Compliance Score"
          value={`${stats.compliance}%`}
          change="+3% improvement"
          changeType="positive"
          icon={<TrendingUp className="h-6 w-6 text-primary-600 dark:text-primary-400" />}
        />
      </div>

      {/* Recent Projects and Findings */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Projects */}
        <Card>
          <Card.Header>
            <Card.Title>Recent Projects</Card.Title>
            <Button
              variant="ghost"
              size="sm"
              rightIcon={<Plus className="h-4 w-4" />}
              onClick={() => navigate('/projects/new')}
            >
              New Project
            </Button>
          </Card.Header>
          <Card.Content className="p-0">
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {recentProjects.map((project) => (
                <div
                  key={project.id}
                  className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
                  onClick={() => navigate(`/projects/${project.id}`)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {project.name}
                      </h4>
                      <div className="flex items-center mt-2 space-x-4">
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
                        <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                          <Clock className="h-3 w-3 mr-1" />
                          {project.lastUpdated}
                        </div>
                      </div>
                    </div>
                    <ArrowRight className="h-5 w-5 text-gray-400" />
                  </div>
                </div>
              ))}
            </div>
          </Card.Content>
          <Card.Footer>
            <Button
              variant="ghost"
              fullWidth
              onClick={() => navigate('/projects')}
            >
              View all projects
            </Button>
          </Card.Footer>
        </Card>

        {/* Recent Findings */}
        <Card>
          <Card.Header>
            <Card.Title>Recent Findings</Card.Title>
            <Button
              variant="ghost"
              size="sm"
              rightIcon={<ArrowRight className="h-4 w-4" />}
              onClick={() => navigate('/findings')}
            >
              View All
            </Button>
          </Card.Header>
          <Card.Content className="p-0">
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {recentFindings.map((finding) => (
                <div
                  key={finding.id}
                  className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
                  onClick={() => navigate(`/findings/${finding.id}`)}
                >
                  <div className="flex items-start space-x-3">
                    <ComplianceBadge status={finding.severity}>
                      {finding.severity.toUpperCase()}
                    </ComplianceBadge>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {finding.title}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {finding.project} • {finding.category}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card.Content>
          <Card.Footer>
            <Button
              variant="ghost"
              fullWidth
              onClick={() => navigate('/findings')}
            >
              View all findings
            </Button>
          </Card.Footer>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <Card.Header>
          <Card.Title>Quick Actions</Card.Title>
        </Card.Header>
        <Card.Content>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button
              variant="outline"
              leftIcon={<FolderKanban className="h-5 w-5" />}
              onClick={() => navigate('/projects/new')}
              fullWidth
            >
              Create New Project
            </Button>
            <Button
              variant="outline"
              leftIcon={<FileText className="h-5 w-5" />}
              onClick={() => navigate('/documents/upload')}
              fullWidth
            >
              Upload Documents
            </Button>
            <Button
              variant="outline"
              leftIcon={<AlertTriangle className="h-5 w-5" />}
              onClick={() => navigate('/chat')}
              fullWidth
            >
              Start Compliance Check
            </Button>
          </div>
        </Card.Content>
      </Card>
    </div>
  )
}
