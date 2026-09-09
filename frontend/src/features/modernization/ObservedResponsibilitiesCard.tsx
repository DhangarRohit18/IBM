import React from 'react'
import type { ResponsibilityItem } from '../../services/api'
import { Activity, FileCode } from 'lucide-react'

interface ObservedResponsibilitiesCardProps {
  responsibilities: ResponsibilityItem[]
  onViewSource?: (filePath: string, line: number, category: string, snippet: string) => void
}

export const ObservedResponsibilitiesCard: React.FC<ObservedResponsibilitiesCardProps> = ({
  responsibilities,
  onViewSource,
}) => {
  return (
    <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-white flex items-center gap-2">
          <Activity className="w-4 h-4 text-indigo-400" />
          Observed Responsibilities ({responsibilities.length})
        </h4>
        <span className="text-[11px] text-gray-400 font-mono">AST Signal Analysis</span>
      </div>

      {responsibilities.length === 0 ? (
        <p className="text-xs text-gray-400 italic">No complex responsibilities observed. Component exhibits single responsibility focus.</p>
      ) : (
        <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
          {responsibilities.map((r, idx) => (
            <div
              key={idx}
              className="bg-gray-900 border border-gray-700/60 rounded p-3 text-xs space-y-1.5 hover:border-gray-600 transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-indigo-300">{r.title}</span>
                <span className="px-2 py-0.5 bg-indigo-900/50 text-indigo-300 rounded font-mono text-[10px]">
                  {r.category}
                </span>
              </div>

              <p className="text-gray-300 text-[11px]">{r.description}</p>

              {r.source_snippet && (
                <div className="bg-gray-950 p-2 rounded border border-gray-800 font-mono text-[11px] text-gray-400 overflow-x-auto">
                  <code>{r.source_snippet}</code>
                </div>
              )}

              <div className="flex items-center justify-between text-gray-400 pt-1 border-t border-gray-800 font-mono text-[10px]">
                <span>{r.evidence_reason}</span>
                {r.relative_file_path && (
                  <button
                    type="button"
                    onClick={() => onViewSource?.(r.relative_file_path, r.line_number, r.category, r.source_snippet)}
                    className="flex items-center gap-1 text-indigo-400 hover:underline"
                  >
                    <FileCode className="w-3 h-3" />
                    Line {r.line_number}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
