import React from 'react'
import type { RulePreservationItem } from '../../services/api'
import { ShieldCheck } from 'lucide-react'

interface BusinessRulesPreservationCardProps {
  rules: RulePreservationItem[]
}

export const BusinessRulesPreservationCard: React.FC<BusinessRulesPreservationCardProps> = ({ rules }) => {
  return (
    <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-white flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          Business Logic to Preserve ({rules.length})
        </h4>
        <span className="text-[11px] text-gray-400 font-mono">Phase 4 Recovery Link</span>
      </div>

      {rules.length === 0 ? (
        <p className="text-xs text-gray-400 italic">No business rules associated with this component.</p>
      ) : (
        <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
          {rules.map((rule, idx) => (
            <div key={idx} className="bg-gray-900 border border-gray-700/60 rounded p-3 text-xs space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-emerald-200">{rule.title}</span>
                <span className="px-2 py-0.5 bg-emerald-900/40 text-emerald-300 rounded font-mono text-[10px]">
                  {rule.rule_type}
                </span>
              </div>
              {rule.condition && (
                <div className="bg-gray-950 p-2 rounded border border-gray-800 font-mono text-[11px] text-emerald-400/90">
                  Condition: {rule.condition}
                </div>
              )}
              {rule.file_path && (
                <div className="text-[10px] text-gray-400 font-mono">
                  {rule.file_path}:{rule.line_start}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
