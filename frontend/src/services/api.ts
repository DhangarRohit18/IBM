/**
 * LEGACYX — Base HTTP API Client & Types (Phase 1, 2 & 3).
 *
 * All API calls from the frontend must go through this client.
 */

const API_BASE = '/api/v1'

export interface ApiError {
  name: 'ApiError'
  status: number
  body: unknown
  message: string
}

export function createApiError(status: number, body: unknown, message: string): ApiError {
  return { name: 'ApiError', status, body, message }
}

export function isApiError(value: unknown): value is ApiError {
  return (
    typeof value === 'object' &&
    value !== null &&
    (value as ApiError).name === 'ApiError'
  )
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`

  const isFormData = options?.body instanceof FormData
  const headers: Record<string, string> = { ...options?.headers as Record<string, string> }
  if (!isFormData && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json'
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (!response.ok) {
    let body: unknown
    try {
      body = await response.json()
    } catch {
      body = await response.text()
    }
    throw createApiError(response.status, body, `HTTP ${response.status}: ${url}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

// ── Phase 1 Health Types ──────────────────────────────────────────────────────

export interface HealthStatusItem {
  name: string
  status: string
  message?: string | null
}

export interface HealthResponse {
  status: string
  app_name: string
  app_version: string
  environment: string
  timestamp: string
  services: HealthStatusItem[]
}

// ── Phase 2 Types ─────────────────────────────────────────────────────────────

export interface Project {
  id: string
  owner_id: string
  name: string
  description?: string | null
  status: 'CREATED' | 'INGESTING' | 'READY' | 'ANALYZING' | 'ANALYZED' | 'FAILED'
  created_at: string
  updated_at: string
}

export interface IngestionRun {
  id: string
  repository_id: string
  status: 'STARTED' | 'COMPLETED' | 'FAILED'
  started_at: string
  completed_at?: string | null
  files_discovered: number
  directories_discovered: number
  bytes_extracted: number
  error_code?: string | null
  error_message?: string | null
}

export interface Repository {
  id: string
  project_id: string
  original_filename: string
  artifact_size: number
  sha256: string
  status: 'UPLOADED' | 'VALIDATING' | 'EXTRACTING' | 'INDEXING' | 'COMPLETED' | 'FAILED'
  created_at: string
  updated_at: string
  latest_ingestion_run?: IngestionRun | null
}

export interface RepositoryFile {
  id: string
  repository_id: string
  relative_path: string
  filename: string
  extension: string
  size_bytes: number
  is_directory: boolean
  checksum?: string | null
}

export interface TechnologyEvidence {
  name: string
  evidence: string[]
}

export interface RepositoryManifest {
  repository: {
    id: string
    original_filename: string
    artifact_size: number
    sha256: string
  }
  summary: {
    total_files: number
    total_directories: number
    total_bytes: number
  }
  extension_breakdown: Record<string, number>
  technologies: TechnologyEvidence[]
  key_files: string[]
}

export interface FileContentResponse {
  relative_path: string
  filename: string
  extension: string
  size_bytes: number
  content: string
  is_truncated: boolean
}

// ── Phase 3 System X-Ray Types ────────────────────────────────────────────────

export interface AnalysisRun {
  id: string
  repository_id: string
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED'
  parser_name: string
  parser_version: string
  files_analyzed: number
  packages_count: number
  classes_count: number
  interfaces_count: number
  enums_count: number
  methods_count: number
  fields_count: number
  relationships_count: number
  error_code?: string | null
  error_message?: string | null
  started_at: string
  completed_at?: string | null
  created_at: string
}

export interface CodePackage {
  id: string
  analysis_id: string
  name: string
  entity_count: number
  created_at: string
}

export interface CodeMethod {
  id: string
  entity_id: string
  name: string
  return_type: string
  parameters: Array<{ name: string; type: string }>
  modifiers: string[]
  annotations: Array<{ name: string; element_pairs: Record<string, string> }>
  is_constructor: boolean
  line_start: number
  line_end: number
  file_path?: string
  line_number?: number
}

export interface CodeField {
  id: string
  entity_id: string
  name: string
  field_type: string
  modifiers: string[]
  annotations: Array<{ name: string; element_pairs: Record<string, string> }>
  line_start: number
  line_end: number
  file_path?: string
  line_number?: number
}

export interface CodeRelationship {
  id: string
  analysis_id: string
  source_entity_id: string
  source_method_id?: string | null
  target_entity_id?: string | null
  target_entity_name: string
  relationship_type: 'IMPORTS' | 'EXTENDS' | 'IMPLEMENTS' | 'DEPENDS_ON' | 'CALLS'
  relative_file_path: string
  line_number: number
  source_construct: string
  evidence_reason: string
  is_resolved: boolean
}

export interface CodeEntity {
  id: string
  analysis_id: string
  repository_id: string
  package_id?: string | null
  entity_type: 'CLASS' | 'INTERFACE' | 'ENUM'
  name: string
  fully_qualified_name: string
  relative_file_path: string
  line_start: number
  line_end: number
  extends_name?: string | null
  implements_names: string[]
  annotations: Array<{ name: string; element_pairs: Record<string, string> }>
  modifiers: string[]
  component_type: 'CONTROLLER' | 'SERVICE' | 'REPOSITORY' | 'ENTITY' | 'CONFIGURATION' | 'COMPONENT' | 'UTILITY' | 'FRAMEWORK_OTHER'
  classification_evidence: string[]
  created_at: string
}

export interface CodeEntitySummary {
  id: string
  name: string
  qualified_name: string
  package_name: string
  kind: string
  component_type: string
  classification_evidence: string[]
  methods_count: number
  fields_count: number
  file_path: string
}

export interface CodeEntityDetail {
  entity: CodeEntity
  package?: CodePackage | null
  methods: CodeMethod[]
  fields: CodeField[]
  outgoing_relationships: CodeRelationship[]
  incoming_relationships: CodeRelationship[]
}

export interface AnalysisSummary {
  analysis_id: string
  repository_id: string
  total_files: number
  total_packages: number
  total_classes: number
  total_methods: number
  total_fields: number
  total_relationships: number
  packages: CodePackage[]
  classes: CodeEntitySummary[]
  component_breakdown: Record<string, number>
  relationships_breakdown: Array<{ type: string; count: number }>
  calls_resolution: { total: number; resolved: number; unresolved: number }
}

export type CodeAnalysisSummary = AnalysisSummary

export interface GraphNode {
  id: string
  name: string
  qualified_name: string
  package_name: string
  kind: string
  component_type: string
  classification_evidence: string[]
  file_path: string
}

export interface GraphEdge {
  id: string
  source_id: string
  target_id: string
  type: string
  line_number: number
  source_construct: string
  evidence_reason: string
  is_resolved: boolean
}

export interface GraphResponse {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export type CodeGraphData = GraphResponse
export type CodeGraphNode = GraphNode
export type CodeGraphEdge = GraphEdge

export interface AnalysisSearchResult {
  classes: CodeEntitySummary[]
  methods: CodeMethod[]
  fields: CodeField[]
  packages: CodePackage[]
}

// ── API Surface ───────────────────────────────────────────────────────────────

export const api = {
  get: <T>(path: string) => request<T>(path, { method: 'GET' }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'POST',
      body: body instanceof FormData ? body : JSON.stringify(body),
    }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'PUT', body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),

  // Phase 2 methods
  projects: {
    list: () => request<Project[]>('/projects'),
    create: (data: { name: string; description?: string }) =>
      request<Project>('/projects', { method: 'POST', body: JSON.stringify(data) }),
    get: (id: string) => request<Project>(`/projects/${id}`),
    uploadRepository: (projectId: string, file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return request<Repository>(`/projects/${projectId}/repositories`, {
        method: 'POST',
        body: formData,
      })
    },
  },

  repositories: {
    get: (id: string) => request<Repository>(`/repositories/${id}`),
    ingest: (id: string) => request<Repository>(`/repositories/${id}/ingest`, { method: 'POST' }),
    files: (id: string) => request<RepositoryFile[]>(`/repositories/${id}/files`),
    manifest: (id: string) => request<RepositoryManifest>(`/repositories/${id}/manifest`),
    ingestionRuns: (id: string) => request<IngestionRun[]>(`/repositories/${id}/ingestion`),
    fileContent: (id: string, path: string) =>
      request<FileContentResponse>(`/repositories/${id}/files/content?path=${encodeURIComponent(path)}`),
  },

  // Phase 3 System X-Ray methods
  analysis: {
    start: (repositoryId: string) =>
      request<AnalysisRun>(`/repositories/${repositoryId}/analysis`, { method: 'POST' }),
    trigger: (repositoryId: string) =>
      request<AnalysisRun>(`/repositories/${repositoryId}/analysis`, { method: 'POST' }),
    listRuns: (repositoryId: string) =>
      request<AnalysisRun[]>(`/repositories/${repositoryId}/analysis`),
    getRun: (analysisId: string) => request<AnalysisRun>(`/analysis/${analysisId}`),
    summary: (analysisId: string) => request<AnalysisSummary>(`/analysis/${analysisId}/summary`),
    getSummary: (analysisId: string) => request<AnalysisSummary>(`/analysis/${analysisId}/summary`),
    packages: (analysisId: string) => request<CodePackage[]>(`/analysis/${analysisId}/packages`),
    classes: (analysisId: string, component?: string, q?: string) => {
      const params = new URLSearchParams()
      if (component) params.append('component', component)
      if (q) params.append('q', q)
      const queryStr = params.toString() ? `?${params.toString()}` : ''
      return request<CodeEntitySummary[]>(`/analysis/${analysisId}/classes${queryStr}`)
    },
    classDetail: (classId: string) =>
      request<CodeEntityDetail>(`/analysis/classes/${classId}`),
    getClassDetail: (classId: string) =>
      request<CodeEntityDetail>(`/analysis/classes/${classId}`),
    relationships: (analysisId: string) =>
      request<CodeRelationship[]>(`/analysis/${analysisId}/relationships`),
    graph: (analysisId: string, pkg?: string, component?: string) => {
      const params = new URLSearchParams()
      if (pkg) params.append('package', pkg)
      if (component) params.append('component', component)
      const queryStr = params.toString() ? `?${params.toString()}` : ''
      return request<GraphResponse>(`/analysis/${analysisId}/graph${queryStr}`)
    },
    getGraph: (analysisId: string, pkg?: string, component?: string) => {
      const params = new URLSearchParams()
      if (pkg) params.append('package', pkg)
      if (component) params.append('component', component)
      const queryStr = params.toString() ? `?${params.toString()}` : ''
      return request<GraphResponse>(`/analysis/${analysisId}/graph${queryStr}`)
    },
    search: (analysisId: string, q: string) =>
      request<AnalysisSearchResult>(`/analysis/${analysisId}/search?q=${encodeURIComponent(q)}`),
  },

  // Phase 4 Business Rules methods
  businessRules: {
    list: (analysisId: string, ruleType?: string, status?: string, q?: string) => {
      const params = new URLSearchParams()
      if (ruleType) params.append('rule_type', ruleType)
      if (status) params.append('status', status)
      if (q) params.append('q', q)
      const queryStr = params.toString() ? `?${params.toString()}` : ''
      return request<BusinessRule[]>(`/analysis/${analysisId}/business-rules${queryStr}`)
    },
    getDetail: (ruleId: string) => request<BusinessRule>(`/business-rules/${ruleId}`),
    explain: (ruleId: string) => request<AIExplanationResponse>(`/business-rules/${ruleId}/explain`, { method: 'POST' }),
    review: (ruleId: string, status: 'REVIEWED' | 'REJECTED', reviewNotes?: string) =>
      request<BusinessRule>(`/business-rules/${ruleId}/review`, {
        method: 'POST',
        body: JSON.stringify({ status, reviewed_by: 'engineer', review_notes: reviewNotes }),
      }),
  },

  // Phase 5 Impact Analysis methods
  impact: {
    analyze: (
      analysisId: string,
      targetType: string,
      targetId: string,
      direction: 'forward' | 'reverse' = 'forward',
      maxDepth = 3
    ) => {
      const params = new URLSearchParams({
        target_type: targetType,
        target_id: targetId,
        direction,
        max_depth: maxDepth.toString(),
      })
      return request<ImpactAnalysisResponse>(`/analysis/${analysisId}/impact?${params.toString()}`)
    },
    explain: (
      analysisId: string,
      targetType: string,
      targetId: string,
      direction: 'forward' | 'reverse' = 'forward',
      maxDepth = 3
    ) => {
      return request<ImpactExplainResponse>(`/impact/explain`, {
        method: 'POST',
        body: JSON.stringify({
          analysis_id: analysisId,
          target_type: targetType,
          target_id: targetId,
          direction,
          max_depth: maxDepth,
        }),
      })
    },
  },


  // Phase 6 Modernization Strategy methods
  modernization: {
    evaluate: (analysisId: string) =>
      request<ModernizationStrategy[]>(`/analysis/${analysisId}/modernization/evaluate`, { method: 'POST' }),
    list: (analysisId: string, strategyType?: string, status?: string, q?: string) => {
      const params = new URLSearchParams()
      if (strategyType) params.append('strategy_type', strategyType)
      if (status) params.append('status', status)
      if (q) params.append('q', q)
      const queryStr = params.toString() ? `?${params.toString()}` : ''
      return request<ModernizationStrategy[]>(`/analysis/${analysisId}/modernization/strategies${queryStr}`)
    },
    getDetail: (id: string) => request<ModernizationStrategy>(`/modernization/strategies/${id}`),
    explain: (id: string) => request<StrategyExplainResponse>(`/modernization/strategies/${id}/explain`, { method: 'POST' }),
    override: (id: string, status: 'REVIEWED' | 'OVERRIDDEN', overrideStrategy?: string, notes?: string) =>
      request<ModernizationStrategy>(`/modernization/strategies/${id}/override`, {
        method: 'POST',
        body: JSON.stringify({
          status,
          user_override_strategy: overrideStrategy,
          user_name: 'lead_architect',
          notes,
        }),
      }),

    // Phase 7 Execution Plan methods
    generatePlans: (analysisId: string, targetEntityId?: string) => {
      const queryStr = targetEntityId ? `?target_entity_id=${targetEntityId}` : ''
      return request<ModernizationPlan[]>(`/analysis/${analysisId}/modernization/plans/generate${queryStr}`, { method: 'POST' })
    },
    listPlans: (analysisId: string, status?: string, q?: string) => {
      const params = new URLSearchParams()
      if (status) params.append('status', status)
      if (q) params.append('q', q)
      const queryStr = params.toString() ? `?${params.toString()}` : ''
      return request<ModernizationPlan[]>(`/analysis/${analysisId}/modernization/plans${queryStr}`)
    },
    getPlan: (id: string) => request<ModernizationPlan>(`/modernization/plans/${id}`),
    getTasks: (id: string) => request<ModernizationTask[]>(`/modernization/plans/${id}/tasks`),
    reviewPlan: (id: string, status: 'REVIEWED' | 'APPROVED' | 'REJECTED', notes?: string) =>
      request<ModernizationPlan>(`/modernization/plans/${id}/review`, {
        method: 'POST',
        body: JSON.stringify({ status, user_name: 'lead_architect', notes }),
      }),
    updateTaskStatus: (taskId: string, status: string) =>
      request<ModernizationTask>(`/modernization/tasks/${taskId}/status`, {
        method: 'POST',
        body: JSON.stringify({ status }),
      }),
    reorderTask: (taskId: string, newSequenceOrder: number) =>
      request<ModernizationTask[]>(`/modernization/tasks/${taskId}/reorder`, {
        method: 'POST',
        body: JSON.stringify({ new_sequence_order: newSequenceOrder }),
      }),
    explainPlan: (id: string) => request<PlanExplainResponse>(`/modernization/plans/${id}/explain`, { method: 'POST' }),

    // Phase 8 Controlled Code Transformation methods
    proposeTransformations: (planId: string) =>
      request<TransformationProposal[]>(`/modernization/plans/${planId}/transformations/propose`, { method: 'POST' }),
    listTransformations: (planId: string) =>
      request<TransformationProposal[]>(`/modernization/plans/${planId}/transformations`),
    getTransformationDetail: (id: string) =>
      request<TransformationProposal>(`/transformations/${id}`),
    getTransformationArtifacts: (id: string) =>
      request<TransformationArtifact[]>(`/transformations/${id}/artifacts`),
    reviewTransformation: (id: string, status: 'REVIEWED' | 'APPROVED' | 'REJECTED', notes?: string) =>
      request<TransformationProposal>(`/transformations/${id}/review`, {
        method: 'POST',
        body: JSON.stringify({ status, user_name: 'lead_architect', notes }),
      }),
    applyTransformation: (id: string, userName = 'lead_architect') =>
      request<TransformationProposal>(`/transformations/${id}/apply`, {
        method: 'POST',
        body: JSON.stringify({ user_name: userName }),
      }),
  },
}

// ── Phase 4 Types ─────────────────────────────────────────────────────────────

export type RuleType = 'VALIDATION' | 'CONDITIONAL' | 'THRESHOLD' | 'CALCULATION' | 'ACTION' | 'STATE_TRANSITION'
export type RuleStatus = 'EXTRACTED' | 'EXPLAINED' | 'REVIEWED' | 'REJECTED'
export type AIExplanationStatus = 'NOT_REQUESTED' | 'PENDING' | 'COMPLETED' | 'FAILED'

export interface RuleTraceStep {
  step_type: 'CONDITION' | 'DECISION_CONTEXT' | 'ACTION' | 'STATE_CHANGE'
  label: string
  details?: string
  line_number?: number
}

export interface BusinessRule {
  id: string
  analysis_id: string
  repository_id: string
  entity_id?: string
  method_id?: string
  rule_type: RuleType
  title: string
  status: RuleStatus

  condition_expression?: string
  action_expression?: string
  outcome_expression?: string
  threshold_value?: string
  threshold_operator?: string
  calculation_formula?: string
  previous_state?: string
  new_state?: string

  rule_trace: RuleTraceStep[]

  relative_file_path: string
  line_start: number
  line_end: number
  source_construct: string
  extraction_reason: string

  ai_explanation?: string
  ai_explanation_status: AIExplanationStatus

  reviewed_by?: string
  reviewed_at?: string
  review_notes?: string
  created_at: string
  updated_at: string
}

export interface AIExplanationResponse {
  rule_id: string
  status: AIExplanationStatus
  explanation?: string
  error_message?: string
}

// ── Phase 5 Types ─────────────────────────────────────────────────────────────

export interface ImpactTargetInfo {
  id: string
  type: string
  name: string
  fully_qualified_name: string
  file_path: string
  description: string
}

export interface AffectedComponent {
  id: string
  name: string
  fully_qualified_name: string
  entity_type: string
  component_type: string
  relative_file_path: string
  line_start: number
  line_end: number
  depth: number
  is_direct: boolean
  is_target?: boolean
}

export interface AffectedRule {
  id: string
  title: string
  rule_type: string
  status: string
  relative_file_path: string
  line_start: number
  line_end: number
  entity_id?: string
  method_id?: string
  condition_expression?: string
  action_expression?: string
  extraction_reason: string
  depth?: number
  is_target?: boolean
}

export interface ImpactPathStep {
  from_component: string
  from_id: string
  to_component: string
  to_id: string
  relationship_type: string
  depth: number
  file_path: string
  line_number: number
  evidence_reason: string
}

export interface ImpactSummary {
  direct_component_count: number
  transitive_component_count: number
  direct_rule_count: number
  transitive_rule_count: number
  total_impacted_nodes: number
}

export interface ImpactGraphEdge {
  id: string
  source: string
  target: string
  target_name: string
  type: string
  line_number: number
  relative_file_path: string
  source_construct: string
  evidence_reason: string
  is_resolved: boolean
}

export interface ImpactGraphData {
  nodes: AffectedComponent[]
  edges: ImpactGraphEdge[]
}

export interface ImpactAnalysisResponse {
  analysis_id: string
  target: ImpactTargetInfo
  direction: 'forward' | 'reverse'
  max_depth: number
  has_evidenced_impact: boolean
  status: string
  summary: ImpactSummary
  direct_affected_components: AffectedComponent[]
  transitive_affected_components: AffectedComponent[]
  direct_affected_rules: AffectedRule[]
  transitive_affected_rules: AffectedRule[]
  impact_paths: ImpactPathStep[]
  graph: ImpactGraphData
}

export interface ImpactExplainResponse {
  explanation: string
  status: string
}

// ── Phase 6 Types ─────────────────────────────────────────────────────────────

export interface ResponsibilityItem {
  category: string
  title: string
  description: string
  relative_file_path: string
  line_number: number
  evidence_reason: string
  source_snippet: string
}

export interface RulePreservationItem {
  id?: string
  title?: string
  rule_type?: string
  file_path?: string
  line_start?: number
  condition?: string
}

export interface DecisionTraceStep {
  step: number
  label: string
  detail: string
}

export interface QualitativeComparisonItem {
  dimension: string
  recommended_value: string
  alternative_value: string
}

export interface StrategyImpactSummary {
  direct_dependent_count: number
  transitive_dependent_count: number
  direct_dependents: string[]
  transitive_dependents: string[]
}

export interface ModernizationStrategy {
  id: string
  analysis_id: string
  repository_id: string
  entity_id: string
  entity_name: string
  relative_file_path: string

  recommended_strategy: string
  alternative_strategy?: string

  why_recommended: string
  why_alternative?: string
  what_not_to_change?: string

  decision_trace: DecisionTraceStep[]
  observed_responsibilities: ResponsibilityItem[]
  rules_to_preserve: RulePreservationItem[]
  impact_summary: StrategyImpactSummary
  qualitative_comparison: QualitativeComparisonItem[]

  status: 'PROPOSED' | 'REVIEWED' | 'OVERRIDDEN'
  user_override_strategy?: string
  user_override_by?: string
  user_override_at?: string
  user_override_notes?: string

  ai_explanation?: string
  ai_explanation_status: string

  created_at: string
  updated_at: string
}

export interface StrategyExplainResponse {
  explanation: string
  status: string
}

// ── Phase 7 Types ─────────────────────────────────────────────────────────────

export interface ModernizationTask {
  id: string
  plan_id: string
  sequence_order: number
  title: string
  description: string
  task_type: string
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'DEFERRED' | 'SKIPPED'
  target_component: string
  target_file_path: string
  depends_on_task_ids: string[]
  rule_ids: string[]
  evidence_references: Array<Record<string, any>>
  verification_checkpoint: Record<string, any>
  created_at: string
  updated_at: string
}

export interface ModernizationPlan {
  id: string
  analysis_id: string
  repository_id: string
  entity_id: string
  strategy_id?: string
  entity_name: string
  relative_file_path: string
  strategy_type: string
  summary: string
  status: 'PROPOSED' | 'REVIEWED' | 'APPROVED' | 'REJECTED'

  rules_to_preserve: Array<Record<string, any>>
  impact_summary: Record<string, any>
  verification_checkpoints: Array<Record<string, any>>

  tasks: ModernizationTask[]

  reviewed_by?: string
  reviewed_at?: string
  review_notes?: string

  ai_explanation?: string
  ai_explanation_status: string

  created_at: string
  updated_at: string
}

export interface PlanExplainResponse {
  explanation: string
  status: string
}

// ── Phase 8 Types ─────────────────────────────────────────────────────────────

export interface TransformationArtifact {
  id: string
  proposal_id: string
  artifact_category: 'EXTRACTED_CLASS' | 'EXTRACTED_INTERFACE' | 'FACADE' | 'ADAPTER' | 'REFACTORED_METHOD' | 'MIGRATED_CALLER' | 'SUPPORTING_TEST_STUB'
  target_file_path: string
  source_file_path: string
  source_line_start: number
  source_line_end: number
  generated_code: string
  diff_content: string
  rules_preserved: Array<Record<string, any>>
  evidence_references: Array<Record<string, any>>
  storage_relative_path?: string
  created_at: string
  updated_at: string
}

export interface TransformationProposal {
  id: string
  plan_id: string
  task_id: string
  analysis_id: string
  repository_id: string
  status: 'PROPOSED' | 'REVIEWED' | 'APPROVED' | 'APPLIED' | 'REJECTED'
  transformation_type: string
  target_entity: string
  summary: string
  specification: Record<string, any>
  rule_ids: string[]
  impacted_entity_ids: string[]

  artifacts: TransformationArtifact[]

  reviewed_by?: string
  reviewed_at?: string
  review_notes?: string

  applied_by?: string
  applied_at?: string
  storage_workspace_path?: string

  ai_proposal_status: string
  ai_proposal_summary?: string

  created_at: string
  updated_at: string
}

// ── Phase 9 Types ─────────────────────────────────────────────────────────────

export interface ValidationEvidence {
  id: string
  run_id: string
  phase_category: 'BUILD' | 'UNIT_TEST' | 'BEHAVIORAL_SCENARIO'
  status: string
  exit_code?: number
  stdout_content: string
  stderr_content: string
  command_executed: string
  execution_time_seconds: number
  produced_artifacts: Array<Record<string, any>>
  error_summary?: string
  created_at: string
}

export interface BehavioralScenario {
  id: string
  run_id: string
  business_rule_id: string
  rule_type: string
  scenario_name: string
  inputs: Record<string, any>
  legacy_expected_outputs: Record<string, any>
  modern_actual_outputs: Record<string, any>
  comparison_result: 'MATCH' | 'MISMATCH' | 'UNABLE_TO_VALIDATE'
  mismatch_details?: string
  created_at: string
}

export interface ValidationRun {
  id: string
  transformation_id: string
  analysis_id: string
  repository_id: string

  build_status: 'BUILD_PASS' | 'BUILD_FAIL' | 'BUILD_ENVIRONMENT_UNAVAILABLE'
  test_status: 'TEST_PASS' | 'TEST_FAIL' | 'TEST_ENVIRONMENT_UNAVAILABLE'
  behavioral_status: 'MATCH' | 'MISMATCH' | 'UNABLE_TO_VALIDATE'
  overall_status: 'VERIFIED' | 'FAILED' | 'UNABLE_TO_VALIDATE'
  review_status: 'PENDING' | 'REVIEWED' | 'VALIDATED'

  passed_scenarios: number
  failed_scenarios: number
  total_scenarios: number

  workspace_path?: string
  build_log_summary?: string
  test_log_summary?: string
  equivalence_summary?: string

  reviewed_by?: string
  reviewed_at?: string
  review_notes?: string

  ai_explanation?: string
  ai_explanation_status: string

  evidences: ValidationEvidence[]
  scenarios: BehavioralScenario[]

  created_at: string
  updated_at: string
}

export async function runValidation(proposalId: string): Promise<ValidationRun> {
  return request<ValidationRun>(`/transformations/${proposalId}/validation/run`, {
    method: 'POST',
  })
}

export async function getValidationRuns(proposalId: string): Promise<ValidationRun[]> {
  return request<ValidationRun[]>(`/transformations/${proposalId}/validation`)
}

export async function getValidationRun(runId: string): Promise<ValidationRun> {
  return request<ValidationRun>(`/validation/${runId}`)
}

export async function getValidationEvidence(runId: string): Promise<ValidationEvidence[]> {
  return request<ValidationEvidence[]>(`/validation/${runId}/evidence`)
}

export async function getValidationScenarios(runId: string): Promise<BehavioralScenario[]> {
  return request<BehavioralScenario[]>(`/validation/${runId}/scenarios`)
}

export async function reviewValidationRun(
  runId: string,
  status: 'REVIEWED' | 'VALIDATED',
  userName = 'qa_lead',
  notes?: string
): Promise<ValidationRun> {
  return request<ValidationRun>(`/validation/${runId}/review`, {
    method: 'POST',
    body: JSON.stringify({
      status,
      user_name: userName,
      notes,
    }),
  })
}

export async function explainValidationRun(runId: string): Promise<{ explanation: string; status: string }> {
  return request<{ explanation: string; status: string }>(`/validation/${runId}/explain`, {
    method: 'POST',
  })
}



