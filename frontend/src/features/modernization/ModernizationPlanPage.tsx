import React, { useState, useEffect } from 'react'
import { api } from '../../services/api'
import type { ModernizationPlan, ModernizationTask, PlanExplainResponse } from '../../services/api'
import { Sparkles, CheckCircle2, AlertTriangle, ArrowUp, ArrowDown, ShieldCheck, GitBranch, ListChecks, Play } from 'lucide-react'

interface ModernizationPlanPageProps {
  repositoryId: string
  analysisRunId?: string
}

export const ModernizationPlanPage: React.FC<ModernizationPlanPageProps> = ({ repositoryId, analysisRunId }) => {
  const [analysisId, setAnalysisId] = useState<string | undefined>(analysisRunId)
  const [loading, setLoading] = useState<boolean>(true)
  const [generating, setGenerating] = useState<boolean>(false)

  const [plans, setPlans] = useState<ModernizationPlan[]>([])
  const [selectedPlanId, setSelectedPlanId] = useState<string>('')
  const [activePlan, setActivePlan] = useState<ModernizationPlan | null>(null)

  // AI Explanation State
  const [explanation, setExplanation] = useState<PlanExplainResponse | null>(null)
  const [explaining, setExplaining] = useState<boolean>(false)

  // Review Modal State
  const [reviewModalOpen, setReviewModalOpen] = useState<boolean>(false)
  const [reviewStatus, setReviewStatus] = useState<'REVIEWED' | 'APPROVED' | 'REJECTED'>('APPROVED')
  const [reviewNotes, setReviewNotes] = useState<string>('')

  useEffect(() => {
    loadAnalysisRun()
  }, [repositoryId, analysisRunId])

  useEffect(() => {
    if (analysisId) {
      fetchPlans()
    }
  }, [analysisId])

  useEffect(() => {
    if (selectedPlanId) {
      const match = plans.find((p) => p.id === selectedPlanId)
      if (match) {
        setActivePlan(match)
        setExplanation(null)
      }
    } else if (plans.length > 0) {
      setSelectedPlanId(plans[0].id)
    }
  }, [selectedPlanId, plans])

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

  const fetchPlans = async () => {
    if (!analysisId) return
    try {
      let data = await api.modernization.listPlans(analysisId)
      if (data.length === 0) {
        data = await api.modernization.generatePlans(analysisId)
      }
      setPlans(data)
      if (data.length > 0 && !selectedPlanId) {
        setSelectedPlanId(data[0].id)
      }
    } catch (err) {
      console.error('Failed to fetch modernization plans', err)
    }
  }

  const handleGeneratePlans = async () => {
    if (!analysisId) return
    setGenerating(true)
    try {
      const data = await api.modernization.generatePlans(analysisId)
      setPlans(data)
      if (data.length > 0) {
        setSelectedPlanId(data[0].id)
      }
    } catch (err) {
      console.error('Plan generation failed', err)
    } finally {
      setGenerating(false)
    }
  }

  const handleTaskStatusChange = async (taskId: string, newStatus: string) => {
    try {
      const updatedTask = await api.modernization.updateTaskStatus(taskId, newStatus)
      if (activePlan) {
        const updatedTasks = activePlan.tasks.map((t: ModernizationTask) => (t.id === taskId ? updatedTask : t))
        const updatedPlan = { ...activePlan, tasks: updatedTasks }
        setActivePlan(updatedPlan)
        setPlans((prev) => prev.map((p) => (p.id === updatedPlan.id ? updatedPlan : p)))
      }
    } catch (err) {
      console.error('Failed to update task status', err)
    }
  }

  const handleReorderTask = async (taskId: string, newSeq: number) => {
    try {
      const updatedTasks = await api.modernization.reorderTask(taskId, newSeq)
      if (activePlan) {
        const updatedPlan = { ...activePlan, tasks: updatedTasks }
        setActivePlan(updatedPlan)
        setPlans((prev) => prev.map((p) => (p.id === updatedPlan.id ? updatedPlan : p)))
      }
    } catch (err) {
      console.error('Failed to reorder task', err)
    }
  }

  const handleReviewPlan = async () => {
    if (!activePlan) return
    try {
      const updatedPlan = await api.modernization.reviewPlan(activePlan.id, reviewStatus, reviewNotes)
      setActivePlan(updatedPlan)
      setPlans((prev) => prev.map((p) => (p.id === updatedPlan.id ? updatedPlan : p)))
      setReviewModalOpen(false)
    } catch (err) {
      console.error('Failed to record plan review', err)
    }
  }

  const handleExplainPlan = async () => {
    if (!activePlan) return
    setExplaining(true)
    try {
      const res = await api.modernization.explainPlan(activePlan.id)
      setExplanation(res)
    } catch (err) {
      console.error('Plan explanation failed', err)
    } finally {
      setExplaining(false)
    }
  }

  if (loading) {
    return (
      <div className="p-8 text-center text-gray-400 flex items-center justify-center gap-2">
        <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        Loading Phase 7 Modernization Execution Plan...
      </div>
    )
  }

  if (!analysisId) {
    return (
      <div className="p-8 text-center bg-gray-800 rounded-lg border border-gray-700 m-6">
        <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto mb-3" />
        <h3 className="text-lg font-medium text-white mb-1">No Completed Analysis Found</h3>
        <p className="text-sm text-gray-400">
          Run System X-Ray and Modernization Strategy before generating execution plans.
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
            <ListChecks className="w-7 h-7 text-indigo-400" />
            Phase 7 — Actionable Modernization Execution Plan
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Bridges Phase 6 strategy recommendations to a deterministic, ordered execution sequence with business rule preservation and verification checkpoints.
          </p>
        </div>

        <button
          type="button"
          onClick={handleGeneratePlans}
          disabled={generating}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded shadow transition-colors flex items-center gap-2"
        >
          {generating ? (
            <>
              <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Generating Plans...
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5" />
              Re-Generate All Plans
            </>
          )}
        </button>
      </div>

      {/* Candidate Plan Selector Bar */}
      <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1 min-w-[280px]">
          <span className="text-xs font-semibold uppercase text-gray-400">Select Plan Target:</span>
          <select
            value={selectedPlanId}
            onChange={(e) => setSelectedPlanId(e.target.value)}
            className="bg-gray-900 border border-gray-700 rounded px-3 py-1.5 text-sm text-white focus:outline-none focus:border-indigo-500 flex-1"
          >
            {plans.map((p) => (
              <option key={p.id} value={p.id}>
                {p.entity_name} ({p.strategy_type}) — Status: {p.status}
              </option>
            ))}
          </select>
        </div>

        {activePlan && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400">Strategy:</span>
            <span className="px-2.5 py-1 bg-indigo-950 text-indigo-300 border border-indigo-700/50 rounded font-mono text-xs font-bold">
              {activePlan.strategy_type}
            </span>

            <span className="text-xs text-gray-400 ml-2">Plan Review:</span>
            <span
              className={`px-2.5 py-1 text-xs font-bold rounded border ${
                activePlan.status === 'APPROVED'
                  ? 'bg-emerald-950 text-emerald-300 border-emerald-700/50'
                  : activePlan.status === 'REVIEWED'
                  ? 'bg-blue-950 text-blue-300 border-blue-700/50'
                  : activePlan.status === 'REJECTED'
                  ? 'bg-red-950 text-red-300 border-red-700/50'
                  : 'bg-amber-950 text-amber-300 border-amber-700/50'
              }`}
            >
              {activePlan.status}
            </span>

            <button
              type="button"
              onClick={() => setReviewModalOpen(true)}
              className="ml-3 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white text-xs font-medium rounded border border-gray-600 transition-colors"
            >
              Review / Approve Plan
            </button>
          </div>
        )}
      </div>

      {activePlan && (
        <div className="space-y-6">
          {/* Overview & Summary Card */}
          <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-3">
            <h3 className="text-base font-bold text-white flex items-center justify-between">
              <span>Modernization Execution Plan Overview</span>
              <span className="text-xs font-mono text-gray-400 font-normal">
                {activePlan.tasks.length} Tasks | {activePlan.rules_to_preserve.length} Preserved Rules
              </span>
            </h3>
            <p className="text-sm text-gray-300 leading-relaxed bg-gray-900/60 p-3 rounded border border-gray-700/50 font-mono">
              {activePlan.summary}
            </p>
            {activePlan.reviewed_by && (
              <div className="text-xs text-emerald-400 flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4" />
                Reviewed by <span className="font-semibold">{activePlan.reviewed_by}</span> on{' '}
                {new Date(activePlan.reviewed_at || '').toLocaleString()}
                {activePlan.review_notes && <span className="text-gray-400">— "{activePlan.review_notes}"</span>}
              </div>
            )}
          </div>

          {/* AI Explanation Banner */}
          <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-400" />
                AI Gateway Execution Rationale (Explanation Only)
              </h4>
              <button
                type="button"
                onClick={handleExplainPlan}
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
                    Explain Execution Plan
                  </>
                )}
              </button>
            </div>

            {explanation || activePlan.ai_explanation ? (
              <div className="bg-purple-950/30 border border-purple-800/40 rounded p-4 text-sm text-purple-200 leading-relaxed">
                {explanation?.explanation || activePlan.ai_explanation}
              </div>
            ) : (
              <p className="text-xs text-gray-400 italic">
                Click above to generate a plain-language summary of the topologically ordered execution sequence.
              </p>
            )}
          </div>

          {/* Section 1: Ordered Execution Sequence (DAG Tasks) */}
          <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <GitBranch className="w-5 h-5 text-indigo-400" />
              1. Ordered Execution Task Sequence (Directed Acyclic Graph)
            </h3>

            <div className="space-y-3">
              {activePlan.tasks.map((task: ModernizationTask, idx: number) => (
                <div
                  key={task.id}
                  className="bg-gray-900/80 border border-gray-700/80 rounded-lg p-4 space-y-3 hover:border-gray-600 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <span className="w-7 h-7 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-700/50 flex items-center justify-center font-bold font-mono text-xs shrink-0 mt-0.5">
                        #{task.sequence_order}
                      </span>
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-bold text-white">{task.title}</h4>
                          <span className="px-2 py-0.5 text-[10px] font-mono font-semibold bg-gray-800 text-gray-300 border border-gray-700 rounded">
                            {task.task_type}
                          </span>
                        </div>
                        <p className="text-xs text-gray-400 mt-1">{task.description}</p>
                      </div>
                    </div>

                    {/* Task Actions & Status */}
                    <div className="flex items-center gap-2 shrink-0">
                      {/* Reorder Buttons */}
                      <div className="flex items-center gap-1 bg-gray-800 border border-gray-700 rounded p-1">
                        <button
                          type="button"
                          disabled={idx === 0}
                          onClick={() => handleReorderTask(task.id, task.sequence_order - 1)}
                          className="p-1 text-gray-400 hover:text-white disabled:opacity-30"
                          title="Move Up"
                        >
                          <ArrowUp className="w-3.5 h-3.5" />
                        </button>
                        <button
                          type="button"
                          disabled={idx === activePlan.tasks.length - 1}
                          onClick={() => handleReorderTask(task.id, task.sequence_order + 1)}
                          className="p-1 text-gray-400 hover:text-white disabled:opacity-30"
                          title="Move Down"
                        >
                          <ArrowDown className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      {/* Status Dropdown */}
                      <select
                        value={task.status}
                        onChange={(e) => handleTaskStatusChange(task.id, e.target.value)}
                        className={`text-xs font-semibold rounded px-2.5 py-1.5 border focus:outline-none ${
                          task.status === 'COMPLETED'
                            ? 'bg-emerald-950 text-emerald-300 border-emerald-700'
                            : task.status === 'IN_PROGRESS'
                            ? 'bg-blue-950 text-blue-300 border-blue-700'
                            : task.status === 'DEFERRED'
                            ? 'bg-amber-950 text-amber-300 border-amber-700'
                            : 'bg-gray-800 text-gray-300 border-gray-700'
                        }`}
                      >
                        <option value="PENDING">PENDING</option>
                        <option value="IN_PROGRESS">IN_PROGRESS</option>
                        <option value="COMPLETED">COMPLETED</option>
                        <option value="DEFERRED">DEFERRED</option>
                        <option value="SKIPPED">SKIPPED</option>
                      </select>
                    </div>
                  </div>

                  {/* Task Traceability Footer */}
                  <div className="pt-2 border-t border-gray-800/80 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    <div>
                      <span className="text-gray-500 font-semibold uppercase text-[10px]">Target Component & File:</span>
                      <p className="text-gray-300 font-mono text-[11px] truncate">
                        {task.target_component} ({task.target_file_path})
                      </p>
                    </div>

                    <div>
                      <span className="text-gray-500 font-semibold uppercase text-[10px]">Verification Checkpoint:</span>
                      <p className="text-indigo-300 text-[11px]">
                        {task.verification_checkpoint?.description || 'Standard refactoring safety check'}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section 2: Business Rules to Preserve Catalog */}
          <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              2. Business Rules to Preserve Catalog
            </h3>

            {activePlan.rules_to_preserve.length > 0 ? (
              <div className="overflow-x-auto border border-gray-700 rounded-lg">
                <table className="w-full text-left text-xs text-gray-300">
                  <thead className="bg-gray-900 text-gray-400 font-semibold border-b border-gray-700 uppercase">
                    <tr>
                      <th className="p-3">Rule Title</th>
                      <th className="p-3">Type</th>
                      <th className="p-3">Source Location</th>
                      <th className="p-3">Condition / Formula</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700/60">
                    {activePlan.rules_to_preserve.map((rule: Record<string, any>, idx: number) => (
                      <tr key={idx} className="hover:bg-gray-750/50 transition-colors">
                        <td className="p-3 font-medium text-white">{rule.title || 'Extracted Business Rule'}</td>
                        <td className="p-3 font-mono text-amber-300">{rule.rule_type}</td>
                        <td className="p-3 font-mono text-gray-400">
                          {rule.relative_file_path}:{rule.line_start}-{rule.line_end}
                        </td>
                        <td className="p-3 font-mono text-indigo-300">
                          {rule.condition_expression || rule.calculation_formula || 'Implicit logic'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-xs text-gray-400 italic">No business rules directly bound to this plan.</p>
            )}
          </div>

          {/* Section 3: Verification Checkpoints Checklist */}
          <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-blue-400" />
              3. Verification Checkpoints Checklist
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {activePlan.verification_checkpoints.map((cp: Record<string, any>, idx: number) => (
                <div key={idx} className="bg-gray-900/60 p-3 rounded border border-gray-700 flex items-start gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-xs font-bold text-white">Task #{cp.task_order}: {cp.task_title}</span>
                    <p className="text-xs text-gray-300 mt-0.5">{cp.checkpoint?.description}</p>
                    <span className="text-[10px] font-mono text-indigo-400">
                      Assertion: {cp.checkpoint?.checkpoint_type}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Review Modal */}
      {reviewModalOpen && activePlan && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 border border-gray-700 rounded-lg max-w-md w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-white">Audit & Review Modernization Plan</h3>
            <p className="text-xs text-gray-400">
              Record human architect review or explicit approval for component <strong>{activePlan.entity_name}</strong>.
            </p>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">Target Plan Status:</label>
                <select
                  value={reviewStatus}
                  onChange={(e) => setReviewStatus(e.target.value as any)}
                  className="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm text-white focus:outline-none"
                >
                  <option value="APPROVED">APPROVED (Ready for Execution)</option>
                  <option value="REVIEWED">REVIEWED (Architect Audit Complete)</option>
                  <option value="REJECTED">REJECTED (Requires Revision)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">Architect Feedback / Audit Notes:</label>
                <textarea
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  placeholder="Record architectural rationale or verification feedback..."
                  rows={3}
                  className="w-full bg-gray-900 border border-gray-700 rounded p-3 text-sm text-white focus:outline-none"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setReviewModalOpen(false)}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white text-xs font-semibold rounded"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleReviewPlan}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded"
              >
                Save Review
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
