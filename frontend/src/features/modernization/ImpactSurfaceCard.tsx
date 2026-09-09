import React from 'react'
import type { StrategyImpactSummary } from '../../services/api'
import { GitMerge } from 'lucide-react'

interface ImpactSurfaceCardProps {
  summary: StrategyImpactSummary
}

export const ImpactSurfaceCard: React.FC<ImpactSurfaceCardProps> = ({ summary }) => {
  return (
    <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-white flex items-center gap-2">
          <GitMerge className="w-4 h-4 text-purple-400" />
          Known Impact Surface (Phase 5 Traversal)
        </h4>
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs">
        <div className="bg-gray-900 border border-gray-700/60 rounded p-3">
          <div className="text-gray-400 mb-1">Direct Dependents (Depth = 1)</div>
          <div className="text-xl font-bold text-indigo-300">{summary.direct_dependent_count}</div>
          {summary.direct_dependents?.length > 0 && (
            <div className="text-[11px] text-gray-400 font-mono mt-1 space-y-0.5">
              {summary.direct_dependents.map((d, i) => (
                <div key={i} className="truncate">• {d}</div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-gray-900 border border-gray-700/60 rounded p-3">
          <div className="text-gray-400 mb-1">Transitive Dependents (Depth &gt; 1)</div>
          <div className="text-xl font-bold text-purple-300">{summary.transitive_dependent_count}</div>
          {summary.transitive_dependents?.length > 0 && (
            <div className="text-[11px] text-gray-400 font-mono mt-1 space-y-0.5">
              {summary.transitive_dependents.map((d, i) => (
                <div key={i} className="truncate">• {d}</div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
