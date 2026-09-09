import React from 'react'
import { Compass, Filter, RefreshCw, Search } from 'lucide-react'

interface ModernizationCandidateSelectorProps {
  candidates: Array<{ id: string; entity_name: string; recommended_strategy: string; status: string }>
  selectedId: string
  setSelectedId: (id: string) => void
  strategyFilter: string
  setStrategyFilter: (val: string) => void
  searchQuery: string
  setSearchQuery: (val: string) => void
  onEvaluate: () => void
  evaluating: boolean
}

export const ModernizationCandidateSelector: React.FC<ModernizationCandidateSelectorProps> = ({
  candidates,
  selectedId,
  setSelectedId,
  strategyFilter,
  setStrategyFilter,
  searchQuery,
  setSearchQuery,
  onEvaluate,
  evaluating,
}) => {
  return (
    <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Compass className="w-5 h-5 text-indigo-400" />
          Modernization Strategy Candidates ({candidates.length})
        </h3>
        <button
          type="button"
          onClick={onEvaluate}
          disabled={evaluating}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-700 text-white text-xs font-semibold rounded shadow transition-colors flex items-center gap-2"
        >
          {evaluating ? (
            <>
              <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Evaluating Strategies...
            </>
          ) : (
            <>
              <RefreshCw className="w-3.5 h-3.5" />
              Re-Evaluate All Candidates
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Component Selector */}
        <div className="md:col-span-2">
          <label className="block text-xs font-medium text-gray-400 mb-1">
            Select Target Component
          </label>
          <select
            value={selectedId}
            onChange={(e) => setSelectedId(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-xs"
          >
            <option value="">-- Select Candidate Component --</option>
            {candidates.map((c) => (
              <option key={c.id} value={c.id}>
                {c.entity_name} [{c.recommended_strategy}] ({c.status})
              </option>
            ))}
          </select>
        </div>

        {/* Search Query Input */}
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1 flex items-center gap-1">
            <Search className="w-3.5 h-3.5 text-gray-400" />
            Search Component
          </label>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search component name..."
            className="w-full bg-gray-900 border border-gray-700 rounded-md px-3 py-2 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {/* Strategy Filter */}
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5 text-gray-400" />
            Filter Strategy
          </label>
          <select
            value={strategyFilter}
            onChange={(e) => setStrategyFilter(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded-md px-3 py-2 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Strategies</option>
            <option value="MODULARIZE">MODULARIZE</option>
            <option value="EXTRACT_SERVICE">EXTRACT_SERVICE</option>
            <option value="STRANGLER">STRANGLER</option>
            <option value="REFACTOR_IN_PLACE">REFACTOR_IN_PLACE</option>
            <option value="RETAIN_AND_WRAP">RETAIN_AND_WRAP</option>
            <option value="NO_MODERNIZATION_NEEDED">NO_MODERNIZATION_NEEDED</option>
          </select>
        </div>
      </div>
    </div>
  )
}
