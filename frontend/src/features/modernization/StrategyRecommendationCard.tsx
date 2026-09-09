import React from 'react'
import type { ModernizationStrategy } from '../../services/api'
import { Award, AlertOctagon } from 'lucide-react'

interface StrategyRecommendationCardProps {
  strategy: ModernizationStrategy
}

export const StrategyRecommendationCard: React.FC<StrategyRecommendationCardProps> = ({ strategy }) => {
  const getStrategyBadgeColor = (strat: string) => {
    switch (strat) {
      case 'MODULARIZE':
        return 'bg-indigo-900/60 text-indigo-200 border-indigo-500/50'
      case 'EXTRACT_SERVICE':
        return 'bg-purple-900/60 text-purple-200 border-purple-500/50'
      case 'STRANGLER':
        return 'bg-amber-900/60 text-amber-200 border-amber-500/50'
      case 'REFACTOR_IN_PLACE':
        return 'bg-blue-900/60 text-blue-200 border-blue-500/50'
      case 'NO_MODERNIZATION_NEEDED':
        return 'bg-emerald-900/60 text-emerald-200 border-emerald-500/50'
      default:
        return 'bg-gray-800 text-gray-200 border-gray-600'
    }
  }

  return (
    <div className="bg-gray-800 rounded-lg p-5 border border-indigo-500/40 space-y-4 shadow-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Award className="w-6 h-6 text-indigo-400" />
          <div>
            <div className="text-xs font-medium text-gray-400">RECOMMENDED STRATEGY</div>
            <h3 className="text-xl font-bold text-white">{strategy.recommended_strategy}</h3>
          </div>
        </div>
        <span
          className={`px-3 py-1 text-xs font-mono font-bold rounded border ${getStrategyBadgeColor(
            strategy.recommended_strategy
          )}`}
        >
          {strategy.status === 'OVERRIDDEN' ? `OVERRIDDEN: ${strategy.user_override_strategy}` : strategy.recommended_strategy}
        </span>
      </div>

      {/* Rationale */}
      <div className="bg-gray-900/80 border border-gray-700/60 rounded p-4 text-xs text-gray-200 space-y-1">
        <div className="font-semibold text-indigo-300">Strategy Rationale:</div>
        <p className="leading-relaxed">{strategy.why_recommended}</p>
      </div>

      {/* What NOT to Change Yet */}
      {strategy.what_not_to_change && (
        <div className="bg-amber-950/30 border border-amber-700/40 rounded p-3 text-xs text-amber-200 flex items-start gap-2.5">
          <AlertOctagon className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-amber-300">Preservation Boundary (What NOT to change yet): </span>
            {strategy.what_not_to_change}
          </div>
        </div>
      )}

      {/* Decision Trace Timeline */}
      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">
          Evidence Decision Trace
        </h4>
        <div className="space-y-2">
          {strategy.decision_trace?.map((step) => (
            <div key={step.step} className="bg-gray-900 border border-gray-700/50 rounded p-2.5 text-xs flex items-start gap-3">
              <span className="w-5 h-5 rounded-full bg-indigo-900 text-indigo-200 flex items-center justify-center font-bold text-[10px] flex-shrink-0">
                {step.step}
              </span>
              <div>
                <span className="font-semibold text-indigo-300">{step.label}: </span>
                <span className="text-gray-300">{step.detail}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
