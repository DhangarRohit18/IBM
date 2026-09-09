import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  FolderOpen,
  Settings,
  BookOpen,
  Cpu,
  BookMarked,
  GitBranch,
  Map,
  GitFork,
  Code2,
  FlaskConical,
} from 'lucide-react'

interface NavItem {
  label: string
  path: string
  tabKey?: string
  icon: React.ComponentType<{ className?: string }>
}

export function Sidebar() {
  const location = useLocation()

  // Extract projectId if currently inside a project workspace
  const match = location.pathname.match(/\/projects\/([^/]+)/)
  const currentProjectId = match ? match[1] : null

  const workspaceItems: NavItem[] = [
    { label: 'Dashboard', path: '/', icon: LayoutDashboard },
  ]

  const projectManagementItems: NavItem[] = [
    { label: 'Projects & Repositories', path: '/projects', icon: FolderOpen },
  ]

  const pipelineItems: NavItem[] = [
    { label: 'System X-Ray', path: currentProjectId ? `/projects/${currentProjectId}` : '/projects', tabKey: 'xray', icon: Cpu },
    { label: 'Business Logic', path: currentProjectId ? `/projects/${currentProjectId}` : '/projects', tabKey: 'rules', icon: BookMarked },
    { label: 'Impact Analysis', path: currentProjectId ? `/projects/${currentProjectId}` : '/projects', tabKey: 'impact', icon: GitBranch },
    { label: 'Modernization Strategy', path: currentProjectId ? `/projects/${currentProjectId}` : '/projects', tabKey: 'modernization', icon: Map },
    { label: 'Execution Plan', path: currentProjectId ? `/projects/${currentProjectId}` : '/projects', tabKey: 'plan', icon: GitFork },
    { label: 'Code Transformation', path: currentProjectId ? `/projects/${currentProjectId}` : '/projects', tabKey: 'transform', icon: Code2 },
    { label: 'Validation', path: currentProjectId ? `/projects/${currentProjectId}` : '/projects', tabKey: 'validation', icon: FlaskConical },
  ]

  const systemItems: NavItem[] = [
    { label: 'Settings', path: '/settings', icon: Settings },
    { label: 'Documentation', path: '/documentation', icon: BookOpen },
  ]

  const isItemActive = (item: NavItem) => {
    if (item.path === '/') return location.pathname === '/'
    if (item.path === '/projects') return location.pathname === '/projects'
    if (currentProjectId && item.tabKey) {
      // Checked via state or URL search params if needed
      return location.pathname.startsWith(`/projects/${currentProjectId}`)
    }
    return location.pathname.startsWith(item.path)
  }

  return (
    <aside className="w-[250px] bg-[#0b192c] text-slate-300 flex flex-col h-screen fixed left-0 top-0 z-40 select-none shadow-xl border-r border-slate-800/60">
      {/* Sidebar Header Brand Mark */}
      <div className="h-[60px] px-5 flex items-center gap-3 border-b border-slate-800/60 bg-[#081220]">
        <div className="w-8 h-8 rounded-lg bg-teal-600 flex items-center justify-center text-white font-bold text-base shadow-md">
          LX
        </div>
        <span className="font-extrabold text-white text-base tracking-tight">
          LEGACY<span className="text-teal-400">X</span>
        </span>
      </div>

      {/* Navigation Scrollable Body */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6 scrollbar-thin">
        {/* Workspace Section */}
        <div>
          <div className="px-3 mb-2 text-[10px] font-bold tracking-wider text-slate-400 uppercase">
            Workspace
          </div>
          <div className="space-y-1">
            {workspaceItems.map((item) => {
              const Icon = item.icon
              const active = isItemActive(item)
              return (
                <NavLink
                  key={item.label}
                  to={item.path}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                    active
                      ? 'bg-teal-600 text-white shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/80'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? 'text-white' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </NavLink>
              )
            })}
          </div>
        </div>

        {/* Project Management Section */}
        <div>
          <div className="px-3 mb-2 text-[10px] font-bold tracking-wider text-slate-400 uppercase">
            Project Management
          </div>
          <div className="space-y-1">
            {projectManagementItems.map((item) => {
              const Icon = item.icon
              const active = isItemActive(item)
              return (
                <NavLink
                  key={item.label}
                  to={item.path}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                    active
                      ? 'bg-teal-600 text-white shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/80'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? 'text-white' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </NavLink>
              )
            })}
          </div>
        </div>

        {/* Modernization Pipeline Section */}
        <div>
          <div className="px-3 mb-2 text-[10px] font-bold tracking-wider text-slate-400 uppercase">
            Modernization Pipeline
          </div>
          <div className="space-y-1">
            {pipelineItems.map((item) => {
              const Icon = item.icon
              const active = isItemActive(item)
              return (
                <NavLink
                  key={item.label}
                  to={item.path}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    active
                      ? 'bg-teal-600 text-white shadow-sm font-semibold'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/80'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? 'text-white' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </NavLink>
              )
            })}
          </div>
        </div>

        <div className="my-2 border-t border-slate-800/60" />

        {/* System Settings & Docs */}
        <div className="space-y-1">
          {systemItems.map((item) => {
            const Icon = item.icon
            const active = isItemActive(item)
            return (
              <NavLink
                key={item.label}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  active
                    ? 'bg-teal-600 text-white shadow-sm'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/80'
                }`}
              >
                <Icon className={`w-4 h-4 ${active ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </NavLink>
            )
          })}
        </div>
      </div>

      {/* Sidebar Footer Accent */}
      <div className="p-4 border-t border-slate-800/80 bg-gradient-to-b from-[#081220] to-[#050c18] relative overflow-hidden">
        <div className="relative z-10 space-y-1">
          <p className="text-xs font-semibold text-slate-200 leading-tight">
            Legacy systems.
          </p>
          <p className="text-xs font-semibold text-slate-400 leading-tight">
            New opportunities.
          </p>
          <p className="text-[10px] font-mono text-slate-500 pt-1">
            LEGACYX v1.0.0
          </p>
        </div>
      </div>
    </aside>
  )
}
