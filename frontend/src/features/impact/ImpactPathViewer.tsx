import React from 'react'
import type { ImpactPathStep } from '../../services/api'
import { FileCode, ArrowRight, CornerDownRight } from 'lucide-react'

interface ImpactPathViewerProps {
  paths: ImpactPathStep[]
  onViewSource?: (filePath: string, line: number) => void
}

export const ImpactPathViewer: React.FC<ImpactPathViewerProps> = ({ paths, onViewSource }) => {
  if (paths.length === 0) {
    return null
  }

  return (
    <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-3">
      <h4 className="text-sm font-semibold text-white flex items-center gap-2">
        <CornerDownRight className="w-4 h-4 text-indigo-400" />
        Deterministic Impact Traversal Paths ({paths.length})
      </h4>

      <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
        {paths.map((p, idx) => (
          <div
            key={idx}
            className="bg-gray-900 border border-gray-700/60 rounded p-3 text-xs space-y-1.5 hover:border-gray-600 transition-colors"
          >
            <div className="flex items-center justify-between font-mono">
              <div className="flex items-center gap-2 text-gray-200">
                <span className="font-semibold text-indigo-300">{p.from_component}</span>
                <span className="px-1.5 py-0.5 bg-gray-800 text-gray-400 text-[10px] rounded border border-gray-700">
                  {p.relationship_type}
                </span>
                <ArrowRight className="w-3 h-3 text-gray-500" />
                <span className="font-semibold text-purple-300">{p.to_component}</span>
              </div>
              <span className="text-[10px] px-2 py-0.5 bg-gray-800 text-gray-400 rounded">
                Depth {p.depth}
              </span>
            </div>

            <div className="flex items-center justify-between text-gray-400 pt-1 border-t border-gray-800">
              <span className="italic">{p.evidence_reason || 'Static code relationship'}</span>

              {p.file_path && (
                <button
                  type="button"
                  onClick={() => onViewSource?.(p.file_path, p.line_number)}
                  className="flex items-center gap-1 text-indigo-400 hover:text-indigo-300 font-mono text-[11px]"
                >
                  <FileCode className="w-3 h-3" />
                  {p.file_path.split('/').pop()}:{p.line_number}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
