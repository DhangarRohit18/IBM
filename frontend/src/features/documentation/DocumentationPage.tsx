import { BookOpen, Layers, CheckCircle2, ShieldCheck, Cpu, GitBranch, Map, GitFork, Code2, FlaskConical, HardDrive } from 'lucide-react'

export function DocumentationPage() {
  const pipelineSteps = [
    { num: 1, title: 'Repository Ingestion', desc: 'Secure ZIP upload, SHA-256 integrity checksum, Zip Slip protection, recursive file indexer, and technology detection (Java, Spring, Maven, Gradle).', icon: HardDrive },
    { num: 2, title: 'System X-Ray', desc: 'Pure-Python Java AST parsing using javalang, 8 architectural classifications (Controller, Service, Entity, etc.), conservative relationship resolution, and interactive SVG architecture graph.', icon: Cpu },
    { num: 3, title: 'Business Logic Recovery', desc: 'Deterministic candidate business rule extraction from source constructs, natural language explanations via AIGateway, and human rule review and editing.', icon: BookOpen },
    { num: 4, title: 'Impact Analysis', desc: 'Recursive graph traversal to compute direct and transitive caller relationships, blast radius metrics, affected rules, and AI risk narratives.', icon: GitBranch },
    { num: 5, title: 'Modernization Strategy', desc: 'Evidence-backed strategy scoring matrix (MODULARIZE, REFACTOR, STRANGLER_FIG), decision trace rationale, and human override gates.', icon: Map },
    { num: 6, title: 'Execution Plan', desc: 'Topological Directed Acyclic Graph (DAG) task planner, task dependency ordering, prerequisite tracking, and plan approval state machine.', icon: GitFork },
    { num: 7, title: 'Code Transformation', desc: 'Isolated modernized code artifact generation, side-by-side unified patch diff viewer, original source immutability, and proposal approval gates.', icon: Code2 },
    { num: 8, title: 'Behavioral Validation', desc: 'Isolated sandbox compilation (javac), unit test runner, deterministic scenario output comparison (MATCH / MISMATCH), and AI evidence explanation.', icon: FlaskConical },
  ]

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xs space-y-2">
        <div className="flex items-center gap-2 text-teal-600 font-extrabold text-xs tracking-wider uppercase">
          <BookOpen className="w-4 h-4" /> Platform Documentation
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900">LEGACYX User & Architecture Guide</h1>
        <p className="text-xs text-slate-500 max-w-3xl leading-relaxed">
          LEGACYX is an evidence-backed legacy application modernization and behavioral validation platform.
          It combines deterministic static analysis with controlled AI explanations and human approval authority.
        </p>
      </div>

      {/* Core Principles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs space-y-2">
          <div className="flex items-center gap-2 text-teal-700 font-extrabold text-xs">
            <CheckCircle2 className="w-4 h-4" /> Deterministic First
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            AST facts, call graphs, class kinds, line evidence, and empirical test outputs are computed 100% deterministically. AI is never the source of truth for repository facts.
          </p>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs space-y-2">
          <div className="flex items-center gap-2 text-teal-700 font-extrabold text-xs">
            <ShieldCheck className="w-4 h-4" /> Immutable Source
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Original legacy source code in <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800">storage/extracted/</code> is strictly read-only. Transformed artifacts are stored in isolated directories.
          </p>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs space-y-2">
          <div className="flex items-center gap-2 text-teal-700 font-extrabold text-xs">
            <Layers className="w-4 h-4" /> Human-in-the-Loop
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Every modernization stage requires explicit human approval state machine transitions (<code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800">PROPOSED</code> → <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800">APPROVED</code> → <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800">VALIDATED</code>).
          </p>
        </div>
      </div>

      {/* 8-Stage Modernization Pipeline Guide */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xs space-y-4">
        <div className="flex items-center gap-2 text-slate-900 font-extrabold text-sm uppercase tracking-wider">
          <Layers className="w-4 h-4 text-teal-600" /> The 8-Stage Modernization Pipeline
        </div>

        <div className="space-y-4 pt-1">
          {pipelineSteps.map((step) => {
            const Icon = step.icon
            return (
              <div key={step.num} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 flex items-start gap-4">
                <div className="w-8 h-8 rounded-xl bg-teal-600 text-white font-extrabold text-xs flex items-center justify-center shrink-0 mt-0.5 shadow-2xs">
                  {step.num}
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4 text-teal-700" />
                    <h3 className="text-sm font-extrabold text-slate-900">{step.title}</h3>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">{step.desc}</p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
