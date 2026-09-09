import React, { useState, useEffect } from 'react'
import { api } from '../../services/api'
import type { BusinessRule } from '../../services/api'
import { RuleListTable } from './RuleListTable'
import { RuleDetailDrawer } from './RuleDetailDrawer'
import { BusinessRuleGraph } from './BusinessRuleGraph'
import { SourceEvidenceViewer } from '../analysis/SourceEvidenceViewer'
import { ShieldCheck, FileCheck, AlertTriangle, Calculator, Sparkles, RefreshCw } from 'lucide-react'

interface BusinessRulesPageProps {
  repositoryId: string
  analysisRunId?: string
}

export const BusinessRulesPage: React.FC<BusinessRulesPageProps> = ({ repositoryId, analysisRunId }) => {
  const [analysisId, setAnalysisId] = useState<string | undefined>(analysisRunId)
  const [rules, setRules] = useState<BusinessRule[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [selectedRule, setSelectedRule] = useState<BusinessRule | undefined>(undefined)

  const [selectedType, setSelectedType] = useState<string | undefined>(undefined)
  const [searchQuery, setSearchQuery] = useState<string>('')

  // Source Evidence Viewer Modal State
  const [evidenceModalOpen, setEvidenceModalOpen] = useState(false)
  const [evidenceHighlightLine, setEvidenceHighlightLine] = useState<number>(1)

  useEffect(() => {
    loadData()
  }, [repositoryId, analysisRunId])

  useEffect(() => {
    if (analysisId) {
      fetchRules()
    }
  }, [analysisId, selectedType, searchQuery])

  const loadData = async () => {
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

  const fetchRules = async () => {
    if (!analysisId) return
    try {
      const data = await api.businessRules.list(analysisId, selectedType, undefined, searchQuery || undefined)
      setRules(data)
      if (data.length > 0 && !selectedRule) {
        setSelectedRule(data[0])
      }
    } catch (err) {
      console.error('Failed to fetch business rules', err)
    }
  }

  const handleExplainRule = async (ruleId: string) => {
    try {
      const res = await api.businessRules.explain(ruleId)
      setRules((prev) =>
        prev.map((r) =>
          r.id === ruleId
            ? { ...r, ai_explanation: res.explanation, ai_explanation_status: res.status, status: r.status === 'EXTRACTED' ? 'EXPLAINED' : r.status }
            : r
        )
      )
      if (selectedRule?.id === ruleId) {
        setSelectedRule((prev) =>
          prev
            ? { ...prev, ai_explanation: res.explanation, ai_explanation_status: res.status, status: prev.status === 'EXTRACTED' ? 'EXPLAINED' : prev.status }
            : undefined
        )
      }
    } catch (err) {
      console.error('Failed to generate AI explanation', err)
    }
  }

  const handleReviewRule = async (ruleId: string, status: 'REVIEWED' | 'REJECTED', notes?: string) => {
    try {
      const updated = await api.businessRules.review(ruleId, status, notes)
      setRules((prev) => prev.map((r) => (r.id === ruleId ? updated : r)))
      if (selectedRule?.id === ruleId) {
        setSelectedRule(updated)
      }
    } catch (err) {
      console.error('Failed to review rule', err)
    }
  }

  const handleViewSource = (_filePath: string, lineStart: number) => {
    setEvidenceHighlightLine(lineStart)
    setEvidenceModalOpen(true)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400">
        <RefreshCw className="w-6 h-6 animate-spin mr-2 text-cyan-400" />
        <span>Loading Business Logic Recovery workspace...</span>
      </div>
    )
  }

  if (!analysisId) {
    return (
      <div className="p-12 text-center text-slate-400 bg-slate-900 border border-slate-800 rounded-lg">
        <ShieldCheck className="w-12 h-12 mx-auto mb-3 text-cyan-400 opacity-80" />
        <h3 className="text-base font-bold text-slate-200 mb-1">Static Analysis Required</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto mb-4">
          Please run System X-Ray static analysis first to generate structural ASTs for Business Logic Recovery.
        </p>
      </div>
    )
  }

  // Summary counts
  const totalCount = rules.length
  const validationCount = rules.filter((r) => r.rule_type === 'VALIDATION').length
  const thresholdCount = rules.filter((r) => r.rule_type === 'THRESHOLD').length
  const calcCount = rules.filter((r) => r.rule_type === 'CALCULATION').length
  const stateCount = rules.filter((r) => r.rule_type === 'STATE_TRANSITION').length

  return (
    <div className="flex flex-col gap-6">
      {/* Metrics Summary Header */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <div className="bg-slate-900 border border-slate-800 p-3.5 rounded-lg">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Total Rules</span>
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-xl font-bold text-slate-100">{totalCount}</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-3.5 rounded-lg">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Validations</span>
            <AlertTriangle className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-xl font-bold text-slate-100">{validationCount}</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-3.5 rounded-lg">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Thresholds</span>
            <FileCheck className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-xl font-bold text-slate-100">{thresholdCount}</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-3.5 rounded-lg">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Calculations</span>
            <Calculator className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-xl font-bold text-slate-100">{calcCount}</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-3.5 rounded-lg">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>State Changes</span>
            <Sparkles className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-xl font-bold text-slate-100">{stateCount}</div>
        </div>
      </div>

      {/* Main Split-Pane Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div className="lg:col-span-7 h-[650px]">
          <RuleListTable
            rules={rules}
            selectedRuleId={selectedRule?.id}
            onSelectRule={(rule) => setSelectedRule(rule)}
            selectedType={selectedType}
            onSelectType={setSelectedType}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
          />
        </div>

        <div className="lg:col-span-5 h-[650px]">
          {selectedRule ? (
            <RuleDetailDrawer
              rule={selectedRule}
              onClose={() => setSelectedRule(undefined)}
              onExplain={handleExplainRule}
              onReview={handleReviewRule}
              onViewSource={handleViewSource}
            />
          ) : (
            <div className="flex items-center justify-center h-full bg-slate-900 border border-slate-800 rounded-lg text-slate-500 text-sm">
              Select a business rule to inspect facts and line evidence.
            </div>
          )}
        </div>
      </div>

      {/* Deterministic Rule Trace Visualizer */}
      <BusinessRuleGraph
        rules={rules}
        selectedRuleId={selectedRule?.id}
      />

      {/* Line Evidence Viewer Modal */}
      {selectedRule && evidenceModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 max-w-2xl w-full">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-sm font-bold text-slate-200">Source Evidence Viewer</h3>
              <button onClick={() => setEvidenceModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                &times;
              </button>
            </div>
            <SourceEvidenceViewer
              relative_file_path={selectedRule.relative_file_path}
              line_number={evidenceHighlightLine}
              source_construct={selectedRule.source_construct}
              evidence_reason={selectedRule.extraction_reason}
              is_resolved={true}
            />
          </div>
        </div>
      )}
    </div>
  )
}
