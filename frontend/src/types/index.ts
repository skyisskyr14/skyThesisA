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
  target?: string
  requirement: string
  protect_others: boolean
  protect_format: boolean
  should_create_rule: boolean
  memory_action?: string
  parsed_task: Record<string, unknown>
  agent_reply: string
}

export interface ReviewResult {
  report_id: number
  project_id: number
  passed: boolean
  allow_export: boolean
  score: number
  blocked_reasons: string[]
  warnings: string[]
  matched_rules: Record<string, unknown>[]
  auto_fix_suggestions: string[]
  checks: Record<string, unknown>
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


export interface TemplateAnalysisResult {
  id: number
  project_id: number
  file_id?: number
  template_type: 'instruction_only' | 'sample_paper' | 'mixed' | 'unknown'
  confidence: number
  rules_json: Record<string, any>
  conflicts_json: any[]
  warnings_json: any[]
  source_evidence_json: any[]
  applied: boolean
  created_at: string
}
