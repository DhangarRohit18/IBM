/**
 * LEGACYX — Platform Documentation Page.
 *
 * User & Architecture Guide with:
 *  - Shared PageHeader banner
 *  - IBM watsonx.ai Integration Callout
 *  - Core Principles cards
 *  - 8-Stage Pipeline with vertical timeline cards
 *  - IBM Technology Integration cards
 *
 * Layer: Presentation (AGENTS.md §1.3)
 */

import {
  BookOpen,
  Layers,
  CheckCircle2,
  ShieldCheck,
  Cpu,
  GitBranch,
  Map,
  GitFork,
  Code2,
  FlaskConical,
  HardDrive,
  Lock,
  Users,
} from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'

const PIPELINE_STEPS = [
  {
    num: '01',
    color: 'bg-blue-600',
    textColor: 'text-blue-700',
    bg: 'bg-blue-50',
    title: 'Repository Ingestion',
    icon: HardDrive,
    desc: 'Secure ZIP upload, SHA-256 integrity checksum, Zip Slip protection, recursive file indexer, and technology detection (Java, Spring, Maven, Gradle).',
  },
  {
    num: '02',
    color: 'bg-cyan-600',
    textColor: 'text-cyan-700',
    bg: 'bg-cyan-50',
    title: 'System X-Ray',
    icon: Cpu,
    desc: 'Pure-Python Java AST parsing using javalang, 8 architectural classifications (Controller, Service, Entity, etc.), conservative relationship resolution, and interactive SVG architecture graph.',
  },
  {
    num: '03',
    color: 'bg-emerald-600',
    textColor: 'text-emerald-700',
    bg: 'bg-emerald-50',
    title: 'Business Logic Recovery',
    icon: BookOpen,
    desc: 'Deterministic candidate business rule extraction from source constructs, natural language explanations via AIGateway, and human rule review and editing.',
  },
  {
    num: '04',
    color: 'bg-amber-600',
    textColor: 'text-amber-700',
    bg: 'bg-amber-50',
    title: 'Impact Analysis',
    icon: GitBranch,
    desc: 'Recursive graph traversal to compute direct and transitive caller relationships, blast radius metrics, affected rules, and AI risk narratives.',
  },
  {
    num: '05',
    color: 'bg-orange-600',
    textColor: 'text-orange-700',
    bg: 'bg-orange-50',
    title: 'Modernization Strategy',
    icon: Map,
    desc: 'Evidence-backed strategy scoring matrix (MODULARIZE, REFACTOR, STRANGLER_FIG), decision trace rationale, and human override gates.',
  },
  {
    num: '06',
    color: 'bg-rose-600',
    textColor: 'text-rose-700',
    bg: 'bg-rose-50',
    title: 'Execution Plan',
    icon: GitFork,
    desc: 'Topological Directed Acyclic Graph (DAG) task planner, task dependency ordering, prerequisite tracking, and plan approval state machine.',
  },
  {
    num: '07',
    color: 'bg-purple-600',
    textColor: 'text-purple-700',
    bg: 'bg-purple-50',
    title: 'Code Transformation',
    icon: Code2,
    desc: 'Isolated modernized code artifact generation, side-by-side unified patch diff viewer, original source immutability, and proposal approval gates.',
  },
  {
    num: '08',
    color: 'bg-indigo-700',
    textColor: 'text-indigo-700',
    bg: 'bg-indigo-50',
    title: 'Behavioral Validation',
    icon: FlaskConical,
    desc: 'Isolated sandbox compilation (javac), unit test runner, deterministic scenario output comparison (MATCH / MISMATCH), and AI evidence explanation.',
  },
]

const PRINCIPLES = [
  {
    icon: <CheckCircle2 className="w-4 h-4 text-teal-600" />,
    bg: 'bg-teal-50 border-teal-200',
    title: 'Deterministic First',
    body: 'AST facts, call graphs, class kinds, line evidence, and empirical test outputs are computed 100% deterministically. AI is never the source of truth for repository facts.',
  },
  {
    icon: <Lock className="w-4 h-4 text-amber-600" />,
    bg: 'bg-amber-50 border-amber-200',
    title: 'Immutable Source',
    body: 'Original legacy source code in storage/extracted/ is strictly read-only. Transformed artifacts are stored in isolated directories.',
  },
  {
    icon: <Users className="w-4 h-4 text-indigo-600" />,
    bg: 'bg-indigo-50 border-indigo-200',
    title: 'Human-in-the-Loop',
    body: 'Every modernization stage requires explicit human approval state machine transitions (PROPOSED → APPROVED → VALIDATED).',
  },
]

