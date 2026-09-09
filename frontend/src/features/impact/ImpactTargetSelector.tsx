import React from 'react'
import { ArrowRightLeft, ArrowRight, Layers, Sliders, Target } from 'lucide-react'

interface ImpactTargetSelectorProps {
  targetType: string
  setTargetType: (val: string) => void
  targetId: string
  setTargetId: (val: string) => void
  direction: 'forward' | 'reverse'
  setDirection: (val: 'forward' | 'reverse') => void
  maxDepth: number
  setMaxDepth: (val: number) => void
  availableEntities: Array<{ id: string; name: string; fully_qualified_name: string }>
  availableRules: Array<{ id: string; title: string }>
  onRunImpact: () => void
  loading: boolean
}

export const ImpactTargetSelector: React.FC<ImpactTargetSelectorProps> = ({
  targetType,
  setTargetType,
  targetId,
  setTargetId,
  direction,
  setDirection,
  maxDepth,
  setMaxDepth,
  availableEntities,
  availableRules,
  onRunImpact,
  loading,
}) => {
  return (
    <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Target className="w-5 h-5 text-indigo-400" />
          Impact Analysis Control Panel
        </h3>
        <span className="text-xs px-2.5 py-1 bg-indigo-900/50 text-indigo-300 border border-indigo-700/50 rounded-full font-mono">
          Phase 5 Engine
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* 1. Target Type */}
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5 flex items-center gap-1">
            <Layers className="w-3.5 h-3.5 text-gray-400" />
            Target Category
          </label>
          <select
            value={targetType}
            onChange={(e) => {
              setTargetType(e.target.value)
              setTargetId('')
            }}
            className="w-full bg-gray-900 border border-gray-700 rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="class">Class / Interface</option>
            <option value="business_rule">Business Rule</option>
          </select>
        </div>

        {/* 2. Target Selection */}
        <div className="md:col-span-2">
          <label className="block text-xs font-medium text-gray-400 mb-1.5">
            Select Target Component / Rule
          </label>
          {targetType === 'business_rule' ? (
            <select
              value={targetId}
              onChange={(e) => setTargetId(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">-- Select Business Rule --</option>
              {availableRules.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.title}
                </option>
              ))}
            </select>
          ) : (
            <select
              value={targetId}
              onChange={(e) => setTargetId(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-xs"
            >
              <option value="">-- Select Code Entity --</option>
              {availableEntities.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name} ({e.fully_qualified_name})
                </option>
              ))}
            </select>
          )}
        </div>

        {/* 3. Traversal Depth */}
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5 flex items-center justify-between">
            <span className="flex items-center gap-1">
              <Sliders className="w-3.5 h-3.5 text-gray-400" />
              Max Depth: {maxDepth}
            </span>
          </label>
          <input
            type="range"
            min={1}
            max={5}
            value={maxDepth}
            onChange={(e) => setMaxDepth(parseInt(e.target.value, 10))}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-indigo-500 mt-2"
          />
        </div>
      </div>

      {/* Traversal Direction Toggle */}
      <div className="pt-2 border-t border-gray-700/60 flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <span className="text-xs font-medium text-gray-400">Traversal Direction:</span>
          <div className="inline-flex rounded-md shadow-sm bg-gray-900 p-1 border border-gray-700">
            <button
              type="button"
              onClick={() => setDirection('forward')}
              className={`px-3 py-1.5 rounded text-xs font-medium flex items-center gap-1.5 transition-colors ${
                direction === 'forward'
                  ? 'bg-indigo-600 text-white shadow'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <ArrowRight className="w-3.5 h-3.5" />
              Forward (Dependencies)
            </button>
            <button
              type="button"
              onClick={() => setDirection('reverse')}
              className={`px-3 py-1.5 rounded text-xs font-medium flex items-center gap-1.5 transition-colors ${
                direction === 'reverse'
                  ? 'bg-purple-600 text-white shadow'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <ArrowRightLeft className="w-3.5 h-3.5" />
              Reverse (Dependents)
            </button>
          </div>
        </div>

        <button
          type="button"
          onClick={onRunImpact}
          disabled={!targetId || loading}
          className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-700 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-md shadow transition-colors flex items-center gap-2"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Analyzing Graph...
            </>
          ) : (
            <>
              <Target className="w-4 h-4" />
              Compute Impact Analysis
            </>
          )}
        </button>
      </div>
    </div>
  )
}
