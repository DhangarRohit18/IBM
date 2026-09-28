/**
 * LEGACYX 2.0 — Modernization Assurance Platform (RoadGuard X / MeetIQ Design System)
 *
 * Core Motto: Modernize the Code. Preserve the Decision. Prove the Difference.
 *
 * Architecture: Clean Panoramic UI with RoadGuard Top Navigation, Zero Horizontal Overflow,
 * Mint/Teal Palette, Crisp Card Borders, and Dual-Harness Assurance Replay.
 */

import { useState, useEffect } from 'react'
import {
  ShieldCheck,
  Activity,
  FileCheck2,
  Layers,
  Sliders,
  ShieldAlert,
  Award,
  Search,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ChevronRight,
  Folder,
  Sparkles,
  Printer,
  X,
  Play,
  Hash,
  GitBranch,
} from 'lucide-react'

// ── Types ─────────────────────────────────────────────────────────────────────

type TabKey =
  | 'dashboard'
  | 'replay'
  | 'contracts'
  | 'blast_radius'
  | 'whatif'
  | 'risk'
  | 'report'

interface ReplayScenario {
  id: string
  scenario_number: number
  scenario_id: string
  scenario_name: string
  scenario_category: string
  legacy_decision: string
  modern_decision: string
  comparison_status: 'PRESERVED' | 'BEHAVIOR_DRIFT'
  drift_type: string
  drift_details?: string
  root_cause_explanation?: string
  legacy_execution_time_ms: number
  modern_execution_time_ms: number
  reviewed: boolean
}

interface ContractSpec {
  id: string
  contract_id: string
  name: string
  rule_id: string
  status: 'ACTIVE' | 'AUDITED'
  is_critical: boolean
  conditions: string[]
  inputs: Record<string, string>
  expected_decision: string
  version: string
}

interface BlastNode {
  id: string
  label: string
  layer: 'Code Layer' | 'Business Logic Layer' | 'Behavioral Replay Layer'
  type: string
  risk: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
  relationships: string[]
}

// ── Mock Data for Instant Interactive Experience ─────────────────────────────

const MOCK_REPLAY_SCENARIOS: ReplayScenario[] = [
  {
    id: 'sc-1',
    scenario_number: 1,
    scenario_id: 'SC-FEE-001',
    scenario_name: 'Standard Retail Account Domestic Wire Under $10,000',
    scenario_category: 'FEE_CALCULATION',
    legacy_decision: 'FEE_ASSESSED: $15.00',
    modern_decision: 'FEE_ASSESSED: $15.00',
    comparison_status: 'PRESERVED',
    drift_type: 'NONE',
    legacy_execution_time_ms: 12,
    modern_execution_time_ms: 2,
    reviewed: true,
  },
  {
    id: 'sc-2',
    scenario_number: 2,
    scenario_id: 'SC-FEE-002',
    scenario_name: 'High-Volume Commercial Wire With Currency Conversion',
    scenario_category: 'FEE_CALCULATION',
    legacy_decision: 'FEE_ASSESSED: $42.50',
    modern_decision: 'FEE_ASSESSED: $40.00',
    comparison_status: 'BEHAVIOR_DRIFT',
    drift_type: 'ROUNDING_PRECISION_DRIFT',
    drift_details: 'Modern service dropped legacy bank 4-decimal banker rounding in favor of IEEE-754 standard 2-decimal trunc.',
    root_cause_explanation: 'Legacy Java TransferFeeService used BigDecimal.ROUND_HALF_EVEN; modern microservice converted to native Go float64.',
    legacy_execution_time_ms: 18,
    modern_execution_time_ms: 3,
    reviewed: false,
  },
  {
    id: 'sc-3',
    scenario_number: 3,
    scenario_id: 'SC-LMT-003',
    scenario_name: 'Cumulative Daily Velocity Limit Exceeded at 23:59:50 UTC',
    scenario_category: 'LIMIT_CHECK',
    legacy_decision: 'TRANSACTION_REJECTED: VELOCITY_CAP',
    modern_decision: 'TRANSACTION_REJECTED: VELOCITY_CAP',
    comparison_status: 'PRESERVED',
    drift_type: 'NONE',
    legacy_execution_time_ms: 9,
    modern_execution_time_ms: 1,
    reviewed: true,
  },
  {
    id: 'sc-4',
    scenario_number: 4,
    scenario_id: 'SC-KYC-004',
    scenario_name: 'Cross-Border Transfer to FATF Monitored Jurisdiction',
    scenario_category: 'COMPLIANCE',
    legacy_decision: 'MANUAL_COMPLIANCE_HOLD',
    modern_decision: 'AUTO_PROCEED_LOW_RISK',
    comparison_status: 'BEHAVIOR_DRIFT',
    drift_type: 'REGULATORY_POLICY_BYPASS',
    drift_details: 'Modern decision rule omitted jurisdiction ISO-3166 code lookup fallback when state-level code was missing.',
    root_cause_explanation: 'Legacy system evaluated CountryRiskProfile.java fallback condition; modern REST gateway skipped null checking in DTO.',
    legacy_execution_time_ms: 24,
    modern_execution_time_ms: 4,
    reviewed: false,
  },
  {
    id: 'sc-5',
    scenario_number: 5,
    scenario_id: 'SC-FRAUD-005',
    scenario_name: 'Structuring Anomaly (3 Identical Transfers within 120s)',
    scenario_category: 'FRAUD_DETECTION',
    legacy_decision: 'SECURITY_ALERT_HOLD',
    modern_decision: 'SECURITY_ALERT_HOLD',
    comparison_status: 'PRESERVED',
    drift_type: 'NONE',
    legacy_execution_time_ms: 15,
    modern_execution_time_ms: 2,
    reviewed: true,
  },
  {
    id: 'sc-6',
    scenario_number: 6,
    scenario_id: 'SC-OVER-006',
    scenario_name: 'Prime Corporate Account Grace Period Overdraft',
    scenario_category: 'CREDIT_DECISION',
    legacy_decision: 'OVERDRAFT_APPROVED_WITH_SURCHARGE',
    modern_decision: 'OVERDRAFT_HARD_DECLINED',
    comparison_status: 'BEHAVIOR_DRIFT',
    drift_type: 'CREDIT_POLICY_STRICTNESS_DRIFT',
    drift_details: 'Prime tier tier-override logic from legacy customer classification matrix was not ported to modern rule engine.',
    root_cause_explanation: 'Legacy COBOL/Java bridge had CustomerTier.PRIME VIP bypass flag hardcoded in legacy AccountManager.java.',
    legacy_execution_time_ms: 31,
    modern_execution_time_ms: 5,
    reviewed: false,
  },
  {
    id: 'sc-7',
    scenario_number: 7,
    scenario_id: 'SC-TAX-007',
    scenario_name: 'Withholding Tax Assessment for Non-Resident Alien Account',
    scenario_category: 'TAX_ACCOUNTING',
    legacy_decision: 'TAX_WITHHELD: 30.00%',
    modern_decision: 'TAX_WITHHELD: 30.00%',
    comparison_status: 'PRESERVED',
    drift_type: 'NONE',
    legacy_execution_time_ms: 14,
    modern_execution_time_ms: 2,
    reviewed: true,
  },
  {
    id: 'sc-8',
    scenario_number: 8,
    scenario_id: 'SC-SETTLE-008',
    scenario_name: 'End-of-Day Ledger Clearing and Interbank Reconciliation',
    scenario_category: 'CLEARING',
    legacy_decision: 'BATCH_RECONCILED_SUCCESS',
    modern_decision: 'BATCH_RECONCILED_SUCCESS',
    comparison_status: 'PRESERVED',
    drift_type: 'NONE',
    legacy_execution_time_ms: 45,
    modern_execution_time_ms: 8,
    reviewed: true,
  },
]

