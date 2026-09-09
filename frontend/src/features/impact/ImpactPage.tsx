import React, { useState, useEffect } from 'react'
import { api } from '../../services/api'
import type {
  ImpactAnalysisResponse,
  ImpactExplainResponse,
  AffectedComponent,
  AffectedRule,
} from '../../services/api'
import { ImpactTargetSelector } from './ImpactTargetSelector'
import { ImpactSummaryCards } from './ImpactSummaryCards'
import { ImpactPathViewer } from './ImpactPathViewer'
import { SourceEvidenceViewer } from '../analysis/SourceEvidenceViewer'
import { Sparkles, Box, ShieldAlert, ArrowUpRight, AlertTriangle } from 'lucide-react'

interface ImpactPageProps {
  repositoryId: string
  analysisRunId?: string
}

export const ImpactPage: React.FC<ImpactPageProps> = ({ repositoryId, analysisRunId }) => {
  const [analysisId, setAnalysisId] = useState<string | undefined>(analysisRunId)
  const [loading, setLoading] = useState<boolean>(true)
  const [analyzingImpact, setAnalyzingImpact] = useState<boolean>(false)

  // Options for Selector
  const [availableEntities, setAvailableEntities] = useState<Array<{ id: string; name: string; fully_qualified_name: string }>>([])
  const [availableRules, setAvailableRules] = useState<Array<{ id: string; title: string }>>([])

  // Selection state
  const [targetType, setTargetType] = useState<string>('class')
  const [targetId, setTargetId] = useState<string>('')
  const [direction, setDirection] = useState<'forward' | 'reverse'>('forward')
  const [maxDepth, setMaxDepth] = useState<number>(3)

  // Results state
  const [impactResult, setImpactResult] = useState<ImpactAnalysisResponse | null>(null)
  const [explanation, setExplanation] = useState<ImpactExplainResponse | null>(null)
  const [explaining, setExplaining] = useState<boolean>(false)

  // Selected Evidence State
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
      loadSelectorOptions(analysisId)
    }
  }, [analysisId])

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

  const loadSelectorOptions = async (activeAnalysisId: string) => {
    try {
      const graph = await api.analysis.getGraph(activeAnalysisId)
      const entities = (graph.nodes || []).map((n: any) => ({
        id: n.id,
        name: n.name,
        fully_qualified_name: n.fully_qualified_name,
      }))
      setAvailableEntities(entities)

      const rules = await api.businessRules.list(activeAnalysisId)
      const ruleOptions = (rules || []).map((r) => ({
        id: r.id,
        title: r.title,
      }))
      setAvailableRules(ruleOptions)

      // Set default target if available
      if (entities.length > 0 && !targetId) {
        setTargetId(entities[0].id)
      }
    } catch (err) {
      console.error('Failed to load options for impact selector', err)
    }
  }

  const handleRunImpact = async () => {
    if (!analysisId || !targetId) return
    setAnalyzingImpact(true)
    setExplanation(null)
    try {
      const res = await api.impact.analyze(analysisId, targetType, targetId, direction, maxDepth)
      setImpactResult(res)
    } catch (err) {
      console.error('Impact analysis failed', err)
    } finally {
      setAnalyzingImpact(false)
    }
  }

  const handleExplainImpact = async () => {
    if (!analysisId || !targetId) return
    setExplaining(true)
    try {
      const res = await api.impact.explain(analysisId, targetType, targetId, direction, maxDepth)
      setExplanation(res)
    } catch (err) {
      console.error('Impact explanation failed', err)
    } finally {
      setExplaining(false)
    }
  }

  const openSourceModal = (filePath: string, line: number, construct = 'CLASS', reason = 'Impact path node') => {
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
        Loading Phase 5 Impact Analysis...
      </div>
    )
  }

  if (!analysisId) {
    return (
      <div className="p-8 text-center bg-gray-800 rounded-lg border border-gray-700 m-6">
        <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto mb-3" />
        <h3 className="text-lg font-medium text-white mb-1">No Completed Analysis Found</h3>
        <p className="text-sm text-gray-400">
          Run System X-Ray (Phase 3) analysis before performing Impact Analysis.
        </p>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex items-center justify-between border-b border-gray-700 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Box className="w-7 h-7 text-indigo-400" />
            Phase 5 — Deterministic Impact Analysis
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Traverse dependency paths and business rule associations with 100% evidence-backed static graph analysis.
          </p>
        </div>
      </div>

      {/* Control Panel */}
      <ImpactTargetSelector
        targetType={targetType}
        setTargetType={setTargetType}
        targetId={targetId}
        setTargetId={setTargetId}
        direction={direction}
        setDirection={setDirection}
        maxDepth={maxDepth}
        setMaxDepth={setMaxDepth}
        availableEntities={availableEntities}
        availableRules={availableRules}
        onRunImpact={handleRunImpact}
        loading={analyzingImpact}
      />

      {/* Results View */}
      {impactResult && (
        <div className="space-y-6">
          {/* Summary Cards & Explicit NO EVIDENCED IMPACT State */}
          <ImpactSummaryCards
            summary={impactResult.summary}
            status={impactResult.status}
            hasEvidencedImpact={impactResult.has_evidenced_impact}
            targetName={impactResult.target.name}
          />

          {/* AI Gateway Explanation (Strict AI Boundary) */}
          <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-400" />
                AI Gateway Impact Narrative (Explanation Only)
              </h4>
              <button
                type="button"
                onClick={handleExplainImpact}
                disabled={explaining}
                className="px-3 py-1.5 bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold rounded shadow transition-colors flex items-center gap-1.5"
              >
                {explaining ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Generating Explanation...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    Explain Impact via AI Gateway
                  </>
                )}
              </button>
            </div>

            {explanation ? (
              <div className="bg-purple-950/30 border border-purple-800/40 rounded p-4 text-sm text-purple-200 leading-relaxed font-sans">
                {explanation.explanation}
              </div>
            ) : (
              <p className="text-xs text-gray-400 italic">
                Click above to generate a plain-language summary derived strictly from established deterministic impact paths.
              </p>
            )}
          </div>

          {/* Step-by-Step Traversal Paths */}
          <ImpactPathViewer
            paths={impactResult.impact_paths}
            onViewSource={openSourceModal}
          />

          {/* Affected Components Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Direct Components */}
            <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-3">
              <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                <Box className="w-4 h-4 text-indigo-400" />
                Direct Affected Components ({impactResult.direct_affected_components.length})
              </h4>
              {impactResult.direct_affected_components.length === 0 ? (
                <p className="text-xs text-gray-400 italic">No direct component impact.</p>
              ) : (
                <div className="space-y-2">
                  {impactResult.direct_affected_components.map((comp: AffectedComponent) => (
                    <div
                      key={comp.id}
                      className="bg-gray-900 border border-gray-700/60 rounded p-3 text-xs flex items-center justify-between"
                    >
                      <div>
                        <div className="font-semibold text-white">{comp.name}</div>
                        <div className="text-gray-400 font-mono text-[11px]">{comp.fully_qualified_name}</div>
                        <span className="inline-block mt-1 text-[10px] px-1.5 py-0.5 bg-indigo-900/60 text-indigo-300 rounded font-mono">
                          {comp.component_type}
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={() => openSourceModal(comp.relative_file_path, comp.line_start)}
                        className="text-gray-400 hover:text-white p-1"
                        title="View Source Evidence"
                      >
                        <ArrowUpRight className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Transitive Components */}
            <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-3">
              <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                <Box className="w-4 h-4 text-purple-400" />
                Transitive Affected Components ({impactResult.transitive_affected_components.length})
              </h4>
              {impactResult.transitive_affected_components.length === 0 ? (
                <p className="text-xs text-gray-400 italic">No transitive component impact.</p>
              ) : (
                <div className="space-y-2 max-h-72 overflow-y-auto">
                  {impactResult.transitive_affected_components.map((comp: AffectedComponent) => (
                    <div
                      key={comp.id}
                      className="bg-gray-900 border border-gray-700/60 rounded p-3 text-xs flex items-center justify-between"
                    >
                      <div>
                        <div className="font-semibold text-white">{comp.name}</div>
                        <div className="text-gray-400 font-mono text-[11px]">{comp.fully_qualified_name}</div>
                        <span className="inline-block mt-1 text-[10px] px-1.5 py-0.5 bg-purple-900/60 text-purple-300 rounded font-mono">
                          Depth {comp.depth}
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={() => openSourceModal(comp.relative_file_path, comp.line_start)}
                        className="text-gray-400 hover:text-white p-1"
                        title="View Source Evidence"
                      >
                        <ArrowUpRight className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Affected Business Rules Section */}
          <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-3">
            <h4 className="text-sm font-semibold text-white flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              Impacted Business Rules ({impactResult.direct_affected_rules.length + impactResult.transitive_affected_rules.length})
            </h4>

            {impactResult.direct_affected_rules.length === 0 && impactResult.transitive_affected_rules.length === 0 ? (
              <p className="text-xs text-gray-400 italic">No business rules associated with affected paths.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[...impactResult.direct_affected_rules, ...impactResult.transitive_affected_rules].map(
                  (rule: AffectedRule) => (
                    <div key={rule.id} className="bg-gray-900 border border-gray-700/60 rounded p-3 space-y-2 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-amber-200">{rule.title}</span>
                        <span className="px-2 py-0.5 bg-amber-900/40 text-amber-300 rounded font-mono text-[10px]">
                          {rule.rule_type}
                        </span>
                      </div>
                      <p className="text-gray-400 text-[11px] line-clamp-2">{rule.extraction_reason}</p>
                      <div className="flex items-center justify-between pt-1 border-t border-gray-800 font-mono text-[10px] text-gray-400">
                        <span>{rule.relative_file_path}:{rule.line_start}</span>
                        <button
                          type="button"
                          onClick={() => openSourceModal(rule.relative_file_path, rule.line_start)}
                          className="text-indigo-400 hover:underline"
                        >
                          Inspect Source
                        </button>
                      </div>
                    </div>
                  )
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Selected Source Evidence Card */}
      {selectedEvidence && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-gray-400 font-semibold uppercase">
            <span>Deterministic Evidence Inspection</span>
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

