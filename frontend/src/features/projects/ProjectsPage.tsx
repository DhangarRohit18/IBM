/**
 * LEGACYX — Projects & Repositories Page.
 *
 * Displays a rich card grid of all projects.
 * Card design mirrors the dashboard project cards exactly:
 *  - Dark thumbnail header with visual art + status badge
 *  - Name, description, progress bar
 *  - CTA button
 *
 * Layer: Presentation (AGENTS.md §1.3)
 */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FolderPlus,
  Layers,
  Search,
  Server,
  ArrowRight,
  MoreHorizontal,
  Clock,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react'
import { api, type Project } from '@/services/api'
import { CreateProjectModal } from './CreateProjectModal'
import { PageHeader } from '@/components/ui/PageHeader'

// ── Status helpers ─────────────────────────────────────────────────────────────

function statusBadgeClass(status: Project['status']) {
  if (status === 'ANALYZED' || status === 'READY')
    return 'bg-emerald-100 text-emerald-800 border-emerald-300'
  if (status === 'INGESTING' || status === 'ANALYZING')
    return 'bg-amber-100 text-amber-800 border-amber-300'
  if (status === 'FAILED')
    return 'bg-rose-100 text-rose-800 border-rose-300'
  return 'bg-blue-100 text-blue-800 border-blue-300'
}

function statusIcon(status: Project['status']) {
  if (status === 'ANALYZED' || status === 'READY')
    return <CheckCircle2 className="w-3 h-3" />
  if (status === 'INGESTING' || status === 'ANALYZING')
    return <Clock className="w-3 h-3 animate-spin" />
  if (status === 'FAILED')
    return <AlertCircle className="w-3 h-3" />
  return null
}

function progressPercent(status: Project['status']) {
  switch (status) {
    case 'CREATED': return 5
    case 'INGESTING': return 15
    case 'ANALYZING': return 45
    case 'ANALYZED':
    case 'READY': return 75
    case 'FAILED': return 20
    default: return 5
  }
}

function progressColor(status: Project['status']) {
  if (status === 'ANALYZED' || status === 'READY') return 'bg-emerald-500'
  if (status === 'FAILED') return 'bg-rose-500'
  if (status === 'INGESTING' || status === 'ANALYZING') return 'bg-amber-500'
  return 'bg-blue-500'
}

// ── Project Card ───────────────────────────────────────────────────────────────

interface ProjectCardProps {
  project: Project
  onClick: () => void
}

function ProjectCard({ project, onClick }: ProjectCardProps) {
  const isAnalyzed = project.status === 'ANALYZED' || project.status === 'READY'
  const pct = progressPercent(project.status)

  // Visual art background gradient per-project (deterministic from name length)
  const gradients = [
    'from-blue-900 via-teal-900 to-slate-900',
    'from-indigo-900 via-purple-900 to-slate-900',
    'from-teal-900 via-cyan-900 to-slate-900',
    'from-slate-900 via-blue-900 to-teal-900',
  ]
  const gradient = gradients[project.name.length % gradients.length]

  return (
    <div
      onClick={onClick}
      className="group bg-white border border-slate-200 hover:border-teal-400 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all cursor-pointer flex flex-col"
    >
      {/* Dark thumbnail header */}
      <div className="relative h-28 bg-slate-900 overflow-hidden shrink-0">
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-900/60 to-transparent z-10" />
        {/* Status badge */}
        <div className="absolute top-2.5 left-3 z-20">
          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold border uppercase tracking-wide ${statusBadgeClass(project.status)}`}>
            {statusIcon(project.status)}
            {project.status}
          </span>
        </div>
        {/* More options */}
        <button
          className="absolute top-2.5 right-2.5 z-20 text-slate-400 hover:text-white p-1 rounded transition-colors"
          aria-label="More options"
          onClick={(e) => e.stopPropagation()}
        >
          <MoreHorizontal className="w-4 h-4" />
        </button>
        {/* Visual art */}
        <div className={`w-full h-full opacity-40 bg-gradient-to-tr ${gradient} flex items-center justify-center`}>
          <Layers className="w-10 h-10 text-white/40" />
        </div>
      </div>

      {/* Card body */}
      <div className="p-4 flex-1 flex flex-col gap-3 min-h-0">
        <div>
          <h3 className="font-bold text-sm text-slate-900 group-hover:text-teal-700 transition-colors truncate">
            {project.name}
          </h3>
          <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed mt-1">
            {project.description || 'Legacy application repository modernization workspace'}
          </p>
        </div>

        {/* Progress bar */}
        <div className="space-y-1 mt-auto">
          <div className="h-1 w-full bg-slate-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${progressColor(project.status)}`}
              style={{ width: `${pct}%` }}
            />
          </div>
          <div className="flex justify-between text-[10px] text-slate-400 font-medium">
            <span>{isAnalyzed ? '6/8 phases done' : project.status === 'CREATED' ? 'Awaiting ingestion' : 'Processing...'}</span>
            <span>Created {new Date(project.created_at).toLocaleDateString()}</span>
          </div>
        </div>

        {/* CTA */}
        <button
          className={`w-full py-1.5 px-3 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-colors cursor-pointer border ${
            isAnalyzed
              ? 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border-emerald-200 group-hover:border-emerald-400'
              : 'bg-blue-50 text-blue-700 hover:bg-blue-100 border-blue-200 group-hover:border-blue-400'
          }`}
        >
          Open Workspace <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  )
}

// ── Projects Page ──────────────────────────────────────────────────────────────

export function ProjectsPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)

  const fetchProjects = async () => {
    try {
      const data = await api.projects.list()
      setProjects(data)
    } catch {
      // swallow — empty state handles it
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchProjects() }, [])

  const filteredProjects = projects.filter(
    (p) =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      (p.description && p.description.toLowerCase().includes(search.toLowerCase()))
  )

  return (
    <div className="space-y-5">
      {/* Page Header */}
      <PageHeader
        eyebrowIcon={<Layers className="w-3.5 h-3.5" />}
        eyebrow="Enterprise Project Repository Management"
        title="Projects & Repositories"
        subtitle="Create or select a legacy application project to manage repository ingestion, system analysis, and modernization pipelines."
        actions={
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition-colors cursor-pointer"
          >
            <FolderPlus className="w-4 h-4" /> New Project
          </button>
        }
      />

      {/* Search Bar */}
      <div className="relative">
        <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        <input
          type="text"
          placeholder="Search projects by name or description..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-900 text-xs focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 shadow-sm"
        />
      </div>

      {/* Project Grid / States */}
      {loading ? (
        <div className="py-16 text-center text-xs text-slate-400 border border-slate-200 rounded-xl bg-white">
          Loading projects...
        </div>
      ) : filteredProjects.length === 0 ? (
        <div className="py-16 text-center border border-dashed border-slate-300 rounded-xl bg-white space-y-3">
          <Server className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-sm font-bold text-slate-800">
            {search ? 'No projects matched' : 'No projects yet'}
          </h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            {search
              ? 'Try a different search term.'
              : 'Create your first legacy application project to start repository ingestion.'}
          </p>
          {!search && (
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-4 py-2 rounded-lg bg-emerald-600 text-white font-bold text-xs hover:bg-emerald-700 transition-colors cursor-pointer"
            >
              Create Project
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredProjects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onClick={() => navigate(`/projects/${project.id}`)}
            />
          ))}
        </div>
      )}

      <CreateProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onProjectCreated={(id) => navigate(`/projects/${id}`)}
      />
    </div>
  )
}
