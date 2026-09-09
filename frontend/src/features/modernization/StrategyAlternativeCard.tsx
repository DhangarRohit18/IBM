import React from 'react'
import type { ModernizationStrategy } from '../../services/api'
import { ArrowRightLeft, Layers } from 'lucide-react'

interface StrategyAlternativeCardProps {
  strategy: ModernizationStrategy
}

export const StrategyAlternativeCard: React.FC<StrategyAlternativeCardProps> = ({ strategy }) => {
  if (!strategy.alternative_strategy) {
    return null
  }

  return (
    <div className="bg-gray-800 rounded-lg p-5 border border-purple-500/30 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <ArrowRightLeft className="w-5 h-5 text-purple-400" />
          <div>
            <div className="text-xs font-medium text-gray-400">ALTERNATIVE STRATEGY CONSIDERATION</div>
            <h3 className="text-lg font-bold text-purple-300">{strategy.alternative_strategy}</h3>
          </div>
        </div>
      </div>

      {strategy.why_alternative && (
        <p className="text-xs text-gray-300 bg-gray-900 border border-gray-700/50 rounded p-3 leading-relaxed">
          {strategy.why_alternative}
        </p>
      )}

      {/* Qualitative Comparison Table (Zero Fake Scores) */}
      {strategy.qualitative_comparison?.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-purple-400" />
            Qualitative Strategy Comparison (Observable Facts)
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left border border-gray-700">
              <thead className="bg-gray-900 text-gray-400 text-[11px] uppercase font-mono border-b border-gray-700">
                <tr>
                  <th className="px-3 py-2">Dimension</th>
                  <th className="px-3 py-2 text-indigo-300">{strategy.recommended_strategy} (Recommended)</th>
                  <th className="px-3 py-2 text-purple-300">{strategy.alternative_strategy} (Alternative)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800 text-gray-300">
                {strategy.qualitative_comparison.map((row, i) => (
                  <tr key={i} className="hover:bg-gray-900/50">
                    <td className="px-3 py-2 font-semibold text-gray-400">{row.dimension}</td>
                    <td className="px-3 py-2">{row.recommended_value}</td>
                    <td className="px-3 py-2">{row.alternative_value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
