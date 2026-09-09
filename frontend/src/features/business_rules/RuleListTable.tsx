import React from 'react'
import type { BusinessRule, RuleType, RuleStatus } from '../../services/api'
import { Filter, Search, FileText, CheckCircle2, XCircle, Sparkles, Code2 } from 'lucide-react'

interface RuleListTableProps {
  rules: BusinessRule[]
  selectedRuleId?: string
  onSelectRule: (rule: BusinessRule) => void
  selectedType?: string
  onSelectType: (type: string | undefined) => void
  searchQuery: string
  onSearchChange: (query: string) => void
}

const typeBadges: Record<RuleType, { label: string; color: string }> = {
  VALIDATION: { label: 'Validation', color: 'bg-red-500/10 text-red-400 border-red-500/20' },
  THRESHOLD: { label: 'Threshold', color: 'bg-amber-500/10 text-amber-400 border-amber-500/20' },
  CALCULATION: { label: 'Calculation', color: 'bg-blue-500/10 text-blue-400 border-blue-500/20' },
  STATE_TRANSITION: { label: 'State Transition', color: 'bg-purple-500/10 text-purple-400 border-purple-500/20' },
  ACTION: { label: 'Action', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' },
  CONDITIONAL: { label: 'Conditional', color: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20' },
}

const statusBadges: Record<RuleStatus, { label: string; color: string; icon: React.ReactNode }> = {
  EXTRACTED: { label: 'Extracted', color: 'bg-slate-800 text-slate-300 border-slate-700', icon: <Code2 className="w-3 h-3" /> },
  EXPLAINED: { label: 'Explained', color: 'bg-blue-900/50 text-blue-300 border-blue-700/50', icon: <Sparkles className="w-3 h-3 text-blue-400" /> },
  REVIEWED: { label: 'Reviewed', color: 'bg-emerald-900/50 text-emerald-300 border-emerald-700/50', icon: <CheckCircle2 className="w-3 h-3 text-emerald-400" /> },
  REJECTED: { label: 'Rejected', color: 'bg-red-900/50 text-red-300 border-red-700/50', icon: <XCircle className="w-3 h-3 text-red-400" /> },
}

export const RuleListTable: React.FC<RuleListTableProps> = ({
  rules,
  selectedRuleId,
  onSelectRule,
  selectedType,
  onSelectType,
  searchQuery,
  onSearchChange,
}) => {
  const ruleTypes: (RuleType | 'ALL')[] = ['ALL', 'VALIDATION', 'THRESHOLD', 'CALCULATION', 'STATE_TRANSITION', 'ACTION', 'CONDITIONAL']

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
      {/* Header & Filter Controls */}
      <div className="p-4 border-b border-slate-800 bg-slate-950/50 flex flex-wrap gap-3 items-center justify-between">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search business rules, conditions, files..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-sm bg-slate-900 border border-slate-700 rounded-md text-slate-200 focus:outline-none focus:border-cyan-500 placeholder-slate-500"
          />
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto py-1">
          <Filter className="w-3.5 h-3.5 text-slate-500 mr-1" />
          {ruleTypes.map((t) => {
            const isActive = (t === 'ALL' && !selectedType) || selectedType === t
            return (
              <button
                key={t}
                onClick={() => onSelectType(t === 'ALL' ? undefined : t)}
                className={`px-2.5 py-1 text-xs font-medium rounded-full border transition-colors whitespace-nowrap ${
                  isActive
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                    : 'bg-slate-800/60 text-slate-400 border-slate-700 hover:bg-slate-800 hover:text-slate-300'
                }`}
              >
                {t === 'ALL' ? 'All Rules' : typeBadges[t as RuleType]?.label || t}
              </button>
            )
          })}
        </div>
      </div>

      {/* Rules Data Table */}
      <div className="flex-1 overflow-y-auto divide-y divide-slate-800/60">
        {rules.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm font-medium">No business rules discovered matching criteria.</p>
          </div>
        ) : (
          rules.map((rule) => {
            const isSelected = rule.id === selectedRuleId
            const tBadge = typeBadges[rule.rule_type] || { label: rule.rule_type, color: 'bg-slate-800 text-slate-400' }
            const sBadge = statusBadges[rule.status] || { label: rule.status, color: 'bg-slate-800 text-slate-400', icon: null }

            return (
              <div
                key={rule.id}
                onClick={() => onSelectRule(rule)}
                className={`p-4 cursor-pointer transition-colors border-l-2 ${
                  isSelected
                    ? 'bg-cyan-950/20 border-l-cyan-500'
                    : 'border-l-transparent hover:bg-slate-800/40'
                }`}
              >
                <div className="flex items-start justify-between gap-3 mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 text-xs font-semibold rounded border ${tBadge.color}`}>
                      {tBadge.label}
                    </span>
                    <span className={`px-2 py-0.5 text-xs font-medium rounded border flex items-center gap-1 ${sBadge.color}`}>
                      {sBadge.icon}
                      {sBadge.label}
                    </span>
                  </div>

                  <span className="text-xs font-mono text-slate-400 flex items-center gap-1">
                    <FileText className="w-3 h-3 text-slate-500" />
                    {rule.relative_file_path.split('/').pop()}:{rule.line_start}
                  </span>
                </div>

                <h4 className="text-sm font-semibold text-slate-200 mb-1">{rule.title}</h4>

                {/* Facts Summary */}
                <div className="bg-slate-950/60 p-2 rounded border border-slate-800/80 font-mono text-xs text-slate-300 space-y-0.5">
                  {rule.condition_expression && (
                    <div className="truncate">
                      <span className="text-amber-400 font-semibold">IF: </span>
                      {rule.condition_expression}
                    </div>
                  )}
                  {rule.calculation_formula && (
                    <div className="truncate">
                      <span className="text-blue-400 font-semibold">FORMULA: </span>
                      {rule.calculation_formula}
                    </div>
                  )}
                  {rule.action_expression && (
                    <div className="truncate">
                      <span className="text-emerald-400 font-semibold">THEN: </span>
                      {rule.action_expression}
                    </div>
                  )}
                  {rule.new_state && (
                    <div className="truncate">
                      <span className="text-purple-400 font-semibold">STATE: </span>
                      {rule.previous_state || 'UNKNOWN'} &rarr; {rule.new_state}
                    </div>
                  )}
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
