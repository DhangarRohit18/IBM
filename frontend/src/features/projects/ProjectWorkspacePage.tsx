import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
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

type WorkspaceTab =
  | 'overview'
  | 'manifest'
  | 'files'
  | 'xray'
  | 'rules'
  | 'impact'
  | 'modernization'
  | 'plan'
  | 'transform'
  | 'validation'

export function ProjectWorkspacePage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const [project, setProject] = useState<Project | null>(null)
  const [repository, setRepository] = useState<Repository | null>(null)
  const [manifest, setManifest] = useState<RepositoryManifest | null>(null)
  const [loading, setLoading] = useState(true)

  const activeTab: WorkspaceTab = (searchParams.get('tab') as WorkspaceTab) || 'overview'

  const handleTabChange = (tab: WorkspaceTab) => {
    setSearchParams({ tab })
  }

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

  const tabs: Array<{ id: WorkspaceTab; label: string; icon: React.ComponentType<{ className?: string }>; badge?: string }> = [
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
    <div className="space-y-5">
      {/* Workspace Header — consistent with PageHeader pattern */}
      <div className="bg-white border border-slate-200/90 rounded-2xl px-6 py-5 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/projects')}
            className="p-2 rounded-xl border border-slate-200 text-slate-500 hover:text-slate-900 hover:bg-slate-50 transition-colors cursor-pointer shrink-0"
            title="Back to Projects"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <span className="text-[10px] font-extrabold tracking-widest text-teal-700 uppercase">
                Project Workspace
              </span>
            </div>
            <div className="flex items-center gap-2.5">
              <Folder className="w-4.5 h-4.5 text-teal-600 shrink-0" />
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">{project.name}</h1>
              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold border uppercase ${
                project.status === 'ANALYZED' || project.status === 'READY'
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                  : project.status === 'FAILED'
                    ? 'bg-rose-50 text-rose-700 border-rose-300'
                    : 'bg-blue-50 text-blue-700 border-blue-300'
              }`}>
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
          className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 bg-white text-xs font-bold text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer shadow-2xs shrink-0"
        >
          <RefreshCw className="w-3.5 h-3.5 text-slate-500" /> Refresh State
        </button>
      </div>

      {/* Main Content Area */}
      {!repository ? (
        <RepositoryUploadCard projectId={project.id} onUploadSuccess={loadWorkspaceData} />
      ) : (
        <div className="space-y-6">
          {/* Progress Card */}
          <IngestionProgressCard repository={repository} onReingest={handleReingest} />

          {/* Segmented Pipeline Workspace Navigation Tabs */}
          <div className="bg-slate-100/90 border border-slate-200/80 rounded-2xl p-1.5 shadow-2xs flex items-center gap-1 overflow-x-auto scrollbar-none">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => handleTabChange(tab.id)}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs whitespace-nowrap transition-all cursor-pointer ${
                    isActive
                      ? 'bg-white text-slate-900 shadow-2xs font-extrabold ring-1 ring-slate-200'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-white/50 font-semibold'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-teal-600' : 'text-slate-400'}`} />
                  <span>{tab.label}</span>
                  {tab.badge && (
                    <span className={`px-1.5 py-0.2 text-[9px] font-mono rounded font-extrabold ${isActive ? 'bg-teal-50 text-teal-700 border border-teal-200' : 'bg-slate-200/80 text-slate-600'}`}>
                      {tab.badge}
                    </span>
                  )}
                </button>
              )
            })}
          </div>

          {/* Active Tab Component Container */}
          <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-2xs">
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
