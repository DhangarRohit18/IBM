import React from 'react'
import type { BusinessRule } from '../../services/api'
import { GitBranch, ShieldCheck } from 'lucide-react'

interface BusinessRuleGraphProps {
  rules: BusinessRule[]
  selectedRuleId?: string
}

export const BusinessRuleGraph: React.FC<BusinessRuleGraphProps> = ({
  rules,
  selectedRuleId,
}) => {
  const selectedRule = rules.find((r) => r.id === selectedRuleId) || rules[0]

  if (!selectedRule || !selectedRule.rule_trace || selectedRule.rule_trace.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 bg-slate-950/40 rounded-lg border border-slate-800">
        <GitBranch className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm font-medium">Select a business rule to view deterministic rule trace.</p>
      </div>
    )
  }

  const steps = selectedRule.rule_trace

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-bold text-slate-200">Deterministic Rule Flow Trace</h3>
        </div>
        <span className="text-xs font-mono text-slate-400">{selectedRule.title}</span>
      </div>

      {/* SVG Rule Trace Diagram */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 py-4 overflow-x-auto">
        {steps.map((step, idx) => (
          <React.Fragment key={idx}>
            <div className="flex-1 min-w-[200px] bg-slate-950 p-4 rounded-lg border border-slate-800 shadow-md">
              <span className="inline-block px-2 py-0.5 text-[10px] font-bold rounded bg-cyan-950 text-cyan-300 border border-cyan-800 mb-2">
                {step.step_type}
              </span>
              <h5 className="text-xs font-bold text-slate-200 mb-1">{step.label}</h5>
              {step.details && <p className="text-[11px] font-mono text-slate-400 truncate">{step.details}</p>}
              {step.line_number && <span className="text-[10px] text-slate-500 block mt-2">Line {step.line_number}</span>}
            </div>

            {idx < steps.length - 1 && (
              <div className="text-slate-600 font-bold text-xl md:rotate-0 rotate-90 my-1 md:my-0">&rarr;</div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  )
}