const MOCK_CONTRACTS: ContractSpec[] = [
  {
    id: '1',
    contract_id: 'DC-FEE-001',
    name: 'Tiered Transfer Fee Calculation Invariant',
    rule_id: 'BR-FEE-001',
    status: 'AUDITED',
    is_critical: true,
    conditions: [
      'AccountTier == "STANDARD" && Amount <= 10000 => Fee == $15.00',
      'AccountTier == "COMMERCIAL" => Rounding strictly 4-decimal precision',
      'Weekend Surcharge applied if UTC hour < 06:00 on Monday',
    ],
    inputs: { accountTier: 'STANDARD', amount: '8500.00', currency: 'USD' },
    expected_decision: 'FEE_ASSESSED: $15.00',
    version: '2.1.0',
  },
  {
    id: '2',
    contract_id: 'DC-LMT-002',
    name: 'Daily Transaction Velocity & Cumulative Ceiling',
    rule_id: 'BR-LMT-002',
    status: 'ACTIVE',
    is_critical: true,
    conditions: [
      'Rolling 24hr window sum <= $50,000 for unverified accounts',
      'Reject immediately with code VELOCITY_CAP without debiting fees',
    ],
    inputs: { accountId: 'ACC-8921', rollingSum: '51200.00', limit: '50000.00' },
    expected_decision: 'TRANSACTION_REJECTED: VELOCITY_CAP',
    version: '1.4.2',
  },
  {
    id: '3',
    contract_id: 'DC-KYC-003',
    name: 'High-Risk Jurisdiction Compliance Quarantine',
    rule_id: 'BR-KYC-003',
    status: 'AUDITED',
    is_critical: true,
    conditions: [
      'CountryCode in FATF_GREY_LIST requires mandatory 4-eye audit hold',
      'Fallback to state-level code lookup if country code ISO is empty',
    ],
    inputs: { countryCode: 'IR', entityType: 'NON_RESIDENT' },
    expected_decision: 'MANUAL_COMPLIANCE_HOLD',
    version: '3.0.1',
  },
  {
    id: '4',
    contract_id: 'DC-FRAUD-004',
    name: 'Multi-Leg Rapid Structuring Anomaly Freeze',
    rule_id: 'BR-FRAUD-004',
    status: 'AUDITED',
    is_critical: false,
    conditions: [
      'Transfers >= 3 within 120 seconds with amount variation <= 5%',
      'Emit SAR alert event to Compliance Ledger',
    ],
    inputs: { accountId: 'ACC-3141', transferCountInWindow: '3', deltaAmount: '12.00' },
    expected_decision: 'SECURITY_ALERT_HOLD',
    version: '1.8.0',
  },
  {
    id: '5',
    contract_id: 'DC-OVER-005',
    name: 'Prime Account Auto-Overdraft Decision',
    rule_id: 'BR-OVER-005',
    status: 'ACTIVE',
    is_critical: false,
    conditions: [
      'CustomerTier == "PRIME" allows overdraft balance up to -$5,000.00',
      'Assess 2.5% surcharge instead of hard transaction decline',
    ],
    inputs: { accountTier: 'PRIME', currentBalance: '-1200.00', requestedDebit: '800.00' },
    expected_decision: 'OVERDRAFT_APPROVED_WITH_SURCHARGE',
    version: '2.0.0',
  },
  {
    id: '6',
    contract_id: 'DC-TAX-006',
    name: 'Non-Resident Alien Statutory Withholding Tax',
    rule_id: 'BR-TAX-006',
    status: 'AUDITED',
    is_critical: true,
    conditions: [
      'TaxStatus == "W8BEN_ABSENT" requires flat 30.00% withholding on gross yield',
      'Zero rounding deduction allowed',
    ],
    inputs: { taxStatus: 'W8BEN_ABSENT', grossYield: '1000.00' },
    expected_decision: 'TAX_WITHHELD: 30.00%',
    version: '1.2.0',
  },
  {
    id: '7',
    contract_id: 'DC-SETTLE-007',
    name: 'End-of-Day Interbank Reconciliation Balance',
    rule_id: 'BR-SETTLE-007',
    status: 'AUDITED',
    is_critical: true,
    conditions: [
      'Debit total == Credit total across all ledger sub-accounts',
      'Discrepancy tolerance: $0.0000',
    ],
    inputs: { debitSum: '12495021.40', creditSum: '12495021.40' },
    expected_decision: 'BATCH_RECONCILED_SUCCESS',
    version: '4.1.0',
  },
]

const MOCK_NODES: BlastNode[] = [
  {
    id: 'NODE-1',
    label: 'TransferDomainService.java',
    layer: 'Code Layer',
    type: 'Java Service Class',
    risk: 'CRITICAL',
    relationships: ['BR-FEE-001 (Implements)', 'SC-FEE-002 (Replayed By)'],
  },
  {
    id: 'NODE-2',
    label: 'AccountManager.java',
    layer: 'Code Layer',
    type: 'Java Controller Entity',
    risk: 'HIGH',
    relationships: ['BR-OVER-005 (Implements)', 'SC-OVER-006 (Replayed By)'],
  },
  {
    id: 'NODE-3',
    label: 'CountryRiskProfile.java',
    layer: 'Code Layer',
    type: 'Java Compliance Entity',
    risk: 'CRITICAL',
    relationships: ['BR-KYC-003 (Implements)', 'SC-KYC-004 (Replayed By)'],
  },
  {
    id: 'NODE-4',
    label: 'BR-FEE-001 (Tiered Fee Matrix)',
    layer: 'Business Logic Layer',
    type: 'Extracted Rule DNA',
    risk: 'HIGH',
    relationships: ['TransferDomainService.java', 'DC-FEE-001 (Contract)', 'SC-FEE-002'],
  },
  {
    id: 'NODE-5',
    label: 'BR-KYC-003 (FATF Compliance Lock)',
    layer: 'Business Logic Layer',
    type: 'Extracted Rule DNA',
    risk: 'CRITICAL',
    relationships: ['CountryRiskProfile.java', 'DC-KYC-003 (Contract)', 'SC-KYC-004'],
  },
  {
    id: 'NODE-6',
    label: 'BR-OVER-005 (Prime VIP Overdraft)',
    layer: 'Business Logic Layer',
    type: 'Extracted Rule DNA',
    risk: 'MEDIUM',
    relationships: ['AccountManager.java', 'DC-OVER-005 (Contract)', 'SC-OVER-006'],
  },
  {
    id: 'NODE-7',
    label: 'SC-FEE-002 (Precision Drift Scenario)',
    layer: 'Behavioral Replay Layer',
    type: 'Dual-Harness Execution Test',
    risk: 'HIGH',
    relationships: ['BR-FEE-001', 'TransferDomainService.java'],
  },
  {
    id: 'NODE-8',
    label: 'SC-KYC-004 (Jurisdiction Policy Bypass)',
    layer: 'Behavioral Replay Layer',
    type: 'Dual-Harness Execution Test',
    risk: 'CRITICAL',
    relationships: ['BR-KYC-003', 'CountryRiskProfile.java'],
  },
  {
    id: 'NODE-9',
    label: 'SC-OVER-006 (Prime Account Hard Decline)',
    layer: 'Behavioral Replay Layer',
    type: 'Dual-Harness Execution Test',
    risk: 'MEDIUM',
    relationships: ['BR-OVER-005', 'AccountManager.java'],
  },
]

// ── Main App Component ─────────────────────────────────────────────────────────

