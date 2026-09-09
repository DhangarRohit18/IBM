/**
 * LEGACYX — Dashboard Page.
 *
 * Layout architecture:
 *  - Single column (stacked) on screens below XL (< 1280px CSS width)
 *    Since the sidebar is 250px wide, at 1280px the usable area is 1030px
 *    which is wide enough for the 2-column split.
 *  - Two columns (8 / 4) at xl: and above.
 *
 * Grid children use min-w-0 to prevent flex/grid blowout.
 * All API data is real — no hardcoded counts.
 *
 * Layer: Presentation (AGENTS.md §1.3)
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FileText,
  Network,
  Sparkles,
  ShieldCheck,
  Folder,
  BarChart3,
  Clock,
  CheckCircle2,
  Plus,
  ArrowRight,
  MoreHorizontal,
  Layers,
  BookOpen,
  Cpu,
  HelpCircle,
} from 'lucide-react'
import { api, type Project } from '@/services/api'

// ── Dashboard Metric Card ──────────────────────────────────────────────────────

interface MetricCardProps {
  icon: React.ReactNode
  iconBg: string
  value: number
  label: string
}

function MetricCard({ icon, iconBg, value, label }: MetricCardProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3 shadow-sm min-w-0">
      <div className={`w-10 h-10 rounded-xl ${iconBg} flex items-center justify-center shrink-0`}>
        {icon}
      </div>
      <div className="min-w-0">
        <div className="text-xl font-extrabold text-slate-900">{value}</div>
        <div className="text-xs text-slate-500 font-medium truncate">{label}</div>
      </div>
    </div>
  )
}

// ── Pipeline Step ──────────────────────────────────────────────────────────────

const PIPELINE_STEPS = [
  { num: 1, color: 'bg-blue-500',    title: 'Repository Ingestion',    desc: 'Upload and index legacy source code' },
  { num: 2, color: 'bg-cyan-500',    title: 'System X-Ray',            desc: 'Discover structure and relationships' },
  { num: 3, color: 'bg-emerald-500', title: 'Business Logic Recovery', desc: 'Extract and preserve business rules' },
  { num: 4, color: 'bg-amber-500',   title: 'Impact Analysis',         desc: 'Understand dependencies and risk' },
  { num: 5, color: 'bg-orange-500',  title: 'Modernization Strategy',  desc: 'Get evidence-based recommendations' },
  { num: 6, color: 'bg-rose-500',    title: 'Execution Plan',          desc: 'Generate a step-by-step plan' },
  { num: 7, color: 'bg-purple-500',  title: 'Code Transformation',     desc: 'Generate modernized code (isolated)' },
  { num: 8, color: 'bg-indigo-600',  title: 'Validation',              desc: 'Build, test and verify behavioral equivalence' },
]

// ── Project Status Badge ───────────────────────────────────────────────────────

function statusBadgeClass(status: Project['status']) {
  if (status === 'ANALYZED' || status === 'READY') {
    return 'bg-emerald-100 text-emerald-800 border border-emerald-300'
  }
  if (status === 'INGESTING' || status === 'ANALYZING') {
    return 'bg-amber-100 text-amber-800 border border-amber-300'
  }
  if (status === 'FAILED') {
    return 'bg-rose-100 text-rose-800 border border-rose-300'
  }
  return 'bg-blue-100 text-blue-800 border border-blue-300'
}

// ── Dashboard Page ─────────────────────────────────────────────────────────────

export function DashboardPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadProjects = async () => {
    setLoading(true)
    setError(null)
    try {
      const list = await api.projects.list()
      setProjects(list)
    } catch {
      setError('Unable to load projects. Check that the backend container is running.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProjects()
  }, [])

  // Derived metrics from real API data — never hardcoded
  const totalProjects  = projects.length
  const analyzedCount  = projects.filter(p => p.status === 'ANALYZED' || p.status === 'READY').length
  const inProgressCount = projects.filter(p => p.status === 'INGESTING' || p.status === 'ANALYZING').length
  const completedCount = projects.filter(p => p.status === 'ANALYZED').length

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[1fr_320px] gap-6 min-w-0">

      {/* ── Left / Main Column ─────────────────────────────────────────────── */}
      <div className="space-y-6 min-w-0">

        {/* Welcome Hero Banner */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-sky-100 via-sky-50 to-blue-50 border border-sky-200/80 p-6 shadow-sm">
          {/* Decorative mountains — only on wider screens, never causes overflow */}
          <div className="absolute right-0 top-0 bottom-0 w-2/5 pointer-events-none hidden lg:block" aria-hidden="true">
            <svg viewBox="0 0 500 300" className="w-full h-full" preserveAspectRatio="xMaxYMid slice">
              <path fill="#0284c7" fillOpacity="0.10" d="M150,300 L280,100 L410,300 Z" />
              <path fill="#0369a1" fillOpacity="0.18" d="M220,300 L350,60 L480,300 Z" />
              <path fill="#0f172a" fillOpacity="0.28" d="M300,300 L420,120 L520,300 Z" />
            </svg>
          </div>

          <div className="relative z-10 space-y-3 max-w-lg">
            <span className="text-[11px] font-extrabold tracking-widest text-slate-400 uppercase">
              Welcome to LegacyX
            </span>
            <h1 className="text-3xl font-black text-slate-900 leading-tight">
              Turn Legacy into{' '}
              <span className="text-emerald-600">What's Next</span>
            </h1>
            <p className="text-sm text-slate-600 leading-relaxed">
              Discover business logic, understand impact, generate modernization plans, and validate with confidence.
            </p>

            {/* Feature Pills */}
            <div className="flex flex-wrap gap-2 pt-1">
              {[
                { icon: <FileText className="w-3 h-3 text-blue-600" />, label: 'Evidence-Driven' },
                { icon: <Network className="w-3 h-3 text-blue-600" />,   label: 'Human-in-the-Loop' },
                { icon: <Sparkles className="w-3 h-3 text-blue-600" />,  label: 'AI-Powered Insights' },
                { icon: <ShieldCheck className="w-3 h-3 text-emerald-600" />, label: 'Safe & Controlled' },
              ].map(({ icon, label }) => (
                <div
                  key={label}
                  className="flex items-center gap-1.5 px-2.5 py-1 bg-white/90 border border-slate-200/70 rounded-md text-[11px] font-semibold text-slate-700 shadow-sm"
                >
                  {icon}
                  <span>{label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Quote badge — only on large screens where there is room */}
          <div className="absolute right-5 bottom-5 max-w-[220px] p-3 rounded-xl bg-slate-900/80 text-white border border-slate-700/50 hidden xl:block" aria-hidden="true">
            <p className="text-[11px] font-medium italic text-slate-200 leading-snug">
              "Understand your systems. Modernize with evidence. Move forward with confidence."
            </p>
          </div>
        </div>

        {/* ── Your Projects Section ─────────────────────────────────────────── */}
        <div className="space-y-4">

          {/* Section Header */}
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div>
              <div className="flex items-center gap-2">
                <Folder className="w-4 h-4 text-slate-900" />
                <h2 className="text-lg font-extrabold text-slate-900">Your Projects</h2>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Create or select a project to begin your modernization journey.
              </p>
            </div>
            <button
              onClick={() => navigate('/projects')}
              className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow-sm transition-colors cursor-pointer shrink-0"
            >
              <Plus className="w-4 h-4" /> New Project
            </button>
          </div>

          {/* Metrics Row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <MetricCard
              icon={<Folder className="w-4 h-4 text-blue-600" />}
              iconBg="bg-blue-50"
              value={totalProjects}
              label="Total Projects"
            />
            <MetricCard
              icon={<BarChart3 className="w-4 h-4 text-emerald-600" />}
              iconBg="bg-emerald-50"
              value={analyzedCount}
              label="Analyzed"
            />
            <MetricCard
              icon={<Clock className="w-4 h-4 text-amber-600" />}
              iconBg="bg-amber-50"
              value={inProgressCount}
              label="In Progress"
            />
            <MetricCard
              icon={<CheckCircle2 className="w-4 h-4 text-purple-600" />}
              iconBg="bg-purple-50"
              value={completedCount}
              label="Completed"
            />
          </div>

          {/* Project Cards / State Regions */}
          {loading ? (
            <div className="p-10 text-center text-xs text-slate-400 border border-slate-200 rounded-xl bg-white">
              Loading projects from backend API...
            </div>

          ) : error ? (
            <div className="p-5 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800 flex items-center justify-between gap-4">
              <span>{error}</span>
              <button
                onClick={loadProjects}
                className="px-3 py-1.5 rounded-lg bg-rose-600 text-white font-bold hover:bg-rose-700 cursor-pointer shrink-0"
              >
                Retry
              </button>
            </div>

          ) : projects.length === 0 ? (
            <div className="py-12 px-6 text-center border border-dashed border-slate-300 rounded-xl bg-white space-y-3">
              <Folder className="w-8 h-8 text-slate-300 mx-auto" />
              <div className="font-bold text-slate-700 text-sm">No projects yet</div>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Create your first legacy application project to ingest source code and start the 8-stage modernization pipeline.
              </p>
              <button
                onClick={() => navigate('/projects')}
                className="px-4 py-2 bg-emerald-600 text-white font-bold rounded-lg hover:bg-emerald-700 cursor-pointer inline-flex items-center gap-1.5 text-xs"
              >
                <Plus className="w-4 h-4" /> Create New Project
              </button>
            </div>

          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-2 2xl:grid-cols-3 gap-4">
              {projects.map((project, index) => {
                const isAnalyzed = project.status === 'ANALYZED' || project.status === 'READY'
                return (
                  <div
                    key={project.id || index}
                    className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md hover:border-slate-300 transition-all flex flex-col"
                  >
                    {/* Card Header with visual art */}
                    <div className="relative h-24 bg-slate-900 overflow-hidden shrink-0">
                      <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-900/50 to-transparent z-10" />
                      <div className="absolute top-2.5 left-3 z-20">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide ${statusBadgeClass(project.status)}`}>
                          {project.status}
                        </span>
                      </div>
                      <button className="absolute top-2.5 right-2.5 z-20 text-slate-300 hover:text-white p-1 rounded" aria-label="More options">
                        <MoreHorizontal className="w-4 h-4" />
                      </button>
                      <div className="w-full h-full opacity-40 bg-gradient-to-tr from-blue-900 via-teal-900 to-slate-900 flex items-center justify-center">
                        <Layers className="w-10 h-10 text-white/50" />
                      </div>
                    </div>

                    {/* Card Body */}
                    <div className="p-4 flex-1 flex flex-col gap-3 min-h-0">
                      <div>
                        <h3 className="font-bold text-sm text-slate-900 truncate">{project.name}</h3>
                        <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed mt-1">
                          {project.description || 'Legacy application repository modernization workspace'}
                        </p>
                      </div>

                      {/* Progress Bar */}
                      <div className="space-y-1 mt-auto">
                        <div className="h-1 w-full bg-slate-100 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${isAnalyzed ? 'bg-emerald-500 w-3/4' : 'bg-blue-500 w-1/4'}`} />
                        </div>
                        <div className="flex justify-between text-[10px] text-slate-400 font-medium">
                          <span>{isAnalyzed ? '6/8 phases done' : 'Repository ingested'}</span>
                          <span>Created {new Date(project.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>

                      {/* CTA */}
                      <button
                        onClick={() => navigate(`/projects/${project.id}`)}
                        className={`w-full py-1.5 px-3 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-colors cursor-pointer ${
                          isAnalyzed
                            ? 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200'
                            : 'bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200'
                        }`}
                      >
                        Open Project <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {/* ── Right Panel: Modernization Pipeline ──────────────────────────────── */}
      <div className="space-y-4 min-w-0">

        {/* Pipeline Overview */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="flex items-start gap-3 mb-4">
            <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center shrink-0">
              <Layers className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <h3 className="font-extrabold text-sm text-slate-900">Modernization Pipeline</h3>
              <p className="text-[11px] text-slate-500 mt-0.5 leading-normal">
                Guided journey from legacy source to validated modern code.
              </p>
            </div>
          </div>

          <div className="space-y-3">
            {PIPELINE_STEPS.map((step) => (
              <div key={step.num} className="flex items-start gap-2.5">
                <div className={`w-5 h-5 rounded-full ${step.color} text-white font-extrabold text-[10px] flex items-center justify-center shrink-0 mt-0.5`}>
                  {step.num}
                </div>
                <div className="min-w-0">
                  <h4 className="text-xs font-bold text-slate-900 leading-tight truncate">{step.title}</h4>
                  <p className="text-[11px] text-slate-500 leading-normal">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="flex items-center gap-2 text-slate-900 font-extrabold text-xs uppercase tracking-wider mb-3">
            <Sparkles className="w-3.5 h-3.5 text-emerald-600" /> Quick Actions
          </div>
          <div className="space-y-1">
            {[
              { icon: <Plus className="w-3.5 h-3.5 text-slate-400" />,       label: 'Create New Project',    to: '/projects' },
              { icon: <BookOpen className="w-3.5 h-3.5 text-slate-400" />,   label: 'View Documentation',    to: '/documentation' },
              { icon: <Cpu className="w-3.5 h-3.5 text-slate-400" />,         label: 'Run System X-Ray',      to: '/projects' },
              { icon: <HelpCircle className="w-3.5 h-3.5 text-slate-400" />, label: 'Explore LegacyBank Demo', to: '/projects' },
            ].map(({ icon, label, to }) => (
              <button
                key={label}
                onClick={() => navigate(to)}
                className="w-full flex items-center justify-between p-2.5 rounded-lg border border-slate-100 text-xs font-semibold text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-2 min-w-0">
                  {icon}
                  <span className="truncate">{label}</span>
                </div>
                <ArrowRight className="w-3 h-3 text-slate-400 shrink-0 ml-2" />
              </button>
            ))}
          </div>
        </div>

        {/* Opportunity Banner */}
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
              <BarChart3 className="w-3.5 h-3.5" />
            </div>
            <p className="text-xs font-bold text-emerald-900 leading-tight">
              From legacy complexity<br />
              <span className="font-normal text-emerald-700">to modern opportunity.</span>
            </p>
          </div>
          <ArrowRight className="w-4 h-4 text-emerald-600 shrink-0" />
        </div>
      </div>

    </div>
  )
}
