import React, { useState, useEffect } from 'react'
import type { ValidationRun, TransformationProposal } from '../../services/api'
import {
  runValidation,
  getValidationRuns,
  reviewValidationRun,
  explainValidationRun,
} from '../../services/api'


interface ValidationWorkspacePageProps {
  proposal: TransformationProposal
  onBack?: () => void
}

export const ValidationWorkspacePage: React.FC<ValidationWorkspacePageProps> = ({ proposal, onBack }) => {
  const [runs, setRuns] = useState<ValidationRun[]>([])
  const [selectedRun, setSelectedRun] = useState<ValidationRun | null>(null)
  const [loading, setLoading] = useState(false)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Review form
  const [reviewerName, setReviewerName] = useState('qa_lead')
  const [reviewNotes, setReviewNotes] = useState('')
  const [reviewing, setReviewing] = useState(false)

  // AI explanation
  const [explaining, setExplaining] = useState(false)

  const fetchRuns = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getValidationRuns(proposal.id)
      setRuns(data)
      if (data.length > 0) {
        setSelectedRun(data[0])
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch validation runs.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRuns()
  }, [proposal.id])

  const handleRunValidation = async () => {
    setRunning(true)
    setError(null)
    try {
      const newRun = await runValidation(proposal.id)
      setRuns((prev) => [newRun, ...prev])
      setSelectedRun(newRun)
    } catch (err: any) {
      setError(err?.message || 'Validation run failed to start.')
    } finally {
      setRunning(false)
    }
  }

  const handleReview = async (status: 'REVIEWED' | 'VALIDATED') => {
    if (!selectedRun) return
    setReviewing(true)
    try {
      const updated = await reviewValidationRun(selectedRun.id, status, reviewerName, reviewNotes)
      setSelectedRun(updated)
      setRuns((prev) => prev.map((r) => (r.id === updated.id ? updated : r)))
    } catch (err: any) {
      setError(err?.message || 'Failed to record human review.')
    } finally {
      setReviewing(false)
    }
  }

  const handleExplain = async () => {
    if (!selectedRun) return
    setExplaining(true)
    try {
      const res = await explainValidationRun(selectedRun.id)
      setSelectedRun({
        ...selectedRun,
        ai_explanation: res.explanation,
        ai_explanation_status: res.status,
      })
    } catch (err: any) {
      setError(err?.message || 'Failed to generate AI evidence explanation.')
    } finally {
      setExplaining(false)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'BUILD_PASS':
      case 'TEST_PASS':
      case 'MATCH':
      case 'VERIFIED':
      case 'VALIDATED':
        return <span style={styles.badgeSuccess}>{status}</span>
      case 'BUILD_FAIL':
      case 'TEST_FAIL':
      case 'MISMATCH':
      case 'FAILED':
      case 'REJECTED':
        return <span style={styles.badgeDanger}>{status}</span>
      case 'BUILD_ENVIRONMENT_UNAVAILABLE':
      case 'TEST_ENVIRONMENT_UNAVAILABLE':
      case 'UNABLE_TO_VALIDATE':
        return <span style={styles.badgeWarning}>{status}</span>
      default:
        return <span style={styles.badgeNeutral}>{status}</span>
    }
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div>
          {onBack && (
            <button onClick={onBack} style={styles.backButton}>
              ← Back to Proposals
            </button>
          )}
          <h1 style={styles.title}>Phase 9 — Build, Unit Test & Behavioral Equivalence Validation</h1>
          <p style={styles.subtitle}>
            Target Entity: <strong>{proposal.target_entity}</strong> | Proposal ID: <code>{proposal.id.slice(0, 8)}</code>
          </p>
        </div>
        <button
          onClick={handleRunValidation}
          disabled={running}
          style={running ? styles.actionButtonDisabled : styles.actionButton}
        >
          {running ? 'Executing Isolated Pipeline...' : '▶ Run Empirical Validation Pipeline'}
        </button>
      </div>

      {error && <div style={styles.errorAlert}>⚠️ {error}</div>}

      {/* Main Content Split */}
      <div style={styles.contentSplit}>
        {/* Left Sidebar: Runs History */}
        <div style={styles.sidebar}>
          <h3 style={styles.sidebarTitle}>Validation Runs ({runs.length})</h3>
          {loading ? (
            <p style={styles.mutedText}>Loading validation runs...</p>
          ) : runs.length === 0 ? (
            <p style={styles.mutedText}>No validation runs executed yet. Click above to run empirical pipeline.</p>
          ) : (
            <div style={styles.runsList}>
              {runs.map((r) => (
                <div
                  key={r.id}
                  onClick={() => setSelectedRun(r)}
                  style={selectedRun?.id === r.id ? styles.runCardActive : styles.runCard}
                >
                  <div style={styles.runCardHeader}>
                    <span style={styles.runId}>Run #{r.id.slice(0, 8)}</span>
                    {getStatusBadge(r.overall_status)}
                  </div>
                  <div style={styles.runMeta}>
                    <span>Build: {r.build_status}</span>
                    <span>Test: {r.test_status}</span>
                    <span>Behavior: {r.behavioral_status}</span>
                  </div>
                  <div style={styles.runTime}>{new Date(r.created_at).toLocaleString()}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Area: Selected Run Workspace Details */}
        <div style={styles.mainArea}>
          {selectedRun ? (
            <div>
              {/* Summary Metric Cards */}
              <div style={styles.metricsGrid}>
                <div style={styles.metricCard}>
                  <div style={styles.metricLabel}>1. Build Status</div>
                  <div style={styles.metricValue}>{getStatusBadge(selectedRun.build_status)}</div>
                  <div style={styles.metricDetail}>Isolated javac / build verification</div>
                </div>
                <div style={styles.metricCard}>
                  <div style={styles.metricLabel}>2. Unit Test Status</div>
                  <div style={styles.metricValue}>{getStatusBadge(selectedRun.test_status)}</div>
                  <div style={styles.metricDetail}>Regression & generated test stubs</div>
                </div>
                <div style={styles.metricCard}>
                  <div style={styles.metricLabel}>3. Behavioral Equivalence</div>
                  <div style={styles.metricValue}>{getStatusBadge(selectedRun.behavioral_status)}</div>
                  <div style={styles.metricDetail}>
                    {selectedRun.passed_scenarios} / {selectedRun.total_scenarios} Phase 4 Scenarios Passed
                  </div>
                </div>
                <div style={styles.metricCard}>
                  <div style={styles.metricLabel}>Overall Empirical Verdict</div>
                  <div style={styles.metricValue}>{getStatusBadge(selectedRun.overall_status)}</div>
                  <div style={styles.metricDetail}>Human Gate: {getStatusBadge(selectedRun.review_status)}</div>
                </div>
              </div>

              {/* Workspace Safeguard Notice */}
              {selectedRun.workspace_path && (
                <div style={styles.safeguardNotice}>
                  🔒 <strong>Isolation Safeguard Active:</strong> Execution ran in temporary workspace at{' '}
                  <code>{selectedRun.workspace_path}</code>. Original <code>storage/extracted/</code> source and Phase 8
                  artifacts were strictly unmodified.
                </div>
              )}

              {/* Behavioral Scenarios Section */}
              <div style={styles.sectionCard}>
                <h3 style={styles.sectionTitle}>
                  Authoritative Phase 4 Behavioral Rule Scenarios ({selectedRun.scenarios.length})
                </h3>
                <p style={styles.sectionDesc}>
                  Inputs strictly generated from Phase 4 Business Rules. Legacy and modern logic were provided identical
                  inputs to compare output equivalence.
                </p>
                {selectedRun.scenarios.length === 0 ? (
                  <p style={styles.mutedText}>No rule scenarios generated for this run.</p>
                ) : (
                  <table style={styles.table}>
                    <thead>
                      <tr>
                        <th style={styles.th}>Rule ID</th>
                        <th style={styles.th}>Scenario Name</th>
                        <th style={styles.th}>Rule Type</th>
                        <th style={styles.th}>Inputs</th>
                        <th style={styles.th}>Legacy Output</th>
                        <th style={styles.th}>Modern Output</th>
                        <th style={styles.th}>Equivalence</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedRun.scenarios.map((sc) => (
                        <tr key={sc.id}>
                          <td style={styles.td}>
                            <code>{sc.business_rule_id}</code>
                          </td>
                          <td style={styles.td}>{sc.scenario_name}</td>
                          <td style={styles.td}>{sc.rule_type}</td>
                          <td style={styles.tdCode}>
                            <pre style={styles.codeSnippet}>{JSON.stringify(sc.inputs, null, 2)}</pre>
                          </td>
                          <td style={styles.tdCode}>
                            <pre style={styles.codeSnippet}>{JSON.stringify(sc.legacy_expected_outputs, null, 2)}</pre>
                          </td>
                          <td style={styles.tdCode}>
                            <pre style={styles.codeSnippet}>{JSON.stringify(sc.modern_actual_outputs, null, 2)}</pre>
                          </td>
                          <td style={styles.td}>{getStatusBadge(sc.comparison_result)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>

              {/* Execution Evidence & Logs Accordion */}
              <div style={styles.sectionCard}>
                <h3 style={styles.sectionTitle}>Execution Evidence & Subprocess Logs ({selectedRun.evidences.length})</h3>
                <p style={styles.sectionDesc}>
                  Captured raw stdout, stderr, exit codes, and execution durations from 30s timeout-guarded processes.
                </p>
                {selectedRun.evidences.map((ev) => (
                  <div key={ev.id} style={styles.evidenceBox}>
                    <div style={styles.evidenceHeader}>
                      <span>
                        <strong>[{ev.phase_category}]</strong> {ev.command_executed}
                      </span>
                      <span>
                        Exit Code: <code>{ev.exit_code ?? 'N/A'}</code> | Time: {ev.execution_time_seconds.toFixed(2)}s |{' '}
                        {getStatusBadge(ev.status)}
                      </span>
                    </div>
                    {ev.stdout_content && (
                      <div style={styles.logBlock}>
                        <div style={styles.logLabel}>stdout:</div>
                        <pre style={styles.logPre}>{ev.stdout_content}</pre>
                      </div>
                    )}
                    {ev.stderr_content && (
                      <div style={styles.logBlock}>
                        <div style={styles.logLabelError}>stderr / error:</div>
                        <pre style={styles.logPreError}>{ev.stderr_content}</pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* AI Evidence Explanation */}
              <div style={styles.sectionCard}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h3 style={styles.sectionTitle}>AI Evidence Explanation (IBM watsonx / AI Gateway)</h3>
                  <button
                    onClick={handleExplain}
                    disabled={explaining}
                    style={explaining ? styles.secondaryButtonDisabled : styles.secondaryButton}
                  >
                    {explaining ? 'Generating AI Explanation...' : '🤖 Explain Evidence'}
                  </button>
                </div>
                {selectedRun.ai_explanation ? (
                  <div style={styles.aiBox}>
                    <p style={styles.aiText}>{selectedRun.ai_explanation}</p>
                  </div>
                ) : (
                  <p style={styles.mutedText}>
                    Click 'Explain Evidence' to request a plain-language summary of empirical build, test, and behavioral results.
                  </p>
                )}
              </div>

              {/* Mandatory Human Review Gate */}
              <div style={styles.reviewCard}>
                <h3 style={styles.sectionTitle}>Mandatory Human Review Gate (AGENTS.md §4.5)</h3>
                <p style={styles.sectionDesc}>
                  No automatic approval. Even if build and tests pass, a human architect must verify and sign off.
                </p>
                <div style={styles.reviewForm}>
                  <div style={{ flex: 1 }}>
                    <label style={styles.label}>Reviewer Name / Role:</label>
                    <input
                      type="text"
                      value={reviewerName}
                      onChange={(e) => setReviewerName(e.target.value)}
                      style={styles.input}
                    />
                  </div>
                  <div style={{ flex: 2 }}>
                    <label style={styles.label}>Audit & Verification Notes:</label>
                    <input
                      type="text"
                      placeholder="Add auditable verification notes..."
                      value={reviewNotes}
                      onChange={(e) => setReviewNotes(e.target.value)}
                      style={styles.input}
                    />
                  </div>
                </div>
                <div style={styles.reviewActions}>
                  <button
                    onClick={() => handleReview('REVIEWED')}
                    disabled={reviewing}
                    style={styles.secondaryButton}
                  >
                    Mark Reviewed
                  </button>
                  <button
                    onClick={() => handleReview('VALIDATED')}
                    disabled={reviewing}
                    style={styles.approveButton}
                  >
                    Approve & Mark Verified
                  </button>
                </div>
                {selectedRun.reviewed_by && (
                  <div style={styles.reviewMeta}>
                    Verified by <strong>{selectedRun.reviewed_by}</strong> at{' '}
                    {new Date(selectedRun.reviewed_at || '').toLocaleString()}. Notes: {selectedRun.review_notes || 'None'}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div style={styles.emptyMain}>Select a validation run from the sidebar or start a new run.</div>
          )}
        </div>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: '24px',
    backgroundColor: '#0f172a',
    color: '#f8fafc',
    minHeight: '100vh',
    fontFamily: 'Inter, system-ui, sans-serif',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
    borderBottom: '1px solid #1e293b',
    paddingBottom: '16px',
  },
  title: {
    fontSize: '22px',
    fontWeight: '700',
    margin: 0,
    color: '#38bdf8',
  },
  subtitle: {
    fontSize: '13px',
    color: '#94a3b8',
    marginTop: '4px',
  },
  backButton: {
    background: 'none',
    border: 'none',
    color: '#38bdf8',
    cursor: 'pointer',
    padding: 0,
    fontSize: '13px',
    marginBottom: '8px',
  },
  actionButton: {
    backgroundColor: '#0284c7',
    color: '#ffffff',
    border: 'none',
    padding: '10px 18px',
    borderRadius: '6px',
    fontWeight: '600',
    cursor: 'pointer',
    fontSize: '14px',
    boxShadow: '0 4px 12px rgba(2, 132, 199, 0.3)',
  },
  actionButtonDisabled: {
    backgroundColor: '#334155',
    color: '#94a3b8',
    border: 'none',
    padding: '10px 18px',
    borderRadius: '6px',
    cursor: 'not-allowed',
  },
  errorAlert: {
    backgroundColor: '#7f1d1d',
    color: '#fecaca',
    padding: '12px 16px',
    borderRadius: '6px',
    marginBottom: '20px',
    fontSize: '14px',
  },
  contentSplit: {
    display: 'flex',
    gap: '24px',
  },
  sidebar: {
    width: '300px',
    flexShrink: 0,
    backgroundColor: '#1e293b',
    borderRadius: '8px',
    padding: '16px',
    border: '1px solid #334155',
  },
  sidebarTitle: {
    fontSize: '15px',
    fontWeight: '600',
    margin: '0 0 12px 0',
    color: '#cbd5e1',
  },
  runsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  runCard: {
    backgroundColor: '#0f172a',
    padding: '12px',
    borderRadius: '6px',
    border: '1px solid #334155',
    cursor: 'pointer',
  },
  runCardActive: {
    backgroundColor: '#1e293b',
    padding: '12px',
    borderRadius: '6px',
    border: '2px solid #0284c7',
    cursor: 'pointer',
  },
  runCardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '6px',
  },
  runId: {
    fontWeight: '600',
    fontSize: '13px',
    color: '#e2e8f0',
  },
  runMeta: {
    fontSize: '11px',
    color: '#94a3b8',
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  runTime: {
    fontSize: '10px',
    color: '#64748b',
    marginTop: '6px',
  },
  mainArea: {
    flex: 1,
  },
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '16px',
    marginBottom: '20px',
  },
  metricCard: {
    backgroundColor: '#1e293b',
    padding: '16px',
    borderRadius: '8px',
    border: '1px solid #334155',
  },
  metricLabel: {
    fontSize: '12px',
    color: '#94a3b8',
    marginBottom: '8px',
    fontWeight: '500',
  },
  metricValue: {
    marginBottom: '8px',
  },
  metricDetail: {
    fontSize: '11px',
    color: '#64748b',
  },
  safeguardNotice: {
    backgroundColor: '#1e293b',
    borderLeft: '4px solid #38bdf8',
    padding: '12px 16px',
    borderRadius: '4px',
    fontSize: '13px',
    color: '#cbd5e1',
    marginBottom: '20px',
  },
  sectionCard: {
    backgroundColor: '#1e293b',
    padding: '20px',
    borderRadius: '8px',
    border: '1px solid #334155',
    marginBottom: '20px',
  },
  reviewCard: {
    backgroundColor: '#1e293b',
    padding: '20px',
    borderRadius: '8px',
    border: '2px solid #0284c7',
    marginBottom: '20px',
  },
  sectionTitle: {
    fontSize: '16px',
    fontWeight: '600',
    margin: '0 0 4px 0',
    color: '#f1f5f9',
  },
  sectionDesc: {
    fontSize: '12px',
    color: '#94a3b8',
    marginTop: 0,
    marginBottom: '16px',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '12px',
  },
  th: {
    textAlign: 'left',
    padding: '8px 12px',
    backgroundColor: '#0f172a',
    color: '#94a3b8',
    borderBottom: '1px solid #334155',
  },
  td: {
    padding: '10px 12px',
    borderBottom: '1px solid #334155',
    verticalAlign: 'top',
  },
  tdCode: {
    padding: '10px 12px',
    borderBottom: '1px solid #334155',
    verticalAlign: 'top',
    maxWidth: '200px',
  },
  codeSnippet: {
    margin: 0,
    fontSize: '11px',
    backgroundColor: '#0f172a',
    padding: '6px',
    borderRadius: '4px',
    overflowX: 'auto',
    whiteSpace: 'pre-wrap',
  },
  evidenceBox: {
    backgroundColor: '#0f172a',
    borderRadius: '6px',
    padding: '12px',
    marginBottom: '12px',
    border: '1px solid #334155',
  },
  evidenceHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '13px',
    marginBottom: '8px',
  },
  logBlock: {
    marginTop: '6px',
  },
  logLabel: {
    fontSize: '11px',
    color: '#38bdf8',
    fontWeight: '600',
  },
  logLabelError: {
    fontSize: '11px',
    color: '#f87171',
    fontWeight: '600',
  },
  logPre: {
    backgroundColor: '#020617',
    color: '#e2e8f0',
    padding: '8px',
    borderRadius: '4px',
    fontSize: '11px',
    margin: '4px 0 0 0',
    overflowX: 'auto',
    maxHeight: '150px',
  },
  logPreError: {
    backgroundColor: '#450a0a',
    color: '#fecaca',
    padding: '8px',
    borderRadius: '4px',
    fontSize: '11px',
    margin: '4px 0 0 0',
    overflowX: 'auto',
    maxHeight: '150px',
  },
  aiBox: {
    backgroundColor: '#0f172a',
    borderLeft: '4px solid #a855f7',
    padding: '14px',
    borderRadius: '4px',
    marginTop: '12px',
  },
  aiText: {
    margin: 0,
    fontSize: '13px',
    color: '#e9d5ff',
    lineHeight: '1.5',
  },
  reviewForm: {
    display: 'flex',
    gap: '16px',
    marginBottom: '16px',
  },
  label: {
    display: 'block',
    fontSize: '12px',
    color: '#94a3b8',
    marginBottom: '4px',
  },
  input: {
    width: '100%',
    backgroundColor: '#0f172a',
    border: '1px solid #334155',
    color: '#f8fafc',
    padding: '8px 12px',
    borderRadius: '6px',
    fontSize: '13px',
  },
  reviewActions: {
    display: 'flex',
    gap: '12px',
  },
  approveButton: {
    backgroundColor: '#16a34a',
    color: '#ffffff',
    border: 'none',
    padding: '10px 18px',
    borderRadius: '6px',
    fontWeight: '600',
    cursor: 'pointer',
    fontSize: '13px',
  },
  secondaryButton: {
    backgroundColor: '#334155',
    color: '#f8fafc',
    border: 'none',
    padding: '10px 18px',
    borderRadius: '6px',
    fontWeight: '600',
    cursor: 'pointer',
    fontSize: '13px',
  },
  secondaryButtonDisabled: {
    backgroundColor: '#1e293b',
    color: '#64748b',
    border: 'none',
    padding: '10px 18px',
    borderRadius: '6px',
    cursor: 'not-allowed',
    fontSize: '13px',
  },
  reviewMeta: {
    marginTop: '14px',
    fontSize: '12px',
    color: '#86efac',
  },
  badgeSuccess: {
    backgroundColor: '#14532d',
    color: '#86efac',
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '11px',
    fontWeight: '700',
  },
  badgeDanger: {
    backgroundColor: '#7f1d1d',
    color: '#fecaca',
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '11px',
    fontWeight: '700',
  },
  badgeWarning: {
    backgroundColor: '#713f12',
    color: '#fde047',
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '11px',
    fontWeight: '700',
  },
  badgeNeutral: {
    backgroundColor: '#334155',
    color: '#cbd5e1',
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '11px',
    fontWeight: '700',
  },
  mutedText: {
    color: '#64748b',
    fontSize: '13px',
  },
  emptyMain: {
    textAlign: 'center',
    padding: '60px 0',
    color: '#64748b',
    fontSize: '14px',
  },
}
