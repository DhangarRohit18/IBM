import React, { useState, useEffect } from 'react'
import { api, type ModernizationPlan, type TransformationProposal } from '../../services/api'
import {
  Code,
  FileCode,
  ShieldCheck,
  CheckCircle,
  XCircle,
  Clock,
  Sparkles,
  Layers,
  GitPullRequest,
  Check,
  X,
  Send,
  Lock,
  AlertCircle,
} from 'lucide-react'

interface Props {
  analysisId: string
}

export const TransformationStudioPage: React.FC<Props> = ({ analysisId }) => {
  const [plans, setPlans] = useState<ModernizationPlan[]>([])
  const [selectedPlanId, setSelectedPlanId] = useState<string>('')
  const [proposals, setProposals] = useState<TransformationProposal[]>([])
  const [selectedProposalId, setSelectedProposalId] = useState<string>('')
  const [selectedArtifactId, setSelectedArtifactId] = useState<string>('')

  const [loadingPlans, setLoadingPlans] = useState<boolean>(true)
  const [loadingProposals, setLoadingProposals] = useState<boolean>(false)
  const [generating, setGenerating] = useState<boolean>(false)
  const [acting, setActing] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [activeView, setActiveView] = useState<'code' | 'diff' | 'rules'>('code')
  const [reviewNotes, setReviewNotes] = useState<string>('')

  useEffect(() => {
    loadPlans()
  }, [analysisId])

  const loadPlans = async () => {
    try {
      setLoadingPlans(true)
      setError(null)
      const data = await api.modernization.listPlans(analysisId)
      setPlans(data)
      if (data.length > 0) {
        setSelectedPlanId(data[0].id)
        loadProposals(data[0].id)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load modernization plans')
    } finally {
      setLoadingPlans(false)
    }
  }

  const loadProposals = async (planId: string) => {
    try {
      setLoadingProposals(true)
      setError(null)
      const data = await api.modernization.listTransformations(planId)
      setProposals(data)
      if (data.length > 0) {
        setSelectedProposalId(data[0].id)
        if (data[0].artifacts && data[0].artifacts.length > 0) {
          setSelectedArtifactId(data[0].artifacts[0].id)
        }
      } else {
        setSelectedProposalId('')
        setSelectedArtifactId('')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load transformation proposals')
    } finally {
      setLoadingProposals(false)
    }
  }

  const handlePlanChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id = e.target.value
    setSelectedPlanId(id)
    loadProposals(id)
  }

  const handleGenerateProposals = async () => {
    if (!selectedPlanId) return
    try {
      setGenerating(true)
      setError(null)
      const data = await api.modernization.proposeTransformations(selectedPlanId)
      setProposals(data)
      if (data.length > 0) {
        setSelectedProposalId(data[0].id)
        if (data[0].artifacts && data[0].artifacts.length > 0) {
          setSelectedArtifactId(data[0].artifacts[0].id)
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate transformation proposals')
    } finally {
      setGenerating(false)
    }
  }

  const handleReview = async (status: 'APPROVED' | 'REJECTED') => {
    if (!selectedProposalId) return
    try {
      setActing(true)
      setError(null)
      const updated = await api.modernization.reviewTransformation(
        selectedProposalId,
        status,
        reviewNotes || `Human review ${status.toLowerCase()} by architect`
      )
      setProposals((prev) => prev.map((p) => (p.id === updated.id ? updated : p)))
      setReviewNotes('')
    } catch (err: any) {
      setError(err.message || `Failed to review transformation`)
    } finally {
      setActing(false)
    }
  }

  const handleApply = async () => {
    if (!selectedProposalId) return
    try {
      setActing(true)
      setError(null)
      const updated = await api.modernization.applyTransformation(selectedProposalId, 'lead_architect')
      setProposals((prev) => prev.map((p) => (p.id === updated.id ? updated : p)))
    } catch (err: any) {
      setError(err.message || 'Failed to apply transformation to isolated workspace')
    } finally {
      setActing(false)
    }
  }

  const selectedProposal = proposals.find((p) => p.id === selectedProposalId)
  const selectedArtifact = selectedProposal?.artifacts.find((a) => a.id === selectedArtifactId) || selectedProposal?.artifacts[0]

  const getStatusBadge = (st: string) => {
    switch (st) {
      case 'APPLIED':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 flex items-center gap-1"><Lock className="w-3 h-3" /> APPLIED</span>
      case 'APPROVED':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-blue-950 text-blue-300 border border-blue-800 flex items-center gap-1"><CheckCircle className="w-3 h-3" /> APPROVED</span>
      case 'REJECTED':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-950 text-rose-300 border border-rose-800 flex items-center gap-1"><XCircle className="w-3 h-3" /> REJECTED</span>
      case 'REVIEWED':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-purple-950 text-purple-300 border border-purple-800 flex items-center gap-1"><Clock className="w-3 h-3" /> REVIEWED</span>
      default:
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-950 text-amber-300 border border-amber-800 flex items-center gap-1"><Clock className="w-3 h-3" /> PROPOSED</span>
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Code className="w-6 h-6 text-indigo-400" />
              <h2 className="text-xl font-bold text-slate-100">Phase 8 — Transformation Studio</h2>
            </div>
            <p className="text-sm text-slate-400">
              Generate isolated, evidence-grounded code transformation proposals for approved Phase 7 plan tasks.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={selectedPlanId}
              onChange={handlePlanChange}
              disabled={loadingPlans || plans.length === 0}
              className="bg-slate-950 border border-slate-800 text-slate-200 text-sm rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
            >
              {plans.length === 0 ? (
                <option value="">No Plans Available</option>
              ) : (
                plans.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.entity_name} ({p.strategy_type})
                  </option>
                ))
              )}
            </select>

            <button
              onClick={handleGenerateProposals}
              disabled={generating || !selectedPlanId}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-lg shadow-lg flex items-center gap-2 disabled:opacity-50 transition-all"
            >
              <Sparkles className="w-4 h-4" />
              {generating ? 'Generating Proposals...' : 'Propose Transformations'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-rose-950/80 border border-rose-800 text-rose-300 p-4 rounded-xl flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <span className="text-sm font-medium">{error}</span>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Sidebar — Task Proposals List */}
        <div className="lg:col-span-4 bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-xl flex flex-col space-y-4">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-400" />
            Transformation Proposals ({proposals.length})
          </h3>

          {loadingProposals ? (
            <div className="p-8 text-center text-slate-400 text-sm">Loading proposals...</div>
          ) : proposals.length === 0 ? (
            <div className="p-8 text-center text-slate-500 text-sm border border-dashed border-slate-800 rounded-xl">
              No transformation proposals generated yet. Click "Propose Transformations" above.
            </div>
          ) : (
            <div className="space-y-3 overflow-y-auto max-h-[600px] pr-1">
              {proposals.map((prop) => {
                const isSelected = prop.id === selectedProposalId
                return (
                  <div
                    key={prop.id}
                    onClick={() => {
                      setSelectedProposalId(prop.id)
                      if (prop.artifacts && prop.artifacts.length > 0) {
                        setSelectedArtifactId(prop.artifacts[0].id)
                      }
                    }}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-indigo-950/40 border-indigo-500 text-slate-100 shadow-md'
                        : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-indigo-300">
                        {prop.transformation_type}
                      </span>
                      {getStatusBadge(prop.status)}
                    </div>

                    <h4 className="text-sm font-semibold text-slate-200 line-clamp-1">{prop.target_entity}</h4>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-2">{prop.summary}</p>

                    <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                      <span>{prop.artifacts.length} Artifact(s)</span>
                      <span>{prop.rule_ids.length} Rule(s) Mapped</span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Right Content Area — Code & Diff Inspection */}
        <div className="lg:col-span-8 space-y-6">
          {selectedProposal ? (
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-xl space-y-6">
              {/* Proposal Header & Human Review Bar */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-bold text-slate-100">{selectedProposal.target_entity}</h3>
                    {getStatusBadge(selectedProposal.status)}
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Transformation Type: <span className="font-mono text-slate-300">{selectedProposal.transformation_type}</span>
                  </p>
                </div>

                {/* Human Review Actions */}
                <div className="flex items-center gap-2">
                  {selectedProposal.status === 'PROPOSED' || selectedProposal.status === 'REVIEWED' ? (
                    <>
                      <button
                        onClick={() => handleReview('APPROVED')}
                        disabled={acting}
                        className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 shadow"
                      >
                        <Check className="w-3.5 h-3.5" /> Approve
                      </button>
                      <button
                        onClick={() => handleReview('REJECTED')}
                        disabled={acting}
                        className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 shadow"
                      >
                        <X className="w-3.5 h-3.5" /> Reject
                      </button>
                    </>
                  ) : selectedProposal.status === 'APPROVED' ? (
                    <button
                      onClick={handleApply}
                      disabled={acting}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg flex items-center gap-2 shadow-lg animate-pulse"
                    >
                      <Send className="w-4 h-4" /> Apply to Isolated Workspace
                    </button>
                  ) : null}
                </div>
              </div>

              {/* Provenance Tags: Deterministic vs AI vs Human */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="bg-slate-950/80 border border-slate-800 p-3 rounded-lg flex items-center gap-3">
                  <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
                  <div>
                    <span className="text-[10px] uppercase font-bold text-slate-400">Source Evidence</span>
                    <p className="text-xs font-semibold text-slate-200">{selectedProposal.rule_ids.length} Business Rules Grounded</p>
                  </div>
                </div>

                <div className="bg-slate-950/80 border border-slate-800 p-3 rounded-lg flex items-center gap-3">
                  <Sparkles className="w-5 h-5 text-indigo-400 shrink-0" />
                  <div>
                    <span className="text-[10px] uppercase font-bold text-slate-400">AI Gateway Context</span>
                    <p className="text-xs font-semibold text-slate-200">{selectedProposal.ai_proposal_status}</p>
                  </div>
                </div>

                <div className="bg-slate-950/80 border border-slate-800 p-3 rounded-lg flex items-center gap-3">
                  <GitPullRequest className="w-5 h-5 text-amber-400 shrink-0" />
                  <div>
                    <span className="text-[10px] uppercase font-bold text-slate-400">Human Audit Decision</span>
                    <p className="text-xs font-semibold text-slate-200">
                      {selectedProposal.reviewed_by ? `Reviewed by ${selectedProposal.reviewed_by}` : 'Pending Architect Approval'}
                    </p>
                  </div>
                </div>
              </div>

              {selectedProposal.storage_workspace_path && (
                <div className="bg-emerald-950/40 border border-emerald-800/80 p-3 rounded-lg flex items-center gap-2 text-xs text-emerald-300">
                  <Lock className="w-4 h-4 shrink-0 text-emerald-400" />
                  <span>
                    Applied to Isolated Workspace: <code className="font-mono">{selectedProposal.storage_workspace_path}</code>
                  </span>
                </div>
              )}

              {/* Artifact Tabs & Code Viewer */}
              {selectedProposal.artifacts.length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <div className="flex items-center gap-2 overflow-x-auto">
                      {selectedProposal.artifacts.map((art) => (
                        <button
                          key={art.id}
                          onClick={() => setSelectedArtifactId(art.id)}
                          className={`px-3 py-1.5 text-xs font-mono rounded-lg transition-all flex items-center gap-1.5 ${
                            art.id === (selectedArtifact?.id || '')
                              ? 'bg-indigo-600 text-white font-semibold'
                              : 'bg-slate-950 text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          <FileCode className="w-3.5 h-3.5" />
                          {art.artifact_category}
                        </button>
                      ))}
                    </div>

                    <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
                      <button
                        onClick={() => setActiveView('code')}
                        className={`px-2.5 py-1 text-xs font-medium rounded ${
                          activeView === 'code' ? 'bg-slate-800 text-slate-100' : 'text-slate-400'
                        }`}
                      >
                        Generated Code
                      </button>
                      <button
                        onClick={() => setActiveView('diff')}
                        className={`px-2.5 py-1 text-xs font-medium rounded ${
                          activeView === 'diff' ? 'bg-slate-800 text-slate-100' : 'text-slate-400'
                        }`}
                      >
                        Unified Diff
                      </button>
                      <button
                        onClick={() => setActiveView('rules')}
                        className={`px-2.5 py-1 text-xs font-medium rounded ${
                          activeView === 'rules' ? 'bg-slate-800 text-slate-100' : 'text-slate-400'
                        }`}
                      >
                        Preserved Rules ({selectedArtifact?.rules_preserved.length || 0})
                      </button>
                    </div>
                  </div>

                  {/* Code View */}
                  {activeView === 'code' && selectedArtifact && (
                    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 overflow-x-auto max-h-[500px]">
                      <div className="text-xs font-mono text-slate-500 mb-2 border-b border-slate-900 pb-1">
                        Target Path: {selectedArtifact.target_file_path}
                      </div>
                      <pre className="text-xs font-mono text-emerald-400 whitespace-pre leading-relaxed">
                        {selectedArtifact.generated_code}
                      </pre>
                    </div>
                  )}

                  {/* Diff View */}
                  {activeView === 'diff' && selectedArtifact && (
                    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 overflow-x-auto max-h-[500px]">
                      <pre className="text-xs font-mono text-slate-300 whitespace-pre leading-relaxed">
                        {selectedArtifact.diff_content}
                      </pre>
                    </div>
                  )}

                  {/* Rules View */}
                  {activeView === 'rules' && selectedArtifact && (
                    <div className="space-y-3">
                      {selectedArtifact.rules_preserved.length === 0 ? (
                        <div className="p-6 text-center text-slate-500 text-sm">No business rules mapped to this artifact.</div>
                      ) : (
                        selectedArtifact.rules_preserved.map((r, idx) => (
                          <div key={idx} className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                            <div className="flex items-center justify-between text-xs">
                              <span className="font-semibold text-slate-200">{r.title || `Rule ${idx + 1}`}</span>
                              <span className="font-mono text-indigo-400">{r.rule_type || 'BUSINESS_RULE'}</span>
                            </div>
                            <p className="text-xs font-mono text-emerald-400 bg-slate-900/60 p-2 rounded border border-slate-800">
                              {r.condition_expression || r.calculation_formula || 'Preserved condition'}
                            </p>
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-12 text-center text-slate-500 text-sm shadow-xl">
              Select a transformation proposal from the list on the left to inspect candidate code and diffs.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
