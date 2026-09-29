// LegacyX Guard — Popup Controller
const SCENARIOS = [
  { id: '#01', name: 'Normal transfer',     legacy: '₹62.50',  current: '₹62.50',  drift: false },
  { id: '#02', name: '₹49,999 boundary',    legacy: '₹124.99', current: '₹124.99', drift: false },
  { id: '#03', name: '₹50,000 boundary',    legacy: '₹250.00', current: '₹250.00', drift: false },
  { id: '#04', name: 'Fee Rounding Mode',   legacy: '₹250.00', current: '₹250.00', drift: false, hero: true },
  { id: '#05', name: 'Premium customer',     legacy: '₹125.00', current: '₹125.00', drift: false },
  { id: '#06', name: 'High-risk (AML)',      legacy: 'HOLD',    current: 'HOLD',    drift: false },
  { id: '#07', name: 'Decimal rounding',     legacy: '₹1.43',   current: '₹1.43',   drift: false },
];

let isMutated = false;

function renderScenarios(mutated) {
  const body = document.getElementById('scenarioBody');
  body.innerHTML = '';
  SCENARIOS.forEach((s) => {
    const hasDrift = mutated && s.hero;
    const currentVal = hasDrift ? '₹249.99' : s.current;
    const row = document.createElement('div');
    row.className = 'scenario-row';
    row.innerHTML = `
      <span class="scenario-id">${s.id}</span>
      <span class="scenario-name">${s.name}</span>
      <span class="scenario-val">${s.legacy}</span>
      <span class="scenario-val" style="${hasDrift ? 'color: var(--accent); font-weight: 800;' : ''}">${currentVal}</span>
      <span class="${hasDrift ? 'tag-drift' : 'tag-preserved'}">${hasDrift ? 'DRIFT' : 'PRESERVED'}</span>
    `;
    body.appendChild(row);
  });
}