export function DocumentationPage() {
  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Page Header */}
      <PageHeader
        eyebrowIcon={<BookOpen className="w-3.5 h-3.5" />}
        eyebrow="Platform Documentation & Reference Guide"
        title="LEGACYX User & Architecture Guide"
        subtitle="LEGACYX is an evidence-backed legacy application modernization and behavioral validation platform. It combines deterministic static analysis with controlled AI explanations and human approval authority."
      />

      {/* IBM watsonx.ai Hero Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 rounded-2xl p-6 shadow-md text-white flex flex-col md:flex-row md:items-center justify-between gap-5">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-xl bg-blue-600/90 text-white flex items-center justify-center shrink-0 shadow-lg ring-1 ring-blue-400/40">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold tracking-widest uppercase text-blue-400">
                Exclusive AI Integration
              </span>
              <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-blue-500/20 text-blue-300 border border-blue-400/30 font-mono">
                IBM watsonx.ai
              </span>
            </div>
            <h3 className="text-lg font-black tracking-tight text-white">
              Powered by IBM watsonx.ai (granite-3-3-8b-instruct)
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">
              All AI reasoning is isolated in a central AI Gateway. AI provides natural language explanations and modernization recommendations over deterministic evidence without ever inventing repository facts.
            </p>
          </div>
        </div>
      </div>

      {/* Core Principles 3-Column Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {PRINCIPLES.map(({ icon, bg, title, body }) => (
          <div key={title} className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-2xs space-y-3">
            <div className={`w-9 h-9 rounded-xl border ${bg} flex items-center justify-center`}>
              {icon}
            </div>
            <div>
              <h3 className="text-sm font-extrabold text-slate-900">{title}</h3>
              <p className="text-xs text-slate-600 leading-relaxed mt-1">{body}</p>
            </div>
          </div>
        ))}
      </div>

      {/* 8-Stage Modernization Pipeline */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-2xs space-y-5">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-slate-900 text-teal-400 flex items-center justify-center shadow-xs">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-extrabold text-slate-900">The 8-Stage Modernization Methodology</h2>
              <p className="text-xs text-slate-500">Structured lifecycle gates from legacy ingestion to behavioral validation</p>
            </div>
          </div>
          <span className="text-xs font-mono font-bold text-slate-400 hidden sm:inline">Phases 3 — 9</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {PIPELINE_STEPS.map((step) => {
            const Icon = step.icon
            return (
              <div
                key={step.num}
                className="bg-slate-50/60 border border-slate-200/80 rounded-xl p-4 flex items-start gap-3.5 hover:border-slate-300 hover:bg-white transition-all shadow-2xs"
              >
                <div className={`w-8 h-8 rounded-lg ${step.bg} border border-slate-200 flex items-center justify-center shrink-0`}>
                  <Icon className={`w-4 h-4 ${step.textColor}`} />
                </div>
                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="text-xs font-extrabold text-slate-900 truncate">{step.title}</h3>
                    <span className="text-[10px] font-mono font-bold text-slate-400 shrink-0">Stage {step.num}</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">{step.desc}</p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* IBM Technology Integration Details */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-2xs space-y-4">
        <h2 className="text-base font-extrabold text-slate-900">IBM Technology Architectural Specifications</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            {
              label: 'AI PROVIDER',
              value: 'IBM watsonx.ai',
              detail: 'granite-3-3-8b-instruct — used for natural language explanation, rule summarization, and risk narrative generation.',
              accent: 'border-l-blue-500',
            },
            {
              label: 'INTEGRATION PATTERN',
              value: 'Centralized AI Gateway',
              detail: 'All AI provider calls route through backend/app/ai/ — strictly forbidden from direct execution in routes or services.',
              accent: 'border-l-teal-500',
            },
            {
              label: 'AI ROLE',
              value: 'Reasoning Layer Only',
              detail: 'AI reasons over established facts but never invents file paths, class names, dependencies, or test execution results.',
              accent: 'border-l-amber-500',
            },
            {
              label: 'GOVERNANCE',
              value: 'Human Approval Gates',
              detail: 'AI outputs remain strictly advisory. Explicit human approval is required before state transitions take effect.',
              accent: 'border-l-indigo-500',
            },
          ].map(({ label, value, detail, accent }) => (
            <div key={label} className={`border border-slate-200 border-l-4 ${accent} rounded-xl p-4 space-y-1 bg-slate-50/50`}>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{label}</div>
              <div className="text-sm font-black text-slate-900">{value}</div>
              <p className="text-xs text-slate-600 leading-relaxed">{detail}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
