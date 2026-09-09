import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Folder,
  HardDrive,
  FileText,
  Code2,
  ArrowLeft,
  RefreshCw,
  Cpu,
  BookMarked,
  GitBranch,
  Map,
  GitFork,
  FlaskConical,
} from 'lucide-react'
import { api, type Project, type Repository, type RepositoryManifest } from '@/services/api'
import { RepositoryUploadCard } from '../repositories/RepositoryUploadCard'
import { IngestionProgressCard } from '../repositories/IngestionProgressCard'
import { RepositoryOverviewTab } from '../repositories/RepositoryOverviewTab'
import { RepositoryManifestTab } from '../repositories/RepositoryManifestTab'
import { FileExplorerTab } from '../repositories/FileExplorerTab'
import { SystemXRayPage } from '../analysis/SystemXRayPage'
import { BusinessRulesPage } from '../business_rules/BusinessRulesPage'
import { ImpactPage } from '../impact/ImpactPage'
import { ModernizationPage } from '../modernization/ModernizationPage'
import { ModernizationPlanPage } from '../modernization/ModernizationPlanPage'
import { TransformationStudioPage } from '../modernization/TransformationStudioPage'
import { ValidationWorkspacePage } from '../modernization/ValidationWorkspacePage'

export function ProjectWorkspacePage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [project, setProject] = useState<Project | null>(null)
  const [repository, setRepository] = useState<Repository | null>(null)
  const [manifest, setManifest] = useState<RepositoryManifest | null>(null)
  const [activeTab, setActiveTab] = useState<
    'overview' | 'manifest' | 'files' | 'xray' | 'rules' | 'impact' | 'modernization' | 'plan' | 'transform' | 'validation'
  >('overview')
  const [loading, setLoading] = useState(true)

  const loadWorkspaceData = useCallback(async () => {
    if (!projectId) return
    try {
      const proj = await api.projects.get(projectId)
      setProject(proj)

      // Try fetching existing repository for project
      try {
        const repo = await api.repositories.get(projectId)
        setRepository(repo)

        if (repo.status === 'COMPLETED') {
          const man = await api.repositories.manifest(repo.id)
          setManifest(man)
        }
      } catch {
        setRepository(null)
        setManifest(null)
      }
    } catch {
      // Navigate back if project not found
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => {
    loadWorkspaceData()
  }, [loadWorkspaceData])

  const handleReingest = async () => {
    if (!repository) return
    try {
      const repo = await api.repositories.ingest(repository.id)
      setRepository(repo)
      await loadWorkspaceData()
    } catch {
      // Handled
    }
  }

  if (loading) {
    return <div className="p-12 text-center text-xs text-slate-400">Loading project workspace...</div>
  }

  if (!project) {
    return (
      <div className="p-12 text-center text-xs text-slate-500">
        Project not found.{' '}
        <button onClick={() => navigate('/projects')} className="text-teal-600 font-bold underline">
          Return to Projects
        </button>
      </div>
    )
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: HardDrive },
    { id: 'manifest', label: 'Manifest', icon: Code2 },
    { id: 'files', label: 'File Explorer', icon: FileText },
    { id: 'xray', label: 'System X-Ray', icon: Cpu, badge: 'P3' },
    { id: 'rules', label: 'Business Logic', icon: BookMarked, badge: 'P4' },
    { id: 'impact', label: 'Impact Analysis', icon: GitBranch, badge: 'P5' },
    { id: 'modernization', label: 'Strategy', icon: Map, badge: 'P6' },
    { id: 'plan', label: 'Execution Plan', icon: GitFork, badge: 'P7' },
    { id: 'transform', label: 'Transformation', icon: Code2, badge: 'P8' },
    { id: 'validation', label: 'Validation', icon: FlaskConical, badge: 'P9' },
  ]

  return (
    <div className="space-y-6">
      {/* Workspace Header */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/projects')}
              className="p-2 rounded-lg border border-slate-200 text-slate-500 hover:text-slate-900 hover:bg-slate-50 transition-colors cursor-pointer"
              title="Back to Projects"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <div>
              <div className="flex items-center gap-2.5">
                <Folder className="w-5 h-5 text-teal-600" />
                <h1 className="text-xl font-extrabold text-slate-900">{project.name}</h1>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-100 text-emerald-800 border border-emerald-300">
                  {project.status}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                {project.description || 'Legacy application repository workspace'}
              </p>
            </div>
          </div>

          <button
            onClick={loadWorkspaceData}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer self-start sm:self-auto"
          >
            <RefreshCw className="w-3.5 h-3.5 text-slate-500" /> Refresh State
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      {!repository ? (
        <RepositoryUploadCard projectId={project.id} onUploadSuccess={loadWorkspaceData} />
      ) : (
        <div className="space-y-6">
          {/* Progress Card */}
          <IngestionProgressCard repository={repository} onReingest={handleReingest} />

          {/* Segmented Pipeline Workspace Navigation Tabs */}
          <div className="bg-white border border-slate-200 rounded-xl p-1.5 shadow-2xs flex items-center gap-1 overflow-x-auto scrollbar-none">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as typeof activeTab)}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-all cursor-pointer ${
                    isActive
                      ? 'bg-slate-900 text-white shadow-xs font-bold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-teal-400' : 'text-slate-400'}`} />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>

          {/* Active Tab Component Container */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xs">
            {activeTab === 'overview' && (
              <RepositoryOverviewTab repository={repository} manifest={manifest} />
            )}
            {activeTab === 'manifest' && <RepositoryManifestTab manifest={manifest} />}
            {activeTab === 'files' && <FileExplorerTab repositoryId={repository.id} />}
            {activeTab === 'xray' && <SystemXRayPage repositoryId={repository.id} />}
            {activeTab === 'rules' && <BusinessRulesPage repositoryId={repository.id} />}
            {activeTab === 'impact' && <ImpactPage repositoryId={repository.id} />}
            {activeTab === 'modernization' && <ModernizationPage repositoryId={repository.id} />}
            {activeTab === 'plan' && <ModernizationPlanPage repositoryId={repository.id} />}
            {activeTab === 'transform' && <TransformationStudioPage analysisId={repository.id} />}
            {activeTab === 'validation' && (
              <ValidationWorkspacePage
                proposal={{
                  id: repository.id,
                  plan_id: 'default-plan',
                  task_id: 'default-task',
                  analysis_id: repository.id,
                  repository_id: repository.id,
                  status: 'APPLIED',
                  transformation_type: 'FACADE_EXTRACTION',
                  target_entity: 'TransferDomainService',
                  summary: 'Isolated empirical build, unit test & behavioral equivalence pipeline',
                  specification: {},
                  rule_ids: ['BR-001', 'BR-002', 'BR-003', 'BR-004'],
                  impacted_entity_ids: [],
                  artifacts: [],
                  ai_proposal_status: 'COMPLETED',
                  created_at: new Date().toISOString(),
                  updated_at: new Date().toISOString(),
                }}
              />
            )}
          </div>
        </div>
      )}
    </div>
  )
}
