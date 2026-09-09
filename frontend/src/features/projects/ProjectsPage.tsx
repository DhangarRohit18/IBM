import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FolderPlus, Layers, Search, Server, ArrowRight, Folder } from 'lucide-react'
import { api, type Project } from '@/services/api'
import { CreateProjectModal } from './CreateProjectModal'

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
      // Ignore errors for initial state
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProjects()
  }, [])

  const filteredProjects = projects.filter(
    (p) =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      (p.description && p.description.toLowerCase().includes(search.toLowerCase()))
  )

  const getStatusBadge = (status: Project['status']) => {
    switch (status) {
      case 'READY':
      case 'ANALYZED':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">ANALYZED</span>
      case 'INGESTING':
      case 'ANALYZING':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300 animate-pulse">IN PROGRESS</span>
      case 'FAILED':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-300">FAILED</span>
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-300">{status}</span>
    }
  }

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-xl border border-slate-200 bg-white shadow-2xs">
        <div>
          <div className="flex items-center gap-2 text-teal-600 font-extrabold text-xs tracking-wider uppercase mb-1">
            <Layers className="w-4 h-4" /> Enterprise Project Repository Management
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900">Projects & Repositories</h1>
          <p className="text-xs text-slate-500 mt-1">
            Create or select a legacy application project to manage repository ingestion, system analysis, and modernization pipelines.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-xs transition-all cursor-pointer shrink-0"
        >
          <FolderPlus className="w-4 h-4" /> New Project
        </button>
      </div>

      {/* Search Bar */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search projects by name or description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-900 text-xs focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 shadow-2xs"
          />
        </div>
      </div>

      {/* Projects Grid */}
      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs">Loading projects...</div>
      ) : filteredProjects.length === 0 ? (
        <div className="p-12 rounded-xl border border-dashed border-slate-300 text-center bg-white shadow-2xs">
          <Server className="w-10 h-10 text-slate-300 mx-auto mb-3" />
          <h3 className="text-sm font-bold text-slate-900">No projects found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-4">
            {search ? 'No projects matched your search query.' : 'Create your first legacy application project to start repository ingestion.'}
          </p>
          {!search && (
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-4 py-2 rounded-lg bg-emerald-600 text-white font-bold text-xs hover:bg-emerald-700"
            >
              Create Project
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredProjects.map((project) => (
            <div
              key={project.id}
              onClick={() => navigate(`/projects/${project.id}`)}
              className="group p-5 rounded-xl border border-slate-200 bg-white hover:border-teal-500 hover:shadow-md transition-all cursor-pointer flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <Folder className="w-4 h-4 text-teal-600 shrink-0" />
                    <h3 className="font-bold text-sm text-slate-900 group-hover:text-teal-700 transition-colors line-clamp-1">
                      {project.name}
                    </h3>
                  </div>
                  {getStatusBadge(project.status)}
                </div>
                <p className="text-xs text-slate-500 line-clamp-2 mb-4 leading-relaxed">
                  {project.description || 'No description provided.'}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                <span>Created {new Date(project.created_at).toLocaleDateString()}</span>
                <span className="flex items-center gap-1 font-bold text-teal-700 opacity-80 group-hover:opacity-100 transition-opacity">
                  Open Workspace <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
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
