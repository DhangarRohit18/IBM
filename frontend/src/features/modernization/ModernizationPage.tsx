import React, { useState, useEffect } from 'react'
import { api } from '../../services/api'
import type { ModernizationStrategy, StrategyExplainResponse } from '../../services/api'
import { ModernizationCandidateSelector } from './ModernizationCandidateSelector'
import { StrategyRecommendationCard } from './StrategyRecommendationCard'
import { StrategyAlternativeCard } from './StrategyAlternativeCard'
import { ObservedResponsibilitiesCard } from './ObservedResponsibilitiesCard'
import { BusinessRulesPreservationCard } from './BusinessRulesPreservationCard'
import { ImpactSurfaceCard } from './ImpactSurfaceCard'
import { HumanOverrideModal } from './HumanOverrideModal'
import { SourceEvidenceViewer } from '../analysis/SourceEvidenceViewer'
import { Compass, Sparkles, UserCheck, AlertTriangle } from 'lucide-react'

interface ModernizationPageProps {
  repositoryId: string
  analysisRunId?: string
}

export const ModernizationPage: React.FC<ModernizationPageProps> = ({ repositoryId, analysisRunId }) => {
  const [analysisId, setAnalysisId] = useState<string | undefined>(analysisRunId)
  const [loading, setLoading] = useState<boolean>(true)
  const [evaluating, setEvaluating] = useState<boolean>(false)

  // Candidate Strategies
  const [strategies, setStrategies] = useState<ModernizationStrategy[]>([])
  const [selectedId, setSelectedId] = useState<string>('')
  const [strategyFilter, setStrategyFilter] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState<string>('')

  // Active Selected Detail Strategy
  const [selectedStrategy, setSelectedStrategy] = useState<ModernizationStrategy | null>(null)

  // AI Explanation State
  const [explanation, setExplanation] = useState<StrategyExplainResponse | null>(null)
  const [explaining, setExplaining] = useState<boolean>(false)

  // Human Override Modal State
  const [overrideModalOpen, setOverrideModalOpen] = useState<boolean>(false)

  // Source Evidence State
  const [selectedEvidence, setSelectedEvidence] = useState<{
    filePath: string
    line: number
    construct: string
    reason: string
  } | null>(null)

  useEffect(() => {
    loadAnalysisRun()
  }, [repositoryId, analysisRunId])

  useEffect(() => {
    if (analysisId) {
      fetchStrategies()
    }
  }, [analysisId, strategyFilter, searchQuery])

  useEffect(() => {
    if (selectedId) {
      const match = strategies.find((s) => s.id === selectedId)
      if (match) {
        setSelectedStrategy(match)
        setExplanation(null)
      }
    } else if (strategies.length > 0) {
      setSelectedId(strategies[0].id)
    }
  }, [selectedId, strategies])

  const loadAnalysisRun = async () => {
    setLoading(true)
    try {
      let activeAnalysisId = analysisRunId
      if (!activeAnalysisId) {
        const runs = await api.analysis.listRuns(repositoryId)
        const completed = runs.find((r) => r.status === 'COMPLETED')
        if (completed) {
          activeAnalysisId = completed.id
        }
      }
      setAnalysisId(activeAnalysisId)
    } catch (err) {
      console.error('Failed to load analysis run', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchStrategies = async () => {
    if (!analysisId) return
    try {
      let data = await api.modernization.list(analysisId, strategyFilter || undefined, undefined, searchQuery || undefined)
      if (data.length === 0) {
        // Auto trigger evaluation if none exist
        data = await api.modernization.evaluate(analysisId)
      }
      setStrategies(data)
      if (data.length > 0 && !selectedId) {
        setSelectedId(data[0].id)
      }
    } catch (err) {
      console.error('Failed to fetch modernization strategies', err)
    }
  }

  const handleRunEvaluation = async () => {
    if (!analysisId) return
    setEvaluating(true)
    try {
      const data = await api.modernization.evaluate(analysisId)
      setStrategies(data)
      if (data.length > 0) {
        setSelectedId(data[0].id)
      }
    } catch (err) {
      console.error('Modernization evaluation failed', err)
    } finally {
      setEvaluating(false)
    }
  }

  const handleExplainStrategy = async () => {
    if (!selectedStrategy) return
    setExplaining(true)
    try {
      const res = await api.modernization.explain(selectedStrategy.id)
      setExplanation(res)
    } catch (err) {
      console.error('Strategy explanation failed', err)
    } finally {
      setExplaining(false)
    }
  }

  const handleSaveOverride = async (status: 'REVIEWED' | 'OVERRIDDEN', overrideStrategy?: string, notes?: string) => {
    if (!selectedStrategy) return
    try {
      const updated = await api.modernization.override(selectedStrategy.id, status, overrideStrategy, notes)
      setSelectedStrategy(updated)
      setStrategies((prev) => prev.map((s) => (s.id === updated.id ? updated : s)))
    } catch (err) {
      console.error('Failed to record human review action', err)
    }
  }

  const openSourceModal = (filePath: string, line: number, construct = 'CLASS', reason = 'Responsibility AST signal') => {
    setSelectedEvidence({
      filePath,
      line,
      construct,
      reason,
    })
  }

  if (loading) {
    return (
      <div className="p-8 text-center text-gray-400 flex items-center justify-center gap-2">
        <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        Loading Phase 6 Modernization Strategy Engine...
      </div>
    )
  }

  if (!analysisId) {
    return (
      <div className="p-8 text-center bg-gray-800 rounded-lg border border-gray-700 m-6">
        <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto mb-3" />
        <h3 className="text-lg font-medium text-white mb-1">No Completed Analysis Found</h3>
        <p className="text-sm text-gray-400">
          Run System X-Ray (Phase 3) analysis before generating Modernization Strategies.
        </p>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-700 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Compass className="w-7 h-7 text-indigo-400" />
            Phase 6 — Evidence-Backed Modernization Strategy Engine
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Recommends component modernization approaches backed strictly by System X-Ray, Business Rules, Impact Analysis, and AST signals.
          </p>
        </div>
      </div>

      {/* Candidate Selector */}
      <ModernizationCandidateSelector
        candidates={strategies.map((s) => ({
          id: s.id,
          entity_name: s.entity_name,
          recommended_strategy: s.recommended_strategy,
          status: s.status,
        }))}
        selectedId={selectedId}
        setSelectedId={setSelectedId}
        strategyFilter={strategyFilter}
        setStrategyFilter={setStrategyFilter}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onEvaluate={handleRunEvaluation}
        evaluating={evaluating}
      />

      {/* Selected Component Strategy Workspace */}
      {selectedStrategy && (
        <div className="space-y-6">
          {/* Action Bar */}
          <div className="flex items-center justify-between bg-gray-800 p-4 rounded-lg border border-gray-700">
            <div>
              <span className="text-xs font-mono text-gray-400">TARGET COMPONENT:</span>
              <h3 className="text-lg font-bold text-white">{selectedStrategy.entity_name}</h3>
              <p className="text-xs text-gray-400 font-mono">{selectedStrategy.relative_file_path}</p>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setOverrideModalOpen(true)}
                className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded shadow transition-colors flex items-center gap-1.5"
              >
                <UserCheck className="w-4 h-4" />
                Audit / Override Strategy
              </button>
            </div>
          </div>

          {/* Top Row: Recommended Strategy & Alternative Strategy */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <StrategyRecommendationCard strategy={selectedStrategy} />
            <StrategyAlternativeCard strategy={selectedStrategy} />
          </div>

          {/* AI Gateway Narrative Section */}
          <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-400" />
                AI Gateway Strategy Narrative (Explanation Only)
              </h4>
              <button
                type="button"
                onClick={handleExplainStrategy}
                disabled={explaining}
                className="px-3 py-1.5 bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold rounded shadow transition-colors flex items-center gap-1.5"
              >
                {explaining ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Generating Rationale...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    Explain Strategy via AI Gateway
                  </>
                )}
              </button>
            </div>

            {explanation || selectedStrategy.ai_explanation ? (
              <div className="bg-purple-950/30 border border-purple-800/40 rounded p-4 text-sm text-purple-200 leading-relaxed">
                {explanation?.explanation || selectedStrategy.ai_explanation}
              </div>
            ) : (
              <p className="text-xs text-gray-400 italic">
                Click above to generate an executive plain-language rationale explaining the established decision trace.
              </p>
            )}
          </div>

          {/* Middle Row: AST Responsibilities & Preserved Business Rules */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ObservedResponsibilitiesCard
              responsibilities={selectedStrategy.observed_responsibilities || []}
              onViewSource={openSourceModal}
            />
            <BusinessRulesPreservationCard
              rules={selectedStrategy.rules_to_preserve || []}
            />
          </div>

          {/* Bottom Row: Known Impact Surface */}
          <ImpactSurfaceCard
            summary={selectedStrategy.impact_summary || { direct_dependent_count: 0, transitive_dependent_count: 0, direct_dependents: [], transitive_dependents: [] }}
          />
        </div>
      )}

      {/* Human Override Audit Modal */}
      {selectedStrategy && (
        <HumanOverrideModal
          isOpen={overrideModalOpen}
          onClose={() => setOverrideModalOpen(false)}
          currentStrategy={selectedStrategy.recommended_strategy}
          onSaveOverride={handleSaveOverride}
        />
      )}

      {/* Selected Source Evidence Inspection */}
      {selectedEvidence && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-gray-400 font-semibold uppercase">
            <span>Deterministic Source Evidence Inspection</span>
            <button
              onClick={() => setSelectedEvidence(null)}
              className="text-gray-400 hover:text-white text-xs underline"
            >
              Close Panel
            </button>
          </div>
          <SourceEvidenceViewer
            relativeFilePath={selectedEvidence.filePath}
            lineNumber={selectedEvidence.line}
            sourceConstruct={selectedEvidence.construct}
            evidenceReason={selectedEvidence.reason}
            isResolved={true}
          />
        </div>
      )}
    </div>
  )
}
