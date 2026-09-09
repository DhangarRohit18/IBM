import React, { useState } from 'react'
import type { BusinessRule } from '../../services/api'
import {
  Sparkles,
  CheckCircle2,
  XCircle,
  FileCode,
  ArrowRight,
  ShieldCheck,
  Code2,
  RefreshCw,
  Info,
} from 'lucide-react'

interface RuleDetailDrawerProps {
  rule: BusinessRule
  onClose: () => void
  onExplain: (ruleId: string) => Promise<void>
  onReview: (ruleId: string, status: 'REVIEWED' | 'REJECTED', notes?: string) => Promise<void>
  onViewSource?: (filePath: string, lineStart: number) => void
}

export const RuleDetailDrawer: React.FC<RuleDetailDrawerProps> = ({
  rule,
  onClose,
  onExplain,
  onReview,
  onViewSource,
}) => {
  const [isExplaining, setIsExplaining] = useState(false)
  const [isReviewing, setIsReviewing] = useState(false)
  const [reviewNotes, setReviewNotes] = useState(rule.review_notes || '')

  const handleExplain = async () => {
    setIsExplaining(true)
    try {
      await onExplain(rule.id)
    } finally {
      setIsExplaining(false)
    }
  }

  const handleStatusUpdate = async (newStatus: 'REVIEWED' | 'REJECTED') => {
    setIsReviewing(true)
    try {
      await onReview(rule.id, newStatus, reviewNotes)
    } finally {
      setIsReviewing(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-slate-900 border-l border-slate-800 w-full overflow-y-auto">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between sticky top-0 z-10">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 text-xs font-semibold rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              {rule.rule_type}
            </span>
            <span className="px-2 py-0.5 text-xs font-semibold rounded bg-slate-800 text-slate-300 border border-slate-700">
              {rule.status}
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100">{rule.title}</h3>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-200 text-xl font-bold p-1"
        >
          &times;
        </button>
      </div>

      <div className="p-5 space-y-6 flex-1">
        {/* 1. Deterministic Facts Panel */}
        <section className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-3">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Code2 className="w-4 h-4 text-cyan-400" />
            Authoritative Deterministic Facts
          </h4>

          <div className="grid grid-cols-1 gap-2 font-mono text-xs text-slate-200">
            {rule.condition_expression && (
              <div className="bg-slate-900/80 p-2.5 rounded border border-slate-800">
                <span className="text-amber-400 font-semibold block mb-0.5">CONDITION (IF)</span>
                <code>{rule.condition_expression}</code>
              </div>
            )}

            {rule.threshold_value && (
              <div className="bg-slate-900/80 p-2.5 rounded border border-slate-800 flex gap-4">
                <div>
                  <span className="text-amber-400 font-semibold block mb-0.5">THRESHOLD OPERATOR</span>
                  <code>{rule.threshold_operator || '=='}</code>
                </div>
                <div>
                  <span className="text-amber-400 font-semibold block mb-0.5">THRESHOLD VALUE</span>
                  <code>{rule.threshold_value}</code>
                </div>
              </div>
            )}

            {rule.calculation_formula && (
              <div className="bg-slate-900/80 p-2.5 rounded border border-slate-800">
                <span className="text-blue-400 font-semibold block mb-0.5">CALCULATION FORMULA</span>
                <code>{rule.calculation_formula}</code>
              </div>
            )}

            {rule.action_expression && (
              <div className="bg-slate-900/80 p-2.5 rounded border border-slate-800">
                <span className="text-emerald-400 font-semibold block mb-0.5">PROMOTED ACTION (THEN)</span>
                <code>{rule.action_expression}</code>
              </div>
            )}

            {rule.new_state && (
              <div className="bg-slate-900/80 p-2.5 rounded border border-slate-800 flex gap-4">
                <div>
                  <span className="text-purple-400 font-semibold block mb-0.5">PREVIOUS STATE</span>
                  <code>{rule.previous_state || 'UNKNOWN'}</code>
                </div>
                <div>
                  <span className="text-purple-400 font-semibold block mb-0.5">NEW STATE</span>
                  <code>{rule.new_state}</code>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* 2. Deterministic Rule Trace */}
        {rule.rule_trace && rule.rule_trace.length > 0 && (
          <section className="space-y-2">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Deterministic Rule Trace
            </h4>
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-2">
              {rule.rule_trace.map((step, idx) => (
                <div key={idx} className="flex items-center gap-3 text-xs font-mono bg-slate-900 p-2 rounded border border-slate-800">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950 text-cyan-400 border border-cyan-800">
                    {step.step_type}
                  </span>
                  <span className="text-slate-200 font-medium flex-1">{step.label}</span>
                  {idx < rule.rule_trace.length - 1 && <ArrowRight className="w-3.5 h-3.5 text-slate-600" />}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* 3. AI Explanation (Stored Separately from Facts) */}
        <section className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-blue-400" />
              Supplementary AI Business Explanation
            </h4>
            <button
              onClick={handleExplain}
              disabled={isExplaining}
              className="px-3 py-1 text-xs font-medium bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded shadow-sm flex items-center gap-1.5 transition-colors"
            >
              {isExplaining ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  {rule.ai_explanation ? 'Re-Explain with AI' : 'Explain with AI'}
                </>
              )}
            </button>
          </div>

          {rule.ai_explanation ? (
            <div className="p-3 bg-blue-950/20 border border-blue-800/40 rounded text-sm text-slate-200 leading-relaxed">
              {rule.ai_explanation}
            </div>
          ) : (
            <div className="p-3 bg-slate-900/50 border border-slate-800 rounded text-xs text-slate-400 flex items-center gap-2">
              <Info className="w-4 h-4 text-slate-500 flex-shrink-0" />
              <span>AI explanation not requested. Click "Explain with AI" to generate a human-readable summary.</span>
            </div>
          )}
        </section>

        {/* 4. Line Evidence & Source Code Navigation */}
        <section className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <FileCode className="w-4 h-4 text-purple-400" />
              Line-Level Source Evidence
            </h4>
            {onViewSource && (
              <button
                onClick={() => onViewSource(rule.relative_file_path, rule.line_start)}
                className="px-3 py-1 text-xs font-medium bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 rounded flex items-center gap-1.5 transition-colors"
              >
                <FileCode className="w-3.5 h-3.5" />
                View Source
              </button>
            )}
          </div>

          <div className="space-y-1.5 text-xs font-mono text-slate-300 bg-slate-900 p-3 rounded border border-slate-800">
            <div>
              <span className="text-slate-500">File: </span>
              <span className="text-slate-200 font-semibold">{rule.relative_file_path}</span>
            </div>
            <div>
              <span className="text-slate-500">Lines: </span>
              <span className="text-amber-400 font-semibold">{rule.line_start} &ndash; {rule.line_end}</span>
            </div>
            <div>
              <span className="text-slate-500">Construct: </span>
              <span className="text-cyan-400 font-semibold">{rule.source_construct}</span>
            </div>
            <div>
              <span className="text-slate-500">Reason: </span>
              <span className="text-slate-300">{rule.extraction_reason}</span>
            </div>
          </div>
        </section>

        {/* 5. Engineer Review & Audit Trail */}
        <section className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-3">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Engineer Review Workflow
          </h4>

          <div className="space-y-2">
            <textarea
              placeholder="Add optional review notes or rationale..."
              value={reviewNotes}
              onChange={(e) => setReviewNotes(e.target.value)}
              className="w-full p-2.5 text-xs bg-slate-900 border border-slate-700 rounded text-slate-200 focus:outline-none focus:border-cyan-500"
              rows={2}
            />

            <div className="flex gap-2">
              <button
                onClick={() => handleStatusUpdate('REVIEWED')}
                disabled={isReviewing}
                className="flex-1 py-1.5 text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded flex items-center justify-center gap-1.5 transition-colors"
              >
                <CheckCircle2 className="w-4 h-4" />
                Mark Reviewed
              </button>
              <button
                onClick={() => handleStatusUpdate('REJECTED')}
                disabled={isReviewing}
                className="flex-1 py-1.5 text-xs font-semibold bg-red-600/80 hover:bg-red-600 disabled:opacity-50 text-white rounded flex items-center justify-center gap-1.5 transition-colors"
              >
                <XCircle className="w-4 h-4" />
                Reject Candidate
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
