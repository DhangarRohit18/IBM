/**
 * LEGACYX — Navigation Sidebar.
 *
 * Clean slate-navy dark theme with high contrast, precise badges,
 * active workspace card indicator, and searchParams tab synchronization.
 *
 * Layer: Presentation (AGENTS.md §1.3)
 */

import { NavLink, useLocation, useSearchParams } from 'react-router-dom'
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
  Layers,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react'

interface NavItem {
  label: string
  path: string
  tabKey?: string
  badge?: string
  icon: React.ComponentType<{ className?: string }>
}

export function Sidebar() {
  const location = useLocation()
  const [searchParams] = useSearchParams()

  const match = location.pathname.match(/\/projects\/([^/?#]+)/)
  const currentProjectId = match ? match[1] : null
  const currentTab = searchParams.get('tab') || 'overview'

  const workspaceItems: NavItem[] = [
    { label: 'Dashboard', path: '/', icon: LayoutDashboard },
  ]

  const projectManagementItems: NavItem[] = [
    { label: 'Projects & Repositories', path: '/projects', icon: FolderOpen },
  ]

  const pipelineItems: NavItem[] = [
    {
      label: 'System X-Ray',
      path: currentProjectId ? `/projects/${currentProjectId}?tab=xray` : '/projects',
      tabKey: 'xray',
      badge: 'P3',
      icon: Cpu,
    },
    {
      label: 'Business Logic',
      path: currentProjectId ? `/projects/${currentProjectId}?tab=rules` : '/projects',
      tabKey: 'rules',
      badge: 'P4',
      icon: BookMarked,
    },
    {
      label: 'Impact Analysis',
      path: currentProjectId ? `/projects/${currentProjectId}?tab=impact` : '/projects',
      tabKey: 'impact',
      badge: 'P5',
      icon: GitBranch,
    },
    {
      label: 'Strategy Engine',
      path: currentProjectId ? `/projects/${currentProjectId}?tab=modernization` : '/projects',
      tabKey: 'modernization',
      badge: 'P6',
      icon: Map,
    },
    {
      label: 'Execution Plan',
      path: currentProjectId ? `/projects/${currentProjectId}?tab=plan` : '/projects',
      tabKey: 'plan',
      badge: 'P7',
      icon: GitFork,
    },
    {
      label: 'Code Transform',
      path: currentProjectId ? `/projects/${currentProjectId}?tab=transform` : '/projects',
      tabKey: 'transform',
      badge: 'P8',
      icon: Code2,
    },
    {
      label: 'Validation',
      path: currentProjectId ? `/projects/${currentProjectId}?tab=validation` : '/projects',
      tabKey: 'validation',
      badge: 'P9',
      icon: FlaskConical,
    },
  ]

  const systemItems: NavItem[] = [
    { label: 'Settings & Health', path: '/settings', icon: Settings },
    { label: 'Documentation', path: '/documentation', icon: BookOpen },
  ]

  const isItemActive = (item: NavItem) => {
    if (item.path === '/') return location.pathname === '/'
    if (item.path === '/projects') {
      return location.pathname === '/projects' && !currentProjectId
    }
    if (item.tabKey && currentProjectId) {
      return location.pathname.startsWith(`/projects/${currentProjectId}`) && currentTab === item.tabKey
    }
    return location.pathname === item.path
  }

  return (
    <aside className="w-[250px] bg-[#070d19] text-slate-300 flex flex-col h-screen sticky top-0 z-40 select-none shadow-xl border-r border-slate-800/80">
      {/* Brand Header */}
      <div className="h-[56px] px-4 flex items-center justify-between border-b border-slate-800/80 bg-[#040812] shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-md bg-teal-600 flex items-center justify-center text-white font-black text-xs shadow-sm ring-1 ring-teal-400/30 shrink-0">
            LX
          </div>
          <div className="flex items-center gap-1.5">
            <span className="font-extrabold text-white text-sm tracking-tight">
              LEGACY<span className="text-teal-400">X</span>
            </span>
            <span className="text-[9px] font-mono font-semibold px-1.5 py-0.5 rounded bg-slate-800/80 text-teal-300 border border-slate-700/60">
              v1.0
            </span>
          </div>
        </div>
      </div>

      {/* Navigation Scrollable Body */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-5 scrollbar-thin min-h-0">
        {/* Workspace Overview */}
        <div>
          <div className="px-2 mb-2 text-[10px] font-extrabold tracking-wider text-slate-400 uppercase">
            Main Workspace
          </div>
          <div className="space-y-0.5">
            {workspaceItems.map((item) => {
              const Icon = item.icon
              const active = isItemActive(item)
              return (
                <NavLink
                  key={item.label}
                  to={item.path}
                  className={`flex items-center justify-between px-2.5 py-2 rounded-lg text-xs transition-all ${
                    active
                      ? 'bg-teal-500/15 text-teal-300 font-bold border-l-2 border-teal-400 pl-2'
                      : 'text-slate-400 font-medium hover:text-slate-100 hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <Icon className={`w-4 h-4 shrink-0 ${active ? 'text-teal-400' : 'text-slate-500'}`} />
                    <span className="truncate">{item.label}</span>
                  </div>
                </NavLink>
              )
            })}
          </div>
        </div>

        {/* Project Management */}
        <div>
          <div className="px-2 mb-2 text-[10px] font-extrabold tracking-wider text-slate-400 uppercase">
            Projects & Repos
          </div>
          <div className="space-y-0.5">
            {projectManagementItems.map((item) => {
              const Icon = item.icon
              const active = isItemActive(item)
              return (
                <NavLink
                  key={item.label}
                  to={item.path}
                  className={`flex items-center justify-between px-2.5 py-2 rounded-lg text-xs transition-all ${
                    active
                      ? 'bg-teal-500/15 text-teal-300 font-bold border-l-2 border-teal-400 pl-2'
                      : 'text-slate-400 font-medium hover:text-slate-100 hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <Icon className={`w-4 h-4 shrink-0 ${active ? 'text-teal-400' : 'text-slate-500'}`} />
                    <span className="truncate">{item.label}</span>
                  </div>
                </NavLink>
              )
            })}
          </div>
        </div>

        {/* Active Workspace Banner Card (if inside a project) */}
        {currentProjectId && (
          <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 shadow-xs space-y-1.5">
            <div className="flex items-center justify-between text-[10px] font-extrabold text-teal-400 uppercase tracking-wider">
              <span className="flex items-center gap-1">
                <Layers className="w-3 h-3" /> Active Workspace
              </span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            </div>
            <div className="text-[11px] font-bold text-slate-200 truncate font-mono">
              {currentProjectId}
            </div>
            <NavLink
              to={`/projects/${currentProjectId}?tab=overview`}
              className="inline-flex items-center gap-1 text-[10px] font-bold text-teal-400 hover:text-teal-300 transition-colors"
            >
              Overview Tab <ChevronRight className="w-3 h-3" />
            </NavLink>
          </div>
        )}

        {/* Modernization Pipeline Section */}
        <div>
          <div className="px-2 mb-2 text-[10px] font-extrabold tracking-wider text-slate-400 uppercase flex items-center justify-between">
            <span>Modernization Pipeline</span>
            <span className="text-[9px] font-mono text-slate-400 font-normal">P3-P9</span>
          </div>
          <div className="space-y-0.5">
            {pipelineItems.map((item) => {
              const Icon = item.icon
              const active = isItemActive(item)
              return (
                <NavLink
                  key={item.label}
                  to={item.path}
                  className={`flex items-center justify-between px-2.5 py-2 rounded-lg text-xs transition-all ${
                    active
                      ? 'bg-teal-500/15 text-teal-300 font-bold border-l-2 border-teal-400 pl-2'
                      : 'text-slate-400 font-medium hover:text-slate-100 hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <Icon className={`w-4 h-4 shrink-0 ${active ? 'text-teal-400' : 'text-slate-500'}`} />
                    <span className="truncate">{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`px-1.5 py-0.2 rounded text-[9px] font-mono font-extrabold shrink-0 ${
                        active
                          ? 'bg-teal-900/60 text-teal-300 border border-teal-500/40'
                          : 'bg-slate-800 text-slate-400 border border-slate-700/50'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              )
            })}
          </div>
        </div>

        <div className="my-2 border-t border-slate-800/80" />

        {/* System Settings & Reference */}
        <div>
          <div className="px-2 mb-2 text-[10px] font-extrabold tracking-wider text-slate-400 uppercase">
            System & Reference
          </div>
          <div className="space-y-0.5">
            {systemItems.map((item) => {
              const Icon = item.icon
              const active = isItemActive(item)
              return (
                <NavLink
                  key={item.label}
                  to={item.path}
                  className={`flex items-center justify-between px-2.5 py-2 rounded-lg text-xs transition-all ${
                    active
                      ? 'bg-teal-500/15 text-teal-300 font-bold border-l-2 border-teal-400 pl-2'
                      : 'text-slate-400 font-medium hover:text-slate-100 hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <Icon className={`w-4 h-4 shrink-0 ${active ? 'text-teal-400' : 'text-slate-500'}`} />
                    <span className="truncate">{item.label}</span>
                  </div>
                </NavLink>
              )
            })}
          </div>
        </div>
      </div>

      {/* Sidebar Footer Accent */}
      <div className="p-3 border-t border-slate-800/80 bg-[#040812] shrink-0 space-y-1">
        <div className="flex items-center justify-between text-[11px] text-slate-300 font-medium">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            Backend Nominal
          </span>
          <span className="text-[10px] font-mono text-slate-400">8ms</span>
        </div>
        <div className="flex items-center gap-1.5 text-[10px] text-slate-400 pt-0.5">
          <ShieldCheck className="w-3 h-3 text-teal-400 shrink-0" />
          <span>IBM watsonx.ai Enabled</span>
        </div>
      </div>
    </aside>
  )
}
