import React from 'react'
import type { ImpactSummary } from '../../services/api'
import { AlertCircle, Box, GitMerge, ShieldAlert, CheckCircle2 } from 'lucide-react'

interface ImpactSummaryCardsProps {
  summary: ImpactSummary
  status: string
  hasEvidencedImpact: boolean
  targetName: string
}

export const ImpactSummaryCards: React.FC<ImpactSummaryCardsProps> = ({
  summary,
  status,
  hasEvidencedImpact,
  targetName,
}) => {
  return (
    <div className="space-y-4">
      {/* Explicit NO EVIDENCED IMPACT Banner */}
      {!hasEvidencedImpact || status === 'NO_EVIDENCED_IMPACT' ? (
        <div className="bg-emerald-950/40 border border-emerald-500/40 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-6 h-6 text-emerald-400 flex-shrink-0" />
            <div>
              <h4 className="text-sm font-semibold text-emerald-200">
                NO EVIDENCED IMPACT DETECTED
              </h4>
              <p className="text-xs text-emerald-400/90 mt-0.5">
                No deterministic call relationships, structural imports, or business rule associations were found for{' '}
                <span className="font-semibold">{targetName}</span> within the selected traversal depth.
              </p>
            </div>
          </div>
          <span className="text-xs px-2.5 py-1 bg-emerald-900/60 text-emerald-300 rounded font-mono font-bold">
            0 Ripple Effects
          </span>
        </div>
      ) : (
        <div className="bg-indigo-950/40 border border-indigo-500/40 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ShieldAlert className="w-6 h-6 text-indigo-400 flex-shrink-0" />
            <div>
              <h4 className="text-sm font-semibold text-indigo-200">
                EVIDENCED IMPACT DETECTED
              </h4>
              <p className="text-xs text-indigo-300/80 mt-0.5">
                Deterministic graph analysis established verified impact paths originating from{' '}
                <span className="font-semibold text-indigo-200">{targetName}</span>.
              </p>
            </div>
          </div>
          <span className="text-xs px-2.5 py-1 bg-indigo-900/60 text-indigo-300 rounded font-mono font-bold">
            {summary.total_impacted_nodes} Total Impacted Nodes
          </span>
        </div>
      )}

      {/* Metrics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 border border-gray-700/80 rounded-lg p-4">
          <div className="flex items-center justify-between text-gray-400 text-xs font-medium mb-1">
            <span>Direct Components</span>
            <Box className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white">{summary.direct_component_count}</div>
          <p className="text-[11px] text-gray-400 mt-1">Immediate static evidence (depth = 1)</p>
        </div>

        <div className="bg-gray-800 border border-gray-700/80 rounded-lg p-4">
          <div className="flex items-center justify-between text-gray-400 text-xs font-medium mb-1">
            <span>Transitive Components</span>
            <GitMerge className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-white">{summary.transitive_component_count}</div>
          <p className="text-[11px] text-gray-400 mt-1">Indirect downstream (depth &gt; 1)</p>
        </div>

        <div className="bg-gray-800 border border-gray-700/80 rounded-lg p-4">
          <div className="flex items-center justify-between text-gray-400 text-xs font-medium mb-1">
            <span>Direct Business Rules</span>
            <ShieldAlert className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-white">{summary.direct_rule_count}</div>
          <p className="text-[11px] text-gray-400 mt-1">Rules in target / direct components</p>
        </div>

        <div className="bg-gray-800 border border-gray-700/80 rounded-lg p-4">
          <div className="flex items-center justify-between text-gray-400 text-xs font-medium mb-1">
            <span>Transitive Rules</span>
            <AlertCircle className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold text-white">{summary.transitive_rule_count}</div>
          <p className="text-[11px] text-gray-400 mt-1">Rules in indirect dependent components</p>
        </div>
      </div>
    </div>
  )
}
