import React, { useState, useRef, useEffect } from 'react'
import { Card, Button, Textarea, Select, Badge } from '@/components/ui'
import {
  Send,
  Bot,
  User as UserIcon,
  FileText,
  Sparkles,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  specialist?: string
  findings?: Array<{
    severity: 'red' | 'amber' | 'green'
    text: string
  }>
}

const specialistAgents = [
  { value: 'general', label: 'General Compliance', icon: '🏗️' },
  { value: 'fire-safety', label: 'Fire Safety (Part B)', icon: '🔥' },
  { value: 'structure', label: 'Structure (Part A)', icon: '🏛️' },
  { value: 'energy', label: 'Energy (Part L)', icon: '⚡' },
  { value: 'ventilation', label: 'Ventilation (Part F)', icon: '💨' },
  { value: 'accessibility', label: 'Accessibility (Part M)', icon: '♿' },
]

// Mock messages
const initialMessages: Message[] = [
  {
    id: '1',
    role: 'assistant',
    content: 'Hello! I\'m your AI compliance assistant. I can help you check building regulations compliance, answer questions about specific requirements, and review your documents. Which specialist area would you like to focus on?',
    timestamp: '10:00 AM',
  },
]

export function Chat() {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [input, setInput] = useState('')
  const [selectedSpecialist, setSelectedSpecialist] = useState('general')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: getMockResponse(input, selectedSpecialist),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        specialist: specialistAgents.find((s) => s.value === selectedSpecialist)?.label,
        findings: getMockFindings(input),
      }
      setMessages((prev) => [...prev, assistantMessage])
      setIsTyping(false)
    }, 1500)
  }

  const getMockResponse = (query: string, specialist: string): string => {
    if (query.toLowerCase().includes('fire')) {
      return 'Based on Approved Document B (Fire Safety), I\'ve analyzed your query. For means of escape, you need to ensure that:\n\n1. Travel distances do not exceed maximum limits\n2. Stairwells have minimum width requirements\n3. Fire doors are properly specified\n4. Emergency lighting is adequately provided\n\nWould you like me to review a specific document for fire safety compliance?'
    }
    if (query.toLowerCase().includes('energy') || query.toLowerCase().includes('insulation')) {
      return 'Regarding Part L (Conservation of fuel and power), your building must meet specific U-value requirements:\n\n- Walls: 0.18 W/m²K\n- Roof: 0.11 W/m²K\n- Floors: 0.13 W/m²K\n- Windows: 1.2 W/m²K\n\nI can help you review your energy calculations and SAP assessments. Upload your documents for a detailed analysis.'
    }
    return `I understand you're asking about compliance requirements. As the ${specialistAgents.find(s => s.value === specialist)?.label} specialist, I can help you with:\n\n• Reviewing documents against regulations\n• Identifying potential compliance issues\n• Providing guidance on requirements\n• Generating compliance reports\n\nPlease upload your documents or ask me specific questions about the regulations.`
  }

  const getMockFindings = (query: string): Message['findings'] => {
    if (query.toLowerCase().includes('fire')) {
      return [
        { severity: 'red', text: 'Fire door specifications missing' },
        { severity: 'amber', text: 'Travel distances need verification' },
        { severity: 'green', text: 'Emergency lighting properly specified' },
      ]
    }
    return undefined
  }

  return (
    <div className="h-[calc(100vh-12rem)] flex flex-col space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">AI Assistant</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Get instant compliance guidance from specialist AI agents
          </p>
        </div>
        <div className="w-full sm:w-64">
          <Select
            value={selectedSpecialist}
            onChange={(e) => setSelectedSpecialist(e.target.value)}
          >
            {specialistAgents.map((agent) => (
              <option key={agent.value} value={agent.value}>
                {agent.icon} {agent.label}
              </option>
            ))}
          </Select>
        </div>
      </div>

      {/* Chat Area */}
      <Card className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
            >
              {/* Avatar */}
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.role === 'user'
                    ? 'bg-primary-600 dark:bg-primary-500'
                    : 'bg-purple-600 dark:bg-purple-500'
                }`}
              >
                {message.role === 'user' ? (
                  <UserIcon className="h-5 w-5 text-white" />
                ) : (
                  <Bot className="h-5 w-5 text-white" />
                )}
              </div>

              {/* Message Content */}
              <div
                className={`flex-1 max-w-2xl ${
                  message.role === 'user' ? 'text-right' : 'text-left'
                }`}
              >
                <div
                  className={`inline-block rounded-lg px-4 py-2 ${
                    message.role === 'user'
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                  }`}
                >
                  {message.specialist && (
                    <div className="flex items-center gap-2 mb-2 text-xs opacity-75">
                      <Sparkles className="h-3 w-3" />
                      <span>{message.specialist}</span>
                    </div>
                  )}
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>

                {/* Findings */}
                {message.findings && message.findings.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <p className="text-xs font-medium text-gray-500 dark:text-gray-400">
                      Quick Findings:
                    </p>
                    {message.findings.map((finding, idx) => (
                      <div
                        key={idx}
                        className="flex items-start gap-2 text-sm bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700"
                      >
                        {finding.severity === 'red' && (
                          <AlertTriangle className="h-4 w-4 text-danger-600 dark:text-danger-400 flex-shrink-0 mt-0.5" />
                        )}
                        {finding.severity === 'amber' && (
                          <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                        )}
                        {finding.severity === 'green' && (
                          <CheckCircle className="h-4 w-4 text-success-600 dark:text-success-400 flex-shrink-0 mt-0.5" />
                        )}
                        <span className="text-gray-700 dark:text-gray-300">{finding.text}</span>
                      </div>
                    ))}
                  </div>
                )}

                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {message.timestamp}
                </p>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center">
                <Bot className="h-5 w-5 text-white" />
              </div>
              <div className="bg-gray-100 dark:bg-gray-700 rounded-lg px-4 py-3">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.2s' }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.4s' }}
                  ></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="flex gap-3">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
              placeholder="Ask about building regulations, upload documents, or request compliance checks..."
              rows={2}
              className="flex-1"
              disabled={isTyping}
            />
            <Button
              variant="primary"
              onClick={handleSend}
              disabled={!input.trim() || isTyping}
              className="self-end"
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </Card>

      {/* Quick Actions */}
      <Card>
        <Card.Content className="p-4">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Quick Actions:
          </p>
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                setInput('What are the fire safety requirements for stairwells?')
              }
            >
              Fire Safety Requirements
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setInput('Check Part L energy performance calculations')}
            >
              Energy Performance
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setInput('Review accessibility compliance Part M')}
            >
              Accessibility Check
            </Button>
            <Button variant="outline" size="sm" leftIcon={<FileText className="h-4 w-4" />}>
              Upload Document
            </Button>
          </div>
        </Card.Content>
      </Card>
    </div>
  )
}
