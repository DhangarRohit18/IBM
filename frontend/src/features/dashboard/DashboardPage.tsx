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
      setError('Unable to load projects from backend API. Ensure backend is running.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProjects()
  }, [])

  // Real derived metrics
  const totalProjects = projects.length
  const analyzedCount = projects.filter(p => p.status === 'ANALYZED' || p.status === 'READY').length
  const inProgressCount = projects.filter(p => p.status === 'INGESTING' || p.status === 'ANALYZING').length
  const completedCount = projects.filter(p => p.status === 'ANALYZED').length

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      {/* Main Center & Left Column (8 cols) */}
      <div className="lg:col-span-8 space-y-6">
        {/* Welcome Hero Banner */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-sky-100 via-sky-50 to-blue-100 border border-sky-200/80 p-7 shadow-xs">
          {/* Decorative Right Mountain Landscape */}
          <div className="absolute right-0 top-0 bottom-0 w-1/2 opacity-85 pointer-events-none mix-blend-multiply hidden sm:block">
            <svg viewBox="0 0 500 300" className="w-full h-full object-cover">
              <path fill="#0284c7" fillOpacity="0.15" d="M150,300 L280,100 L410,300 Z" />
              <path fill="#0369a1" fillOpacity="0.25" d="M220,300 L350,60 L480,300 Z" />
              <path fill="#0f172a" fillOpacity="0.35" d="M300,300 L420,120 L520,300 Z" />
            </svg>
          </div>

          <div className="relative z-10 max-w-xl space-y-4">
            <span className="text-[11px] font-extrabold tracking-wider text-slate-500 uppercase">
              WELCOME TO LEGACYX
            </span>
            <h1 className="text-3xl sm:text-4xl font-black text-slate-900 leading-tight">
              Turn Legacy into <br />
              What's <span className="text-emerald-600">Next</span>
            </h1>
            <p className="text-sm text-slate-600 leading-relaxed font-normal">
              Discover business logic, understand impact, generate modernization plans, and validate with confidence.
            </p>

            {/* Feature Pills */}
            <div className="flex flex-wrap gap-2.5 pt-2">
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-white/90 backdrop-blur-xs rounded-lg text-xs font-semibold text-slate-700 shadow-2xs border border-slate-200/60">
                <FileText className="w-3.5 h-3.5 text-blue-600" />
                <span>Evidence-Driven</span>
              </div>
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-white/90 backdrop-blur-xs rounded-lg text-xs font-semibold text-slate-700 shadow-2xs border border-slate-200/60">
                <Network className="w-3.5 h-3.5 text-blue-600" />
                <span>Human-in-the-Loop</span>
              </div>
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-white/90 backdrop-blur-xs rounded-lg text-xs font-semibold text-slate-700 shadow-2xs border border-slate-200/60">
                <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                <span>AI-Powered Insights</span>
              </div>
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-white/90 backdrop-blur-xs rounded-lg text-xs font-semibold text-slate-700 shadow-2xs border border-slate-200/60">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                <span>Safe & Controlled</span>
              </div>
            </div>
          </div>

          {/* Quote Overlay Badge */}
          <div className="absolute right-6 bottom-6 max-w-xs p-3 rounded-xl bg-slate-900/80 backdrop-blur-md text-white border border-slate-700/50 hidden md:block">
            <p className="text-[11px] font-medium italic text-slate-200 leading-snug">
              "Understand your systems. Modernize with evidence. Move forward with confidence."
            </p>
          </div>
        </div>

        {/* Your Projects Section Header */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <Folder className="w-5 h-5 text-slate-900" />
                <h2 className="text-xl font-extrabold text-slate-900">Your Projects</h2>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Create or select a project to begin your modernization journey.
              </p>
            </div>
            <button
              onClick={() => navigate('/projects')}
              className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow-xs transition-all cursor-pointer"
            >
              <Plus className="w-4 h-4" /> New Project
            </button>
          </div>

          {/* Metrics Row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3.5 shadow-2xs">
              <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
                <Folder className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xl font-extrabold text-slate-900">{totalProjects}</div>
                <div className="text-xs text-slate-500 font-medium">Total Projects</div>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3.5 shadow-2xs">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
                <BarChart3 className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xl font-extrabold text-slate-900">{analyzedCount}</div>
                <div className="text-xs text-slate-500 font-medium">Analyzed</div>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3.5 shadow-2xs">
              <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xl font-extrabold text-slate-900">{inProgressCount}</div>
                <div className="text-xs text-slate-500 font-medium">In Progress</div>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3.5 shadow-2xs">
              <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xl font-extrabold text-slate-900">{completedCount}</div>
                <div className="text-xs text-slate-500 font-medium">Completed</div>
              </div>
            </div>
          </div>

          {/* Project Cards Grid / States */}
          {loading ? (
            <div className="p-12 text-center text-xs text-slate-400 border border-slate-200 rounded-xl bg-white">
              Loading projects from backend API...
            </div>
          ) : error ? (
            <div className="p-6 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800 flex items-center justify-between gap-4">
              <span>{error}</span>
              <button
                onClick={loadProjects}
                className="px-3 py-1.5 rounded-lg bg-rose-600 text-white font-bold hover:bg-rose-700 cursor-pointer shrink-0"
              >
                Retry
              </button>
            </div>
          ) : projects.length === 0 ? (
            <div className="p-12 text-center text-xs border border-dashed border-slate-300 rounded-xl bg-white space-y-3">
              <Folder className="w-8 h-8 text-slate-300 mx-auto" />
              <div className="font-bold text-slate-700">No projects found in database</div>
              <p className="text-slate-500 max-w-sm mx-auto">
                Create your first legacy application project to ingest source code and start the 8-stage modernization pipeline.
              </p>
              <button
                onClick={() => navigate('/projects')}
                className="px-4 py-2 bg-emerald-600 text-white font-bold rounded-lg hover:bg-emerald-700 cursor-pointer inline-flex items-center gap-1.5"
              >
                <Plus className="w-4 h-4" /> Create New Project
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
              {projects.map((project, index) => {
                const isAnalyzed = project.status === 'ANALYZED' || project.status === 'READY'
                return (
                  <div
                    key={project.id || index}
                    className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-2xs hover:shadow-md transition-all flex flex-col justify-between"
                  >
                    <div>
                      {/* Thumbnail & Badge Header */}
                      <div className="relative h-28 bg-slate-900 overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-900/50 to-transparent z-10" />
                        <div className="absolute top-3 left-3 z-20">
                          <span
                            className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wide ${
                              isAnalyzed
                                ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                                : 'bg-blue-100 text-blue-800 border border-blue-300'
                            }`}
                          >
                            {project.status}
                          </span>
                        </div>
                        <button className="absolute top-3 right-3 z-20 text-slate-300 hover:text-white p-1">
                          <MoreHorizontal className="w-4 h-4" />
                        </button>

                        {/* Visual Architecture Art */}
                        <div className="w-full h-full opacity-40 bg-gradient-to-tr from-blue-900 via-teal-900 to-slate-900 flex items-center justify-center">
                          <Layers className="w-12 h-12 text-white/50" />
                        </div>
                      </div>

                      {/* Card Content Body */}
                      <div className="p-4 space-y-2">
                        <h3 className="font-bold text-sm text-slate-900 truncate">{project.name}</h3>
                        <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
                          {project.description || 'Legacy application repository modernization workspace'}
                        </p>
                      </div>
                    </div>

                    {/* Progress & Actions Footer */}
                    <div className="p-4 pt-0 space-y-3">
                      {/* Progress Bar */}
                      <div className="space-y-1">
                        <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden flex">
                          <div
                            className={`h-full ${isAnalyzed ? 'bg-emerald-500 w-3/4' : 'bg-blue-500 w-1/4'}`}
                          />
                        </div>
                        <div className="flex justify-between text-[10px] text-slate-400 font-medium">
                          <span>{isAnalyzed ? '6/8 phases completed' : 'Repository ingested'}</span>
                          <span>Created {new Date(project.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>

                      {/* Open Project CTA */}
                      <button
                        onClick={() => navigate(`/projects/${project.id}`)}
                        className={`w-full py-2 px-3 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
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

      {/* Right Sidebar Column (4 cols) */}
      <div className="lg:col-span-4 space-y-6">
        {/* Modernization Pipeline Overview Card */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs space-y-4">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center font-bold flex-shrink-0">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-sm text-slate-900">Modernization Pipeline</h3>
              <p className="text-xs text-slate-500 mt-0.5 leading-normal">
                A guided journey from legacy source code to validated modern code.
              </p>
            </div>
          </div>

          {/* 8-Stage Step List matching screenshot */}
          <div className="space-y-3 pt-1">
            {[
              { num: 1, color: 'bg-blue-500', title: 'Repository Ingestion', desc: 'Upload and index legacy source code' },
              { num: 2, color: 'bg-cyan-500', title: 'System X-Ray', desc: 'Discover structure and relationships' },
              { num: 3, color: 'bg-emerald-500', title: 'Business Logic Recovery', desc: 'Extract and preserve business rules' },
              { num: 4, color: 'bg-amber-500', title: 'Impact Analysis', desc: 'Understand dependencies and risk' },
              { num: 5, color: 'bg-orange-500', title: 'Modernization Strategy', desc: 'Get evidence-based recommendations' },
              { num: 6, color: 'bg-rose-500', title: 'Execution Plan', desc: 'Generate a step-by-step plan' },
              { num: 7, color: 'bg-purple-500', title: 'Code Transformation', desc: 'Generate modernized code (isolated)' },
              { num: 8, color: 'bg-indigo-600', title: 'Validation', desc: 'Build, test and verify behavioral equivalence' },
            ].map((step) => (
              <div key={step.num} className="flex items-start gap-3">
                <div
                  className={`w-6 h-6 rounded-full ${step.color} text-white font-extrabold text-xs flex items-center justify-center flex-shrink-0 mt-0.5 shadow-2xs`}
                >
                  {step.num}
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900 leading-tight">{step.title}</h4>
                  <p className="text-[11px] text-slate-500 leading-normal">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions Card */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs space-y-3">
          <div className="flex items-center gap-2 text-slate-900 font-extrabold text-xs uppercase tracking-wider">
            <Sparkles className="w-4 h-4 text-emerald-600" /> Quick Actions
          </div>
          <div className="space-y-1.5 pt-1">
            <button
              onClick={() => navigate('/projects')}
              className="w-full flex items-center justify-between p-2.5 rounded-lg border border-slate-150 text-xs font-semibold text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-2">
                <Plus className="w-4 h-4 text-slate-400" />
                <span>Create New Project</span>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
            </button>

            <button
              onClick={() => navigate('/documentation')}
              className="w-full flex items-center justify-between p-2.5 rounded-lg border border-slate-150 text-xs font-semibold text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-slate-400" />
                <span>View Documentation</span>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
            </button>

            <button
              onClick={() => navigate('/projects')}
              className="w-full flex items-center justify-between p-2.5 rounded-lg border border-slate-150 text-xs font-semibold text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-slate-400" />
                <span>Run System X-Ray</span>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
            </button>

            <button
              onClick={() => navigate('/projects')}
              className="w-full flex items-center justify-between p-2.5 rounded-lg border border-slate-150 text-xs font-semibold text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-slate-400" />
                <span>Explore LegacyBank Demo</span>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
            </button>
          </div>
        </div>

        {/* Opportunity Callout Banner */}
        <div className="bg-emerald-50/70 border border-emerald-200/80 rounded-xl p-4 flex items-center justify-between gap-3 text-emerald-900">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center flex-shrink-0">
              <BarChart3 className="w-4 h-4" />
            </div>
            <p className="text-xs font-bold leading-tight">
              From legacy complexity <br />
              <span className="text-emerald-700 font-normal">to modern opportunity.</span>
            </p>
          </div>
          <ArrowRight className="w-4 h-4 text-emerald-700 flex-shrink-0" />
        </div>
      </div>
    </div>
  )
}
