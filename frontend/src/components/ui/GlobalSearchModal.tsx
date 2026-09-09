import { useState, useEffect } from 'react'
import { Search, X, Folder } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { api, type Project } from '@/services/api'

interface GlobalSearchModalProps {
  onClose: () => void
}

export function GlobalSearchModal({ onClose }: GlobalSearchModalProps) {
  const [query, setQuery] = useState('')
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  useEffect(() => {
    async function loadProjects() {
      try {
        const list = await api.projects.list()
        setProjects(list)
      } catch {
        setProjects([])
      } finally {
        setLoading(false)
      }
    }
    loadProjects()
  }, [])

  const filteredProjects = projects.filter(
    (p) =>
      p.name.toLowerCase().includes(query.toLowerCase()) ||
      (p.description && p.description.toLowerCase().includes(query.toLowerCase()))
  )

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-start justify-center pt-20 p-4">
      <div className="bg-white rounded-xl shadow-2xl border border-slate-200 w-full max-w-xl overflow-hidden">
        {/* Search Header */}
        <div className="p-3 border-b border-slate-150 flex items-center gap-3">
          <Search className="w-4 h-4 text-slate-400 ml-1" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search projects..."
            className="w-full bg-transparent border-none text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none"
            autoFocus
          />
          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search Results */}
        <div className="p-2 max-h-80 overflow-y-auto">
          {loading ? (
            <div className="p-8 text-center text-xs text-slate-400">Loading projects...</div>
          ) : filteredProjects.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-400">
              {query ? `No projects matching "${query}"` : 'No projects found in database.'}
            </div>
          ) : (
            <div className="space-y-1">
              <div className="px-3 py-1.5 text-[10px] font-semibold tracking-wider text-slate-400 uppercase">
                Projects ({filteredProjects.length})
              </div>
              {filteredProjects.map((project) => (
                <button
                  key={project.id}
                  onClick={() => {
                    navigate(`/projects/${project.id}`)
                    onClose()
                  }}
                  className="w-full flex items-center justify-between p-2.5 rounded-lg text-left text-xs text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <Folder className="w-4 h-4 text-teal-600 shrink-0" />
                    <div>
                      <div className="font-bold text-slate-900 leading-tight">{project.name}</div>
                      {project.description && (
                        <div className="text-[11px] text-slate-500 line-clamp-1">{project.description}</div>
                      )}
                    </div>
                  </div>
                  <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 border border-emerald-200 uppercase px-2 py-0.5 rounded font-bold">
                    {project.status}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2 bg-slate-50 border-t border-slate-150 flex items-center justify-between text-[11px] text-slate-400">
          <span>Click a project to open workspace</span>
          <span>ESC to exit</span>
        </div>
      </div>
    </div>
  )
}
