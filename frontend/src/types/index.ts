export type ProjectStatus =
  | 'created'
  | 'uploaded'
  | 'parsed'
  | 'planned'
  | 'writing'
  | 'formatting'
  | 'reviewing'
  | 'revision'
  | 'completed'
  | 'failed'
  | 'paused'

export type StepStatus = 'pending' | 'running' | 'waiting_user' | 'completed' | 'failed' | 'skipped'

export interface ThesisProject {
  id: number
  title: string
  author: string
  major: string
  school: string
  status: ProjectStatus
  current_step: string
  step_statuses: Record<string, StepStatus>
  created_at: string
  updated_at: string
}

export interface ChatIntent {
  message: string
  intent: string
  scope?: string
  protect_others: boolean
  protect_format: boolean
  memory_action?: string
  parsed_task: Record<string, unknown>
  agent_reply: string
}

export interface ReviewReport {
  id: number
  project_id: number
  summary: string
  checks: Record<string, unknown>
  allow_export: boolean
  blocked_reasons: string[]
  created_at: string
}