function updateUI(mutated) {
  isMutated = mutated;

  // Metrics
  document.getElementById('driftCount').textContent = mutated ? '1' : '0';
  document.getElementById('equivPct').textContent = mutated ? '85.7%' : '100%';
  document.getElementById('driftCount').style.color = mutated ? '#dc2626' : 'var(--accent)';

  // Status badge
  const badge = document.getElementById('statusBadge');
  badge.textContent = mutated ? '1 DRIFT DETECTED' : 'GUARD ACTIVE';
  badge.className = mutated ? 'status-badge status-drift' : 'status-badge status-active';

  // Replay status
  document.getElementById('replayStatus').textContent = mutated ? '6/7 — 1 DRIFT' : '7/7 EQUIVALENT';

  // Mutation button
  const mutateBtn = document.getElementById('btnMutate');
  document.getElementById('mutateLabel').textContent = mutated ? 'Remove Drift' : 'Inject Drift';
  mutateBtn.className = mutated ? 'btn btn-mutation-on' : 'btn btn-secondary';

  // Drift evidence
  document.getElementById('driftEvidence').classList.toggle('hidden', !mutated);

  // Scenarios
  renderScenarios(mutated);
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  updateUI(false);

  // Verify Change
  document.getElementById('btnVerify').addEventListener('click', () => {
    const btn = document.getElementById('btnVerify');
    btn.innerHTML = '<span class="btn-icon spin">⟳</span> Replaying 7 Scenarios...';
    btn.disabled = true;
    setTimeout(() => {
      btn.innerHTML = '<span class="btn-icon">▶</span> Verify Change (Replay)';
      btn.disabled = false;
      updateUI(isMutated);
    }, 600);
  });

  // Inject / Remove Drift
  document.getElementById('btnMutate').addEventListener('click', () => {
    updateUI(!isMutated);
    chrome.runtime.sendMessage({ type: 'TOGGLE_MUTATION' });
    // Also notify content script
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, {
          type: 'DRIFT_STATE',
          mutated: isMutated,
        }).catch(() => {});
      }
    });
  });

  // 01 — Understand
  document.getElementById('btnAnalyze').addEventListener('click', () => {
    showAI(
      '01 — Understand: Business Decisions in calculateTransferFee()\n\n' +
      'DEC-01: Transfer Fee Calculation\n' +
      '  Rule: amount > ₹50,000 ? 0.50% (High-Value) : 0.25% (Standard)\n' +
      '  Risk: HIGH | Scenarios: 7 | Lines: 38-55\n\n' +
      'DEC-02: High-Risk Compliance Boundary\n' +
      '  Rule: amount > ₹50,000 AND risk_score > 70 → Compliance Hold\n' +
      '  Risk: CRITICAL | Lines: 57-68\n\n' +
      'DEC-03: VIP Tier Exemption Policy\n' +
      '  Rule: customer.tier == VIP → 50% discount\n' +
      '  Risk: MEDIUM | Lines: 70-82\n\n' +
      'Dependencies: CustomerService, AccountService, FeePolicy\n' +
      'Affected APIs: POST /api/v1/transfers, GET /api/v1/fees/estimate'
    );
  });

  // 02 — Baseline
  document.getElementById('btnBaseline').addEventListener('click', () => {
    showAI(
      '02 — Capture: Behavioral Baseline Frozen!\n\n' +
      '7 canonical execution paths captured and cryptographically hashed.\n' +
      'Baseline Fingerprint: sha256:4f9a0c2188b1ec45d3e098a12903fe45b8\n\n' +
      'SCEN-01: Normal transfer       → ₹62.50   [FROZEN]\n' +
      'SCEN-02: ₹49,999 boundary      → ₹124.99  [FROZEN]\n' +
      'SCEN-03: ₹50,000 boundary      → ₹250.00  [FROZEN]\n' +
      'SCEN-04: ₹50,001 boundary      → ₹250.01  [FROZEN]\n' +
      'SCEN-05: Premium customer       → ₹125.00  [FROZEN]\n' +
      'SCEN-06: High-risk customer     → HOLD     [FROZEN]\n' +
      'SCEN-07: Decimal rounding       → ₹1.43    [FROZEN]'
    );
  });

  // 03 — Blast Radius
  document.getElementById('btnImpact').addEventListener('click', () => {
    showAI(
      '03 — Change Impact (Blast Radius):\n\n' +
      '• 3 Business Decisions Affected\n' +
      '• 7 Behavioral Scenarios Affected\n' +
      '• 3 Downstream Services: TransferService, AccountService, AuditLedgerService\n' +
      '• 2 Public APIs: POST /api/v1/transfers, GET /api/v1/fees/estimate\n\n' +
      'Safety Advisory: Change directly modifies monetary outcome for high-value transactions. Replay verification mandatory before git commit.'
    );
  });

  // Ask LegacyX AI
  document.getElementById('btnAsk').addEventListener('click', () => {
    showAI(
      'LegacyX AI Explanation (Grounded in AST Evidence):\n\n' +
      'Method calculateTransferFee() is classified as HIGH RISK because it directly governs monetary debits across 3 downstream services (AccountService, TransferService, AuditLedgerService) and 2 public REST endpoints.\n\n' +
      'It establishes the high-value transaction boundary at ₹50,000. Under boundary condition Scenario #04, altering the rounding strategy from RoundingMode.HALF_UP to RoundingMode.HALF_DOWN produces an unprescribed ₹0.01 deficit.\n\n' +
      'Evidence: AST nodes [calculateTransferFee, amount, BigDecimal.setScale]\n' +
      'Frozen Baseline Hash: sha256:4f9a0c2188b1ec45d3e098a12903fe45b8'
    );
  });
});

function showAI(text) {
  const el = document.getElementById('aiAnswer');
  const txt = document.getElementById('aiAnswerText');
  el.classList.remove('hidden');
  txt.textContent = '';
  // Typewriter effect
  let i = 0;
  const interval = setInterval(() => {
    txt.textContent += text[i];
    i++;
    if (i >= text.length) clearInterval(interval);
  }, 4);
}