export default function App() {
  const [activeTab, setActiveTab] = useState<TabKey>('dashboard')
  const [searchOpen, setSearchOpen] = useState(false)
  const [replays] = useState<ReplayScenario[]>(MOCK_REPLAY_SCENARIOS)
  const [replayFilter, setReplayFilter] = useState<'ALL' | 'PRESERVED' | 'DRIFT'>('ALL')
  const [investigatingScenario, setInvestigatingScenario] = useState<ReplayScenario | null>(null)

  // What-If Simulator state
  const [feeThreshold, setFeeThreshold] = useState<number>(10000)
  const [overdraftCap, setOverdraftCap] = useState<number>(5000)
  const [simulationRun, setSimulationRun] = useState(false)

  // Contracts state
  const [selectedContract, setSelectedContract] = useState<ContractSpec>(MOCK_CONTRACTS[0])

  // Blast Radius state
  const [selectedNode, setSelectedNode] = useState<BlastNode>(MOCK_NODES[0])
  const [nodeLayerFilter, setNodeLayerFilter] = useState<string>('ALL')

  // Keyboard shortcut Ctrl+K for search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setSearchOpen((prev) => !prev)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const filteredReplays = replays.filter((r) => {
    if (replayFilter === 'PRESERVED') return r.comparison_status === 'PRESERVED'
    if (replayFilter === 'DRIFT') return r.comparison_status === 'BEHAVIOR_DRIFT'
    return true
  })

  const preservedCount = replays.filter((r) => r.comparison_status === 'PRESERVED').length
  const driftCount = replays.filter((r) => r.comparison_status === 'BEHAVIOR_DRIFT').length

  const handleRunReplay = () => {
    // Quick demonstration replay animation
    alert('Decision Replay Lab re-executed: 8 scenarios validated against dual-harness. 5 Preserved, 3 Silent Drift Detected.')
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* ── Top Header Navigation Bar (Clean Linear / Stripe Style) ─────── */}
      <header
        style={{
          height: '54px',
          width: '100%',
          backgroundColor: '#ffffff',
          borderBottom: '1px solid #e2e8f0',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px',
          position: 'sticky',
          top: 0,
          zIndex: 40,
          boxShadow: '0 1px 2px rgba(0, 0, 0, 0.03)',
        }}
      >
        {/* Left: Brand Identity */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
          <button
            onClick={() => setActiveTab('dashboard')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: 0,
            }}
          >
            <div
              style={{
                width: '28px',
                height: '28px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #0c645d 0%, #14877e 100%)',
                color: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 2px 4px rgba(12, 100, 93, 0.2)',
              }}
            >
              <ShieldCheck size={16} color="#ffffff" />
            </div>
            <span style={{ fontWeight: 800, fontSize: '15px', letterSpacing: '-0.02em', color: '#0b2321' }}>
              LEGACY<span style={{ color: '#0c645d' }}>X</span>
            </span>
          </button>
        </div>

        {/* Center: Clean Horizontal Navigation Tabs (Single line, no wrap, no noisy badges) */}
        <nav
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            flexShrink: 0,
            justifyContent: 'center',
          }}
        >
          <button
            className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>

          <button
            className={`nav-tab ${activeTab === 'replay' ? 'active' : ''}`}
            onClick={() => setActiveTab('replay')}
          >
            Replay Lab
          </button>

          <button
            className={`nav-tab ${activeTab === 'contracts' ? 'active' : ''}`}
            onClick={() => setActiveTab('contracts')}
          >
            Contracts
          </button>

          <button
            className={`nav-tab ${activeTab === 'blast_radius' ? 'active' : ''}`}
            onClick={() => setActiveTab('blast_radius')}
          >
            Blast Radius
          </button>

          <button
            className={`nav-tab ${activeTab === 'whatif' ? 'active' : ''}`}
            onClick={() => setActiveTab('whatif')}
          >
            What-If Lab
          </button>

          <button
            className={`nav-tab ${activeTab === 'risk' ? 'active' : ''}`}
            onClick={() => setActiveTab('risk')}
          >
            Risk Scorecard
          </button>

          <button
            className={`nav-tab ${activeTab === 'report' ? 'active' : ''}`}
            onClick={() => setActiveTab('report')}
          >
            Sign-Off Report
          </button>
        </nav>

        {/* Right: Quick Search, Verified Status, Profile */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>
          <button
            onClick={() => setSearchOpen(true)}
            title="Search specifications & business rules (Ctrl+K)"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '5px 10px',
              borderRadius: '6px',
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              fontSize: '12px',
              color: '#64748b',
              cursor: 'pointer',
            }}
          >
            <Search size={13} color="#94a3b8" />
            <span style={{ fontSize: '11px', fontWeight: 600 }}>Search</span>
            <kbd
              style={{
                fontSize: '9px',
                fontWeight: 700,
                padding: '1px 4px',
                backgroundColor: '#ffffff',
                border: '1px solid #cbd5e1',
                borderRadius: '4px',
                color: '#64748b',
              }}
            >
              ⌘K
            </kbd>
          </button>

          <div
            title="Deterministic Verification Engine is Active"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              padding: '4px 8px',
              borderRadius: '6px',
              backgroundColor: '#ecfdf5',
              border: '1px solid #a7f3d0',
              color: '#065f46',
              fontSize: '11px',
              fontWeight: 700,
            }}
          >
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#10b981' }} />
            <span>Verified</span>
          </div>

          <div
            title="Sarvesh K — Lead Auditor"
            style={{
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              backgroundColor: '#0c645d',
              color: '#ffffff',
              fontWeight: 800,
              fontSize: '11px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
            }}
          >
            SK
          </div>
        </div>
      </header>

      {/* ── Panoramic Main Canvas ─────────────────────────────────────────── */}
      <main className="panoramic-canvas">
        {/* VIEW 1: DASHBOARD OVERVIEW */}
        {activeTab === 'dashboard' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Hero Welcome Banner */}
            <div className="card-luxury" style={{ padding: '28px 32px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px', marginBottom: '14px' }}>
                <span className="pill-badge">
                  <ShieldCheck size={14} />
                  LEGACYX 2.0 • Modernization Assurance Platform
                </span>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <button className="btn-secondary" onClick={() => setActiveTab('contracts')}>
                    <FileCheck2 size={15} />
                    <span>View Decision Contracts</span>
                  </button>
                  <button className="btn-primary" onClick={() => setActiveTab('replay')}>
                    <Activity size={15} />
                    <span>Launch Replay Lab</span>
                  </button>
                </div>
              </div>

              <h1 style={{ fontSize: '28px', fontWeight: 900, color: '#0b2321', letterSpacing: '-0.03em', lineHeight: 1.25, maxWidth: '800px', marginBottom: '8px' }}>
                Modernize the Code.{' '}
                <span style={{ color: '#0c645d' }}>Preserve the Decision.</span>{' '}
                <span style={{ color: '#14877e' }}>Prove the Difference.</span>
              </h1>

              <p style={{ fontSize: '13.5px', color: '#475569', lineHeight: 1.6, maxWidth: '840px' }}>
                Legacy modernization fails when systems silently alter critical business decisions.
                LegacyX delivers mathematical and execution proof: Rule DNA extraction, Decision Contracts,
                Dual-Harness Replay, and Root-Cause Silent Drift Detection.
              </p>
            </div>

            {/* 4 Key Modernization Assurance Metrics */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
              <div className="card-clean" style={{ padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: '#e6f5f3', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Folder size={20} color="#0c645d" />
                  </div>
                  <span className="pill-badge" style={{ fontSize: '10px' }}>Active Core</span>
                </div>
                <div style={{ fontSize: '28px', fontWeight: 900, color: '#0b2321', letterSpacing: '-0.02em', marginBottom: '4px' }}>
                  LegacyBank Core
                </div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#334155' }}>Enterprise Banking Repository</div>
                <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>Java EE, Spring 3, Oracle PL/SQL</div>
              </div>

              <div className="card-clean" style={{ padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: '#e6f5f3', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <FileCheck2 size={20} color="#0c645d" />
                  </div>
                  <span className="pill-badge" style={{ fontSize: '10px' }}>Synthesized</span>
                </div>
                <div style={{ fontSize: '28px', fontWeight: 900, color: '#0b2321', letterSpacing: '-0.02em', marginBottom: '4px' }}>
                  7 Contracts
                </div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#334155' }}>Decision Contract Specifications</div>
                <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>Language-agnostic business rules</div>
              </div>

              <div className="card-clean" style={{ padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: '#fff1f2', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Activity size={20} color="#e11d48" />
                  </div>
                  <span style={{ fontSize: '10px', fontWeight: 800, padding: '2px 8px', borderRadius: '999px', background: '#fee2e2', color: '#991b1b' }}>
                    3 Drifts Isolated
                  </span>
                </div>
                <div style={{ fontSize: '28px', fontWeight: 900, color: '#0b2321', letterSpacing: '-0.02em', marginBottom: '4px' }}>
                  5 / 8 Preserved
                </div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#334155' }}>Dual-Harness Execution Parity</div>
                <div style={{ fontSize: '11px', color: '#e11d48', fontWeight: 600, marginTop: '2px' }}>Root causes identified and pinned</div>
              </div>

              <div className="card-clean" style={{ padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: '#ecfdf5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Award size={20} color="#059669" />
                  </div>
                  <span style={{ fontSize: '10px', fontWeight: 800, padding: '2px 8px', borderRadius: '999px', background: '#d1fae5', color: '#065f46' }}>
                    ISO Verified
                  </span>
                </div>
                <div style={{ fontSize: '28px', fontWeight: 900, color: '#0b2321', letterSpacing: '-0.02em', marginBottom: '4px' }}>
                  SHA-256 Sealed
                </div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#334155' }}>Assurance Certificate Seal</div>
                <div style={{ fontSize: '11px', color: '#059669', fontWeight: 600, marginTop: '2px' }}>Audit hash tree cryptographically verified</div>
              </div>
            </div>

            {/* Featured Active Modernization Workspace Card */}
            <div className="card-clean" style={{ padding: '28px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #cbe6e3', paddingBottom: '18px', marginBottom: '20px', flexWrap: 'wrap', gap: '14px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span className="pill-badge" style={{ fontSize: '10px' }}>
                      FEATURED ACTIVE WORKSPACE
                    </span>
                    <span style={{ fontSize: '11px', fontFamily: 'monospace', color: '#64748b' }}>
                      ID: d1436de1-b225-4516-93b5-a84b73c3b81c
                    </span>
                  </div>
                  <h2 style={{ fontSize: '20px', fontWeight: 900, color: '#0b2321' }}>
                    LegacyBank Enterprise Core Banking Ledger
                  </h2>
                  <p style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
                    Primary transactional ledger, wire fees, KYC rules, and high-velocity credit processing.
                  </p>
                </div>

                <button className="btn-primary" onClick={() => setActiveTab('replay')}>
                  <span>Enter Replay Lab</span>
                  <ArrowRight size={14} />
                </button>
              </div>

              {/* Quick Navigation Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                {[
                  { title: 'Decision Replay Lab', desc: '8 Dual-Harness Scenarios', tab: 'replay', icon: Activity, color: '#0c645d' },
                  { title: 'Decision Contracts', desc: '7 Invariant Specifications', tab: 'contracts', icon: FileCheck2, color: '#1d4ed8' },
                  { title: '3-Layer Blast Radius', desc: '9 Cross-Layer Nodes', tab: 'blast_radius', icon: Layers, color: '#0f766e' },
                  { title: 'What-If Simulator', desc: 'Parameter Drift Modeling', tab: 'whatif', icon: Sliders, color: '#b45309' },
                  { title: 'Assurance Report', desc: 'Cryptographic Sign-Off', tab: 'report', icon: Award, color: '#047857' },
                ].map((item) => {
                  const Icon = item.icon
                  return (
                    <button
                      key={item.title}
                      onClick={() => setActiveTab(item.tab as TabKey)}
                      style={{
                        padding: '16px',
                        borderRadius: '16px',
                        border: '1px solid #cbe6e3',
                        background: '#ffffff',
                        textAlign: 'left',
                        cursor: 'pointer',
                        transition: 'all 160ms ease',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = '#0c645d'
                        e.currentTarget.style.backgroundColor = '#f0f8f7'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = '#cbe6e3'
                        e.currentTarget.style.backgroundColor = '#ffffff'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <div style={{ width: '28px', height: '28px', borderRadius: '8px', background: '#e6f5f3', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <Icon size={16} color={item.color} />
                        </div>
                        <ChevronRight size={14} color="#94a3b8" />
                      </div>
                      <div style={{ fontSize: '13px', fontWeight: 800, color: '#0b2321' }}>{item.title}</div>
                      <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>{item.desc}</div>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* 9-Stage Modernization Pipeline Stepper */}
            <div className="card-clean" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Sparkles size={16} color="#0c645d" />
                  <span style={{ fontSize: '12px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.04em', color: '#0b2321' }}>
                    Deterministic Modernization Pipeline
                  </span>
                </div>
                <span className="tag-mono" style={{ color: '#64748b' }}>
                  DISCOVER → DECIDE → REPLAY → PROVE
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '10px' }}>
                {[
                  { n: 1, name: 'Ingestion', sub: 'AST Indexing' },
                  { n: 2, name: 'System X-Ray', sub: 'Call Graphs' },
                  { n: 3, name: 'Rule DNA', sub: 'Constraints' },
                  { n: 4, name: 'Contracts', sub: 'Invariants' },
                  { n: 5, name: 'Replay Lab', sub: 'Dual-Harness' },
                  { n: 6, name: 'Blast Radius', sub: 'Cross-Impact' },
                  { n: 7, name: 'What-If', sub: 'Simulation' },
                  { n: 8, name: 'Transform', sub: 'Sandbox Code' },
                  { n: 9, name: 'Sign-Off', sub: 'SHA-256 Seal' },
                ].map((st) => (
                  <div
                    key={st.n}
                    style={{
                      padding: '12px',
                      borderRadius: '12px',
                      border: '1px solid #cbe6e3',
                      background: '#f4fbfb',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '4px',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ width: '20px', height: '20px', borderRadius: '50%', background: '#ffffff', border: '1px solid #a8ded7', fontSize: '10px', fontWeight: 800, color: '#0c645d', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {st.n}
                      </span>
                      <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981' }} />
                    </div>
                    <span style={{ fontSize: '12px', fontWeight: 800, color: '#0b2321', marginTop: '4px' }}>{st.name}</span>
                    <span style={{ fontSize: '10px', color: '#64748b' }}>{st.sub}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* VIEW 2: DECISION REPLAY LAB */}
        {activeTab === 'replay' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px', borderBottom: '1px solid #cbe6e3', paddingBottom: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span className="pill-badge">DUAL-HARNESS EXECUTION REPLAY</span>
                  <span style={{ fontSize: '11px', color: '#64748b', fontFamily: 'monospace' }}>Legacy Engine vs Modern Service</span>
                </div>
                <h2 style={{ fontSize: '22px', fontWeight: 900, color: '#0b2321' }}>
                  Decision Replay Lab & Silent Drift Detection
                </h2>
                <p style={{ fontSize: '12.5px', color: '#64748b', marginTop: '2px', maxWidth: '780px' }}>
                  Executes production transaction payloads simultaneously through legacy Java byte-code and modernized microservices.
                  Detects precision shifts, boundary drifts, and regulatory oversights that pass standard unit tests.
                </p>
              </div>

              <button className="btn-primary" onClick={handleRunReplay}>
                <Play size={14} fill="#ffffff" />
                <span>Run Decision Replay</span>
              </button>
            </div>

            {/* Scoreboard Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
              <div className="card-clean" style={{ padding: '16px' }}>
                <div className="tag-mono" style={{ color: '#64748b', marginBottom: '4px' }}>SCENARIOS REPLAYED</div>
                <div style={{ fontSize: '26px', fontWeight: 900, color: '#0b2321' }}>{replays.length}</div>
                <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>100% Deterministic</div>
              </div>

              <div className="card-clean" style={{ padding: '16px', background: '#ecfdf5', borderColor: '#a7f3d0' }}>
                <div className="tag-mono" style={{ color: '#065f46', marginBottom: '4px' }}>DECISIONS PRESERVED</div>
                <div style={{ fontSize: '26px', fontWeight: 900, color: '#047857' }}>{preservedCount}</div>
                <div style={{ fontSize: '11px', color: '#065f46', fontWeight: 700, marginTop: '2px' }}>
                  {Math.round((preservedCount / replays.length) * 100)}% Decision Parity
                </div>
              </div>

              <div className="card-clean" style={{ padding: '16px', background: '#fff1f2', borderColor: '#fecdd3' }}>
                <div className="tag-mono" style={{ color: '#9f1239', marginBottom: '4px' }}>SILENT DRIFT DETECTED</div>
                <div style={{ fontSize: '26px', fontWeight: 900, color: '#be123c' }}>{driftCount}</div>
                <div style={{ fontSize: '11px', color: '#9f1239', fontWeight: 700, marginTop: '2px' }}>
                  Root-Cause Isolated
                </div>
              </div>

              <div className="card-clean" style={{ padding: '16px', background: '#fffbeb', borderColor: '#fde68a' }}>
                <div className="tag-mono" style={{ color: '#92400e', marginBottom: '4px' }}>INCONCLUSIVE / EDGE</div>
                <div style={{ fontSize: '26px', fontWeight: 900, color: '#b45309' }}>0</div>
                <div style={{ fontSize: '11px', color: '#92400e', marginTop: '2px' }}>Clean Coverage</div>
              </div>

              <div className="card-clean" style={{ padding: '16px', background: '#e6f5f3', borderColor: '#a8ded7' }}>
                <div className="tag-mono" style={{ color: '#0c645d', marginBottom: '4px' }}>MODERNIZATION RISK</div>
                <div style={{ fontSize: '22px', fontWeight: 900, color: '#0c645d' }}>ELEVATED (58.2)</div>
                <div style={{ fontSize: '11px', color: '#0c645d', fontWeight: 700, marginTop: '2px' }}>
                  Auditor Sign-Off Required
                </div>
              </div>
            </div>

            {/* Filter Pills */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <button
                className={`pill-button ${replayFilter === 'ALL' ? 'active' : ''}`}
                onClick={() => setReplayFilter('ALL')}
              >
                All Scenarios ({replays.length})
              </button>
              <button
                className={`pill-button ${replayFilter === 'PRESERVED' ? 'active' : ''}`}
                onClick={() => setReplayFilter('PRESERVED')}
              >
                <CheckCircle2 size={13} />
                <span>Preserved ({preservedCount})</span>
              </button>
              <button
                className={`pill-button ${replayFilter === 'DRIFT' ? 'active' : ''}`}
                onClick={() => setReplayFilter('DRIFT')}
              >
                <AlertTriangle size={13} />
                <span>Silent Drift ({driftCount})</span>
              </button>
            </div>

            {/* Scenarios List Cards */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {filteredReplays.map((sc) => {
                const isDrift = sc.comparison_status === 'BEHAVIOR_DRIFT'
                return (
                  <div
                    key={sc.id}
                    className="card-clean"
                    style={{
                      padding: '18px 20px',
                      borderColor: isDrift ? '#fda4af' : '#cbe6e3',
                      backgroundColor: isDrift ? '#fffbfb' : '#ffffff',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px', flexWrap: 'wrap' }}>
                      {/* Scenario Meta */}
                      <div style={{ flex: '1 1 340px', minWidth: '280px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                          <span style={{ fontSize: '11px', fontFamily: 'monospace', fontWeight: 800, padding: '2px 6px', background: '#f1f5f9', borderRadius: '4px', color: '#334155' }}>
                            #{sc.scenario_number}
                          </span>
                          <span style={{ fontSize: '11px', fontFamily: 'monospace', color: '#64748b' }}>{sc.scenario_id}</span>
                          <span className="pill-badge" style={{ fontSize: '9px', padding: '2px 6px' }}>{sc.scenario_category}</span>
                          {sc.drift_type !== 'NONE' && (
                            <span style={{ fontSize: '9px', fontWeight: 800, padding: '2px 6px', borderRadius: '999px', background: '#fef3c7', color: '#92400e', border: '1px solid #fde68a' }}>
                              {sc.drift_type}
                            </span>
                          )}
                        </div>
                        <div style={{ fontSize: '14px', fontWeight: 800, color: '#0b2321' }}>{sc.scenario_name}</div>
                      </div>

                      {/* Decisions Comparison Side-by-Side */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>
                        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '8px 14px', textAlign: 'center', minWidth: '130px' }}>
                          <span style={{ fontSize: '9px', textTransform: 'uppercase', color: '#64748b', fontWeight: 700, display: 'block', marginBottom: '2px' }}>
                            Legacy Decision
                          </span>
                          <span style={{ fontSize: '12px', fontWeight: 800, color: '#0b2321', fontFamily: 'monospace' }}>
                            {sc.legacy_decision}
                          </span>
                        </div>

                        <ArrowRight size={14} color="#94a3b8" />

                        <div
                          style={{
                            background: isDrift ? '#ffe4e6' : '#ecfdf5',
                            border: `1px solid ${isDrift ? '#fecdd3' : '#a7f3d0'}`,
                            borderRadius: '10px',
                            padding: '8px 14px',
                            textAlign: 'center',
                            minWidth: '130px',
                          }}
                        >
                          <span style={{ fontSize: '9px', textTransform: 'uppercase', color: isDrift ? '#9f1239' : '#065f46', fontWeight: 700, display: 'block', marginBottom: '2px' }}>
                            Modern Decision
                          </span>
                          <span style={{ fontSize: '12px', fontWeight: 800, color: isDrift ? '#9f1239' : '#065f46', fontFamily: 'monospace' }}>
                            {sc.modern_decision}
                          </span>
                        </div>
                      </div>

                      {/* Status & Actions */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexShrink: 0 }}>
                        <div style={{ textAlign: 'right' }}>
                          <span
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px',
                              padding: '4px 10px',
                              borderRadius: '999px',
                              fontSize: '11px',
                              fontWeight: 800,
                              textTransform: 'uppercase',
                              background: isDrift ? '#fee2e2' : '#dcfce7',
                              color: isDrift ? '#991b1b' : '#15803d',
                              border: `1px solid ${isDrift ? '#fca5a5' : '#86efac'}`,
                            }}
                          >
                            {isDrift ? <AlertTriangle size={12} /> : <CheckCircle2 size={12} />}
                            {isDrift ? 'Drift Detected' : 'Preserved'}
                          </span>
                          <div style={{ fontSize: '10px', color: '#94a3b8', marginTop: '3px', fontFamily: 'monospace' }}>
                            {sc.legacy_execution_time_ms}ms legacy • {sc.modern_execution_time_ms}ms modern
                          </div>
                        </div>

                        <button
                          className="btn-secondary"
                          style={{ padding: '6px 12px', fontSize: '11px' }}
                          onClick={() => setInvestigatingScenario(sc)}
                        >
                          <span>Investigate</span>
                          <ChevronRight size={13} />
                        </button>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* VIEW 3: DECISION CONTRACTS */}
        {activeTab === 'contracts' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ borderBottom: '1px solid #cbe6e3', paddingBottom: '16px' }}>
              <span className="pill-badge">DECISION CONTRACT SPECIFICATIONS</span>
              <h2 style={{ fontSize: '22px', fontWeight: 900, color: '#0b2321', marginTop: '4px' }}>
                Language-Agnostic Decision Contracts (Rule DNA)
              </h2>
              <p style={{ fontSize: '12.5px', color: '#64748b', marginTop: '2px' }}>
                Extracted business decision specifications verified against AST call graphs.
                Provides a tamper-proof contract baseline that modern cloud services must satisfy.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
              {/* Left: Contracts List */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {MOCK_CONTRACTS.map((contract) => (
                  <button
                    key={contract.id}
                    onClick={() => setSelectedContract(contract)}
                    style={{
                      padding: '16px',
                      borderRadius: '16px',
                      border: `1px solid ${selectedContract.id === contract.id ? '#0c645d' : '#cbe6e3'}`,
                      background: selectedContract.id === contract.id ? '#f0f8f7' : '#ffffff',
                      textAlign: 'left',
                      cursor: 'pointer',
                      transition: 'all 160ms ease',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <span className="tag-mono" style={{ color: '#0c645d' }}>{contract.contract_id}</span>
                      <span style={{ fontSize: '10px', fontWeight: 700, padding: '2px 6px', borderRadius: '4px', background: contract.is_critical ? '#fee2e2' : '#ecfdf5', color: contract.is_critical ? '#991b1b' : '#065f46' }}>
                        {contract.is_critical ? 'ZERO DRIFT TOLERANCE' : 'STANDARD'}
                      </span>
                    </div>
                    <div style={{ fontSize: '13.5px', fontWeight: 800, color: '#0b2321' }}>{contract.name}</div>
                    <div style={{ fontSize: '11px', color: '#64748b', marginTop: '4px', fontFamily: 'monospace' }}>
                      Anchored AST Rule: {contract.rule_id}
                    </div>
                  </button>
                ))}
              </div>

              {/* Right: Detailed Specification Viewer */}
              <div className="card-clean" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #cbe6e3', paddingBottom: '14px', marginBottom: '16px' }}>
                  <div>
                    <span className="tag-mono" style={{ color: '#0c645d' }}>{selectedContract.contract_id}</span>
                    <h3 style={{ fontSize: '17px', fontWeight: 900, color: '#0b2321', marginTop: '2px' }}>
                      {selectedContract.name}
                    </h3>
                  </div>
                  <span className="pill-badge">{selectedContract.status}</span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <div>
                    <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#64748b', marginBottom: '6px' }}>
                      INVARIANT CONDITIONS SPECIFICATION
                    </div>
                    <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '12px' }}>
                      {selectedContract.conditions.map((cond, idx) => (
                        <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', fontFamily: 'monospace', color: '#0b2321', marginBottom: idx !== selectedContract.conditions.length - 1 ? '6px' : 0 }}>
                          <CheckCircle2 size={13} color="#059669" />
                          <span>{cond}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#64748b', marginBottom: '6px' }}>
                      FORMAL INPUT PARAMETERS
                    </div>
                    <pre style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '12px', fontSize: '11.5px', color: '#0b2321', overflowX: 'auto' }}>
                      {JSON.stringify(selectedContract.inputs, null, 2)}
                    </pre>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                    <div style={{ background: '#e6f5f3', border: '1px solid #a8ded7', borderRadius: '12px', padding: '12px' }}>
                      <span style={{ fontSize: '10px', textTransform: 'uppercase', fontWeight: 800, color: '#0c645d' }}>
                        EXPECTED DECISION
                      </span>
                      <div style={{ fontSize: '13px', fontWeight: 900, color: '#0b2321', fontFamily: 'monospace', marginTop: '2px' }}>
                        {selectedContract.expected_decision}
                      </div>
                    </div>

                    <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '12px' }}>
                      <span style={{ fontSize: '10px', textTransform: 'uppercase', fontWeight: 800, color: '#64748b' }}>
                        CONTRACT VERSION
                      </span>
                      <div style={{ fontSize: '13px', fontWeight: 800, color: '#0b2321', marginTop: '2px' }}>
                        v{selectedContract.version} (Verified)
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* VIEW 4: 3-LAYER BLAST RADIUS */}
        {activeTab === 'blast_radius' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ borderBottom: '1px solid #cbe6e3', paddingBottom: '16px' }}>
              <span className="pill-badge">CROSS-LAYER IMPACT GRAPH</span>
              <h2 style={{ fontSize: '22px', fontWeight: 900, color: '#0b2321', marginTop: '4px' }}>
                3-Layer Blast Radius & Cross-Boundary Impact
              </h2>
              <p style={{ fontSize: '12.5px', color: '#64748b', marginTop: '2px' }}>
                Traces changes across three distinct planes: Code AST Layer, Extracted Business Rule DNA, and Behavioral Replay Tests.
              </p>
            </div>

            {/* Layer Filter Buttons */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {['ALL', 'Code Layer', 'Business Logic Layer', 'Behavioral Replay Layer'].map((layer) => (
                <button
                  key={layer}
                  className={`pill-button ${nodeLayerFilter === layer ? 'active' : ''}`}
                  onClick={() => setNodeLayerFilter(layer)}
                >
                  {layer === 'ALL' ? 'All 3 Layers (9 Nodes)' : layer}
                </button>
              ))}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
              {/* Nodes List */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {MOCK_NODES.filter((n) => nodeLayerFilter === 'ALL' || n.layer === nodeLayerFilter).map((node) => (
                  <button
                    key={node.id}
                    onClick={() => setSelectedNode(node)}
                    style={{
                      padding: '14px 16px',
                      borderRadius: '16px',
                      border: `1px solid ${selectedNode.id === node.id ? '#0c645d' : '#cbe6e3'}`,
                      background: selectedNode.id === node.id ? '#f0f8f7' : '#ffffff',
                      textAlign: 'left',
                      cursor: 'pointer',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                      <span className="tag-mono" style={{ color: '#0c645d' }}>{node.layer}</span>
                      <span style={{ fontSize: '9px', fontWeight: 800, padding: '2px 6px', borderRadius: '4px', background: node.risk === 'CRITICAL' ? '#fee2e2' : node.risk === 'HIGH' ? '#ffedd5' : '#ecfdf5', color: node.risk === 'CRITICAL' ? '#991b1b' : node.risk === 'HIGH' ? '#9a3412' : '#065f46' }}>
                        {node.risk} RISK
                      </span>
                    </div>
                    <div style={{ fontSize: '13px', fontWeight: 800, color: '#0b2321' }}>{node.label}</div>
                    <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>{node.type}</div>
                  </button>
                ))}
              </div>

              {/* Inspector Panel */}
              <div className="card-clean" style={{ padding: '24px' }}>
                <div style={{ borderBottom: '1px solid #cbe6e3', paddingBottom: '14px', marginBottom: '16px' }}>
                  <span className="tag-mono" style={{ color: '#0c645d' }}>{selectedNode.layer} INSPECTOR</span>
                  <h3 style={{ fontSize: '18px', fontWeight: 900, color: '#0b2321', marginTop: '2px' }}>
                    {selectedNode.label}
                  </h3>
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>Type: {selectedNode.type}</div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  <div>
                    <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#64748b', display: 'block', marginBottom: '8px' }}>
                      CONNECTED GRAPH RELATIONSHIPS
                    </span>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      {selectedNode.relationships.map((rel, idx) => (
                        <div key={idx} style={{ padding: '10px 12px', borderRadius: '10px', background: '#f8fafc', border: '1px solid #e2e8f0', fontSize: '12px', fontFamily: 'monospace', color: '#0b2321', display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <GitBranch size={13} color="#0c645d" />
                          <span>{rel}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div style={{ background: '#e6f5f3', border: '1px solid #a8ded7', borderRadius: '12px', padding: '14px' }}>
                    <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#0c645d', marginBottom: '4px' }}>
                      ISOLATION AUDIT EVIDENCE
                    </div>
                    <p style={{ fontSize: '12px', color: '#0b2321', lineHeight: 1.5 }}>
                      Modifying this node propagates a blast radius of <strong>2 downstream decision scenarios</strong> and <strong>1 active decision contract</strong>.
                      Behavioral regression verification must be executed before code merges.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* VIEW 5: WHAT-IF SIMULATOR */}
        {activeTab === 'whatif' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ borderBottom: '1px solid #cbe6e3', paddingBottom: '16px' }}>
              <span className="pill-badge">POLICY MUTATION SIMULATOR</span>
              <h2 style={{ fontSize: '22px', fontWeight: 900, color: '#0b2321', marginTop: '4px' }}>
                What-If Business Rule Mutation & Policy Simulator
              </h2>
              <p style={{ fontSize: '12.5px', color: '#64748b', marginTop: '2px' }}>
                Interactively adjust business thresholds and policy values to predict silent drift rate and simulate impact before production rollout.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
              {/* Controls */}
              <div className="card-clean" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <label style={{ fontSize: '13px', fontWeight: 800, color: '#0b2321' }}>
                      Domestic Transfer Fee Threshold
                    </label>
                    <span style={{ fontSize: '13px', fontWeight: 900, color: '#0c645d', fontFamily: 'monospace' }}>
                      ${feeThreshold.toLocaleString()}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="5000"
                    max="25000"
                    step="1000"
                    value={feeThreshold}
                    onChange={(e) => {
                      setFeeThreshold(Number(e.target.value))
                      setSimulationRun(true)
                    }}
                    style={{ width: '100%', accentColor: '#0c645d' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#64748b' }}>
                    <span>$5,000 (Strict)</span>
                    <span>$25,000 (Relaxed)</span>
                  </div>
                </div>

                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <label style={{ fontSize: '13px', fontWeight: 800, color: '#0b2321' }}>
                      Prime VIP Overdraft Balance Limit
                    </label>
                    <span style={{ fontSize: '13px', fontWeight: 900, color: '#0c645d', fontFamily: 'monospace' }}>
                      ${overdraftCap.toLocaleString()}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="1000"
                    max="10000"
                    step="500"
                    value={overdraftCap}
                    onChange={(e) => {
                      setOverdraftCap(Number(e.target.value))
                      setSimulationRun(true)
                    }}
                    style={{ width: '100%', accentColor: '#0c645d' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#64748b' }}>
                    <span>$1,000</span>
                    <span>$10,000</span>
                  </div>
                </div>

                <button
                  className="btn-primary"
                  onClick={() => setSimulationRun(true)}
                  style={{ justifyContent: 'center' }}
                >
                  <Play size={14} fill="#ffffff" />
                  <span>Simulate Blast Radius Impact</span>
                </button>
              </div>

              {/* Simulation Result */}
              <div className="card-clean" style={{ padding: '24px' }}>
                <div style={{ borderBottom: '1px solid #cbe6e3', paddingBottom: '12px', marginBottom: '16px' }}>
                  <span className="tag-mono" style={{ color: '#0c645d' }}>PREDICTIVE TELEMETRY</span>
                  <h3 style={{ fontSize: '17px', fontWeight: 900, color: '#0b2321', marginTop: '2px' }}>
                    Projected Modernization Impact
                  </h3>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                  <div style={{ padding: '14px', borderRadius: '12px', background: '#f8fafc', border: '1px solid #e2e8f0' }}>
                    <span style={{ fontSize: '10px', textTransform: 'uppercase', color: '#64748b', fontWeight: 800 }}>
                      PROJECTED DRIFT SCENARIOS
                    </span>
                    <div style={{ fontSize: '24px', fontWeight: 900, color: '#e11d48', marginTop: '2px' }}>
                      {simulationRun ? '4 of 8' : '3 of 8'}
                    </div>
                  </div>

                  <div style={{ padding: '14px', borderRadius: '12px', background: '#f8fafc', border: '1px solid #e2e8f0' }}>
                    <span style={{ fontSize: '10px', textTransform: 'uppercase', color: '#64748b', fontWeight: 800 }}>
                      DRIFT RATE SHIFT
                    </span>
                    <div style={{ fontSize: '24px', fontWeight: 900, color: '#d97706', marginTop: '2px' }}>
                      {simulationRun ? '+12.5%' : '37.5%'}
                    </div>
                  </div>
                </div>

                <div style={{ background: '#e6f5f3', border: '1px solid #a8ded7', borderRadius: '12px', padding: '14px' }}>
                  <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#0c645d', display: 'block', marginBottom: '4px' }}>
                    ASSURANCE ENGINE PROJECTION
                  </span>
                  <p style={{ fontSize: '12px', color: '#0b2321', lineHeight: 1.5 }}>
                    Adjusting the domestic wire fee threshold to <strong>${feeThreshold.toLocaleString()}</strong> alters the boundary of 
                    contract <code>DC-FEE-001</code>. Transactions between $10,000 and ${feeThreshold.toLocaleString()} will shift from tier 2 to tier 1 surcharge.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* VIEW 6: RISK SCORECARD */}
        {activeTab === 'risk' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ borderBottom: '1px solid #cbe6e3', paddingBottom: '16px' }}>
              <span className="pill-badge">SAFETY & COMPLIANCE SCORECARD</span>
              <h2 style={{ fontSize: '22px', fontWeight: 900, color: '#0b2321', marginTop: '4px' }}>
                6-Dimensional Modernization Risk Scorecard
              </h2>
              <p style={{ fontSize: '12.5px', color: '#64748b', marginTop: '2px' }}>
                Multi-faceted safety index evaluating structural coupling, contract drift, regulatory risk, and test coverage.
              </p>
            </div>

            {/* Composite Score Hero */}
            <div className="card-luxury" style={{ padding: '24px 28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px' }}>
              <div>
                <span className="tag-mono" style={{ color: '#0c645d' }}>COMPOSITE MODERNIZATION RISK INDEX</span>
                <div style={{ fontSize: '38px', fontWeight: 900, color: '#0b2321', letterSpacing: '-0.03em', marginTop: '2px' }}>
                  58.2 <span style={{ fontSize: '18px', color: '#64748b', fontWeight: 600 }}>/ 100</span>
                </div>
                <div style={{ display: 'inline-block', marginTop: '4px', padding: '3px 10px', borderRadius: '999px', background: '#fef3c7', color: '#92400e', border: '1px solid #fde68a', fontSize: '11px', fontWeight: 800 }}>
                  ELEVATED MODERNIZATION RISK
                </div>
              </div>

              <div style={{ maxWidth: '440px', background: '#ffffff', border: '1px solid #cbe6e3', borderRadius: '16px', padding: '16px' }}>
                <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#64748b', display: 'block', marginBottom: '6px' }}>
                  Auditor Recommendations:
                </span>
                <ul style={{ fontSize: '12px', color: '#0b2321', paddingLeft: '18px', lineHeight: 1.5 }}>
                  <li>Resolve BigDecimal rounding precision mismatch in TransferFeeService.</li>
                  <li>Re-introduce ISO-3166 jurisdiction fallback in KYC compliance gateway.</li>
                  <li>Restore Prime Account VIP bypass condition in AccountManager.</li>
                </ul>
              </div>
            </div>

            {/* 6 Dimensions Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
              {[
                { name: 'Decision Contract Drift', score: 68, risk: 'HIGH', desc: '3 of 8 critical scenarios exhibit decision variance' },
                { name: 'AST Structural Coupling', score: 72, risk: 'HIGH', desc: 'Direct circular dependencies in legacy TransferService' },
                { name: 'Business Rule Complexity', score: 55, risk: 'MEDIUM', desc: 'Average cyclomatic complexity 14.2 across core ledger' },
                { name: 'Regulatory Compliance Lock', score: 35, risk: 'LOW', desc: 'Sanctions and tax rules are isolated in discrete modules' },
                { name: 'Behavioral Test Parity', score: 45, risk: 'MEDIUM', desc: 'Dual-harness covers 89.4% of execution branches' },
                { name: 'Subprocess Build Stability', score: 74, risk: 'HIGH', desc: 'Clean compile in isolated container with zero regressions' },
              ].map((dim) => (
                <div key={dim.name} className="card-clean" style={{ padding: '18px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: '12px', fontWeight: 800, color: '#0b2321' }}>{dim.name}</span>
                    <span style={{ fontSize: '10px', fontWeight: 800, padding: '2px 6px', borderRadius: '4px', background: dim.risk === 'HIGH' ? '#fee2e2' : dim.risk === 'MEDIUM' ? '#ffedd5' : '#ecfdf5', color: dim.risk === 'HIGH' ? '#991b1b' : dim.risk === 'MEDIUM' ? '#9a3412' : '#065f46' }}>
                      {dim.risk}
                    </span>
                  </div>
                  <div style={{ fontSize: '22px', fontWeight: 900, color: '#0b2321', fontFamily: 'monospace' }}>
                    {dim.score} <span style={{ fontSize: '12px', color: '#64748b', fontWeight: 600 }}>/ 100</span>
                  </div>
                  <p style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>{dim.desc}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* VIEW 7: ASSURANCE REPORT */}
        {activeTab === 'report' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px', borderBottom: '1px solid #cbe6e3', paddingBottom: '16px' }}>
              <div>
                <span className="pill-badge">CRYPTOGRAPHIC AUDIT CERTIFICATE</span>
                <h2 style={{ fontSize: '22px', fontWeight: 900, color: '#0b2321', marginTop: '4px' }}>
                  Executive Modernization Assurance Certificate
                </h2>
                <p style={{ fontSize: '12.5px', color: '#64748b', marginTop: '2px' }}>
                  Cryptographically sealed audit trail proving dual-harness decision preservation.
                </p>
              </div>

              <button className="btn-primary" onClick={() => window.print()}>
                <Printer size={14} />
                <span>Print / Export Audit Certificate</span>
              </button>
            </div>

            {/* Document Card */}
            <div className="card-clean" style={{ padding: '36px', maxWidth: '960px', margin: '0 auto', width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '2px solid #0c645d', paddingBottom: '16px', marginBottom: '24px' }}>
                <div>
                  <span style={{ fontSize: '22px', fontWeight: 900, color: '#0b2321', letterSpacing: '-0.02em' }}>
                    LEGACY<span style={{ color: '#0c645d' }}>X</span> 2.0
                  </span>
                  <div style={{ fontSize: '12px', fontWeight: 700, color: '#0c645d', marginTop: '2px' }}>
                    Modernization Assurance Seal • MAR-20260927-5D30C1
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontSize: '11px', textTransform: 'uppercase', color: '#64748b', fontWeight: 700, display: 'block' }}>
                    AUDIT SIGN-OFF STATUS
                  </span>
                  <span style={{ fontSize: '13px', fontWeight: 900, color: '#059669' }}>
                    SEALED & PROVEN
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div>
                  <h4 style={{ fontSize: '14px', fontWeight: 800, color: '#0b2321', marginBottom: '6px' }}>
                    Executive Modernization Summary
                  </h4>
                  <p style={{ fontSize: '12.5px', color: '#334155', lineHeight: 1.6 }}>
                    This Modernization Assurance Certificate provides empirical, mathematical, and execution-level proof of behavioral
                    equivalence for <strong>LegacyBank Enterprise Core</strong>. Out of 8 comprehensive high-value transaction scenarios
                    replayed through the dual-harness environment, 5 were verified to be bitwise identical in decision logic, and 3
                    identified silent drifts were isolated with precise AST line anchors and remediation tasks.
                  </p>
                </div>

                {/* Evidence Hash Tree */}
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                    <Hash size={14} color="#0c645d" />
                    <span style={{ fontSize: '12px', fontWeight: 800, color: '#0b2321', textTransform: 'uppercase' }}>
                      Cryptographic Evidence Hash Tree (SHA-256 Immutability)
                    </span>
                  </div>

                  <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '14px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {[
                      { component: 'AST System X-Ray Index', hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' },
                      { component: 'Business Rule DNA Synthesizer', hash: '8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4' },
                      { component: 'Decision Contracts Invariant Spec', hash: '7d1a54127b222502f5b79b5fb0803061152a44f92b37e23c65dd0e336d10e84f' },
                      { component: 'Dual-Harness Replay Ledger', hash: '12c6fc06c99a4622474e93ad8685da010dd6d93d01bbe801b8885f0538d363ec' },
                    ].map((item) => (
                      <div key={item.component} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '11px', fontFamily: 'monospace', borderBottom: '1px solid #edf2f7', paddingBottom: '6px' }}>
                        <span style={{ fontWeight: 700, color: '#0c645d' }}>{item.component}</span>
                        <span style={{ color: '#64748b' }}>{item.hash}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Auditor Signature */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', borderTop: '1px solid #e2e8f0', paddingTop: '20px', marginTop: '10px' }}>
                  <div>
                    <span style={{ fontSize: '10px', textTransform: 'uppercase', color: '#64748b', fontWeight: 700, display: 'block' }}>
                      LEAD MODERNIZATION ARCHITECT & AUDITOR
                    </span>
                    <span style={{ fontSize: '14px', fontWeight: 800, color: '#0b2321' }}>
                      Sarvesh K (Verified Automated Assurance Pipeline)
                    </span>
                    <span style={{ fontSize: '11px', color: '#64748b', display: 'block' }}>
                      LegacyX National Assurance Council • ISO/SOC2 Compliance Chain
                    </span>
                  </div>

                  <div style={{ textAlign: 'right', fontSize: '11px', color: '#64748b', fontFamily: 'monospace' }}>
                    Timestamp: {new Date().toUTCString()}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* ── Footer ───────────────────────────────────────────────────────── */}
      <footer
        style={{
          borderTop: '1px solid #cbe6e3',
          backgroundColor: 'rgba(255, 255, 255, 0.7)',
          padding: '14px 28px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '11.5px',
          color: '#64748b',
          maxWidth: '1440px',
          margin: '0 auto',
          width: '100%',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#10b981' }} />
          <span style={{ fontWeight: 700, color: '#0b2321' }}>LegacyX 2.0 Assurance Engine</span>
          <span>•</span>
          <span>Dual-Harness Behavioral Verification</span>
        </div>
        <div style={{ fontFamily: 'monospace', fontSize: '10.5px' }}>
          Deterministic Verification Protocol Active
        </div>
      </footer>

      {/* ── Drift Investigation Drawer / Modal ────────────────────────────── */}
      {investigatingScenario && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(11, 35, 33, 0.5)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            justifyContent: 'flex-end',
            zIndex: 50,
          }}
          onClick={() => setInvestigatingScenario(null)}
        >
          <div
            style={{
              width: '100%',
              maxWidth: '600px',
              height: '100%',
              backgroundColor: '#ffffff',
              borderLeft: '1px solid #cbe6e3',
              padding: '28px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              boxShadow: 'var(--shadow-lg)',
              overflowY: 'auto',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #cbe6e3', paddingBottom: '14px', marginBottom: '20px' }}>
                <div>
                  <span className="pill-badge" style={{ fontSize: '10px' }}>
                    SCENARIO #{investigatingScenario.scenario_number} INVESTIGATION
                  </span>
                  <h3 style={{ fontSize: '18px', fontWeight: 900, color: '#0b2321', marginTop: '2px' }}>
                    {investigatingScenario.scenario_name}
                  </h3>
                </div>
                <button
                  onClick={() => setInvestigatingScenario(null)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px' }}
                >
                  <X size={18} color="#64748b" />
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div style={{ padding: '12px', borderRadius: '12px', background: '#f8fafc', border: '1px solid #e2e8f0' }}>
                    <span style={{ fontSize: '10px', textTransform: 'uppercase', color: '#64748b', fontWeight: 700 }}>
                      LEGACY DECISION
                    </span>
                    <div style={{ fontSize: '13px', fontWeight: 900, color: '#0b2321', fontFamily: 'monospace', marginTop: '2px' }}>
                      {investigatingScenario.legacy_decision}
                    </div>
                  </div>

                  <div style={{ padding: '12px', borderRadius: '12px', background: investigatingScenario.comparison_status === 'BEHAVIOR_DRIFT' ? '#ffe4e6' : '#ecfdf5', border: `1px solid ${investigatingScenario.comparison_status === 'BEHAVIOR_DRIFT' ? '#fecdd3' : '#a7f3d0'}` }}>
                    <span style={{ fontSize: '10px', textTransform: 'uppercase', color: investigatingScenario.comparison_status === 'BEHAVIOR_DRIFT' ? '#9f1239' : '#065f46', fontWeight: 700 }}>
                      MODERN DECISION
                    </span>
                    <div style={{ fontSize: '13px', fontWeight: 900, color: investigatingScenario.comparison_status === 'BEHAVIOR_DRIFT' ? '#9f1239' : '#065f46', fontFamily: 'monospace', marginTop: '2px' }}>
                      {investigatingScenario.modern_decision}
                    </div>
                  </div>
                </div>

                {investigatingScenario.drift_details && (
                  <div style={{ background: '#fff1f2', border: '1px solid #fecdd3', borderRadius: '12px', padding: '14px' }}>
                    <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#9f1239', display: 'block', marginBottom: '4px' }}>
                      DRIFT ANALYSIS & BOUNDARY SHIFT
                    </span>
                    <p style={{ fontSize: '12.5px', color: '#9f1239', lineHeight: 1.5 }}>
                      {investigatingScenario.drift_details}
                    </p>
                  </div>
                )}

                {investigatingScenario.root_cause_explanation && (
                  <div style={{ background: '#e6f5f3', border: '1px solid #a8ded7', borderRadius: '12px', padding: '14px' }}>
                    <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#0c645d', display: 'block', marginBottom: '4px' }}>
                      ROOT-CAUSE CODE ANCHOR
                    </span>
                    <p style={{ fontSize: '12.5px', color: '#0b2321', lineHeight: 1.5 }}>
                      {investigatingScenario.root_cause_explanation}
                    </p>
                  </div>
                )}

                <div>
                  <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#64748b', display: 'block', marginBottom: '6px' }}>
                    AUDITOR VERIFICATION ACTION
                  </span>
                  <p style={{ fontSize: '12px', color: '#475569', lineHeight: 1.5 }}>
                    Under AGENTS.md §4.3 & §5.3, this scenario requires explicit developer remediation or architectural decision sign-off before marking verified.
                  </p>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '10px', paddingTop: '16px', borderTop: '1px solid #e2e8f0' }}>
              <button
                className="btn-secondary"
                style={{ flex: 1, justifyContent: 'center' }}
                onClick={() => setInvestigatingScenario(null)}
              >
                Close Drawer
              </button>
              <button
                className="btn-primary"
                style={{ flex: 1, justifyContent: 'center' }}
                onClick={() => {
                  alert(`Remediation ticket spawned for ${investigatingScenario.scenario_id}`)
                  setInvestigatingScenario(null)
                }}
              >
                Remediate Drift
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Quick Search Modal ────────────────────────────────────────────── */}
      {searchOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(11, 35, 33, 0.5)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'center',
            paddingTop: '80px',
            zIndex: 60,
          }}
          onClick={() => setSearchOpen(false)}
        >
          <div
            style={{
              width: '100%',
              maxWidth: '540px',
              backgroundColor: '#ffffff',
              borderRadius: '20px',
              border: '1px solid #cbe6e3',
              boxShadow: 'var(--shadow-lg)',
              overflow: 'hidden',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '16px 20px', borderBottom: '1px solid #cbe6e3' }}>
              <Search size={18} color="#0c645d" />
              <input
                type="text"
                autoFocus
                placeholder="Jump to: Replay Lab, Contracts, Blast Radius, Risk..."
                style={{ width: '100%', border: 'none', outline: 'none', fontSize: '14px', color: '#0b2321', background: 'transparent' }}
              />
              <kbd style={{ fontSize: '10px', padding: '2px 6px', background: '#f1f5f9', border: '1px solid #cbd5e1', borderRadius: '4px' }}>
                ESC
              </kbd>
            </div>

            <div style={{ padding: '12px' }}>
              {[
                { title: 'Decision Replay Lab', sub: '8 Dual-Harness Scenarios', tab: 'replay', icon: Activity },
                { title: 'Decision Contracts', sub: '7 Invariant Specifications', tab: 'contracts', icon: FileCheck2 },
                { title: '3-Layer Blast Radius', sub: '9 Multi-Layer Entities', tab: 'blast_radius', icon: Layers },
                { title: 'What-If Business Simulator', sub: 'Policy Drift Modeling', tab: 'whatif', icon: Sliders },
                { title: 'Modernization Risk Scorecard', sub: 'Score: 58.2 / 100', tab: 'risk', icon: ShieldAlert },
                { title: 'Assurance Report', sub: 'SHA-256 Verified Seal', tab: 'report', icon: Award },
              ].map((item) => {
                const Icon = item.icon
                return (
                  <button
                    key={item.title}
                    onClick={() => {
                      setActiveTab(item.tab as TabKey)
                      setSearchOpen(false)
                    }}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      padding: '10px 14px',
                      borderRadius: '12px',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      textAlign: 'left',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f0f8f7')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    <Icon size={16} color="#0c645d" />
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: 800, color: '#0b2321' }}>{item.title}</div>
                      <div style={{ fontSize: '11px', color: '#64748b' }}>{item.sub}</div>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
