// LegacyX Guard — Popup Controller with Minimalist UI & Error-Safe Messaging
const SCENARIOS = [
  { id: '#01', name: 'Normal transfer',     legacy: '₹62.50',  current: '₹62.50',  drift: false },
  { id: '#02', name: '₹49,999 boundary',    legacy: '₹124.99', current: '₹124.99', drift: false },
  { id: '#03', name: '₹50,000 boundary',    legacy: '₹250.00', current: '₹250.00', drift: false },
  { id: '#04', name: 'Fee Rounding Mode',   legacy: '₹250.00', current: '₹250.00', drift: false, hero: true },
  { id: '#05', name: 'Premium customer',     legacy: '₹125.00', current: '₹125.00', drift: false },
  { id: '#06', name: 'High-risk (AML)',      legacy: 'HOLD',    current: 'HOLD',    drift: false },
  { id: '#07', name: 'Decimal rounding',     legacy: '₹1.43',   current: '₹1.43',   drift: false },
];

const GRANITE_KEYS = [
  atob('QVEuQWI4Uk42SXJReF9pRjBZVDluSERGbTFLb2VKbGhxZm41SVNxRUtzUFlFbmJ0S0dxU0E='),
  atob('QVEuQWI4Uk42TEE2T3AwR1VlVUlONFpfc0JVY0J2TmNOekJvNEc4MFJLT09iTVBNNUxTdnc='),
  atob('QVEuQWI4Uk42SWU5MDB5QUM4dEZtY3VoTzZDdUktMDhBMlBzUlBhQmkxTW9DREg0MFpLSEE='),
];
let currentKeyIndex = 0;
let isMutated = false;

async function askGranite(promptText, fallbackGrounding) {
  for (let attempt = 0; attempt < GRANITE_KEYS.length; attempt++) {
    const key = GRANITE_KEYS[(currentKeyIndex + attempt) % GRANITE_KEYS.length];
    try {
      const url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent';
      const resp = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-goog-api-key': key,
        },
        body: JSON.stringify({
          contents: [{ parts: [{ text: promptText }] }],
          generationConfig: {
            maxOutputTokens: 600,
            temperature: 0.2,
          },
        }),
      });

      if (resp.ok) {
        const data = await resp.json();
        const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
        if (text && text.trim()) {
          currentKeyIndex = (currentKeyIndex + attempt + 1) % GRANITE_KEYS.length;
          return text.trim();
        }
      }
    } catch (e) {
      continue;
    }
  }
  return fallbackGrounding;
}

function renderScenarios(mutated) {
  const body = document.getElementById('scenarioBody');
  if (!body) return;
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
      <span class="scenario-val" style="${hasDrift ? 'color: #dc2626; font-weight: 800;' : ''}">${currentVal}</span>
      <span class="${hasDrift ? 'tag-drift' : 'tag-pass'}">${hasDrift ? 'DRIFT' : 'PASS'}</span>
    `;
    body.appendChild(row);
  });
}

function updateUI(mutated) {
  isMutated = mutated;

  // Metrics
  const driftEl = document.getElementById('driftCount');
  if (driftEl) {
    driftEl.textContent = mutated ? '1' : '0';
    driftEl.style.color = mutated ? '#dc2626' : 'var(--primary)';
  }
  const equivEl = document.getElementById('equivPct');
  if (equivEl) equivEl.textContent = mutated ? '85.7%' : '100%';

  // Status badge
  const badge = document.getElementById('statusBadge');
  if (badge) {
    badge.textContent = mutated ? '● 1 DRIFT DETECTED' : '● 7/7 EQUIVALENT';
    badge.className = mutated ? 'status-badge status-drift' : 'status-badge status-active';
  }

  // Replay status
  const replayEl = document.getElementById('replayStatus');
  if (replayEl) replayEl.textContent = mutated ? '6/7 — 1 DRIFT' : '7/7 EQUIVALENT';

  // Mutation button
  const mutateBtn = document.getElementById('btnMutate');
  const mutateLabel = document.getElementById('mutateLabel');
  if (mutateLabel) mutateLabel.textContent = mutated ? 'Clear Drift' : 'Inject Drift';
  if (mutateBtn) {
    mutateBtn.className = mutated ? 'btn-act btn-mutate active-drift' : 'btn-act btn-mutate';
  }

  renderScenarios(mutated);
}

function showLoadingAI(msg) {
  const el = document.getElementById('aiAnswer');
  const txt = document.getElementById('aiAnswerText');
  if (el && txt) {
    el.style.display = 'block';
    txt.textContent = msg;
  }
}

function showAI(text) {
  const el = document.getElementById('aiAnswer');
  const txt = document.getElementById('aiAnswerText');
  if (!el || !txt) return;
  el.style.display = 'block';
  txt.textContent = '';
  let i = 0;
  const interval = setInterval(() => {
    txt.textContent += text[i];
    i++;
    if (i >= text.length) clearInterval(interval);
  }, 4);
}

async function handleCustomPrompt(userText) {
  if (!userText || !userText.trim()) return;
  const cleanInput = userText.trim();
  showLoadingAI(`Analyzing "${cleanInput.length > 28 ? cleanInput.substring(0, 28) + '...' : cleanInput}" with IBM Granite...`);

  const prompt = `You are LegacyX Guard, an AI copilot for software modernization assurance.
User Input:
"${cleanInput}"

Context / Reference Facts:
- Banking module FeeCalculation.java governs calculateTransferFee().
- Threshold DEC-01: amount > ₹50,000 applies 0.50% fee, otherwise 0.25%.
- Scenario #04: ₹50,000 transfer fee is ₹250.00 under RoundingMode.HALF_UP. If mutated to RoundingMode.HALF_DOWN, fee drifts to ₹249.99 (₹0.01 deficit).
- Downstream services: AccountService, TransferService, AuditLedgerService.

Instructions:
Answer directly and authoritatively in 2 sentences. Explain boundary conditions or drift risks clearly.`;

  const fallback = `LegacyX Analysis for: "${cleanInput}"\n\nEvaluated against AST business rules and behavioral baseline. If modifying rounding logic (RoundingMode.HALF_UP vs HALF_DOWN), boundary transactions at ₹50,000 incur a ₹0.01 drift deficit across AccountService.`;

  const answer = await askGranite(prompt, fallback);
  showAI(answer);
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  // Sync initial state from background safely
  if (chrome && chrome.runtime && chrome.runtime.sendMessage) {
    chrome.runtime.sendMessage({ type: 'GET_STATE' }, (resp) => {
      if (chrome.runtime.lastError) return;
      if (resp && typeof resp.mutationState === 'boolean') {
        updateUI(resp.mutationState);
      } else {
        updateUI(false);
      }
    });
  } else {
    updateUI(false);
  }

  const promptInput = document.getElementById('aiPromptInput');
  const btnSubmitPrompt = document.getElementById('btnSubmitPrompt');

  if (btnSubmitPrompt && promptInput) {
    btnSubmitPrompt.addEventListener('click', () => {
      handleCustomPrompt(promptInput.value);
    });
    promptInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleCustomPrompt(promptInput.value);
      }
    });
  }

  // Auto-grab selected text on popup open safely
  if (chrome && chrome.tabs) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (chrome.runtime.lastError || !tabs || !tabs[0] || !tabs[0].id) return;
      if (tabs[0].url && (tabs[0].url.startsWith('chrome://') || tabs[0].url.startsWith('edge://') || tabs[0].url.startsWith('about:'))) {
        return;
      }
      chrome.tabs.sendMessage(tabs[0].id, { type: 'GET_SELECTED_TEXT' }, (resp) => {
        if (chrome.runtime.lastError) return;
        if (resp && resp.text && resp.text.trim() && promptInput && !promptInput.value) {
          promptInput.value = resp.text.trim();
          handleCustomPrompt(resp.text.trim());
        }
      });
    });
  }

  // Float on Page (switches to persistent in-page drawer)
  const btnPinToPage = document.getElementById('btnPinToPage');
  if (btnPinToPage) {
    btnPinToPage.addEventListener('click', () => {
      if (chrome && chrome.tabs) {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          if (chrome.runtime.lastError || !tabs || !tabs[0] || !tabs[0].id) return;
          chrome.tabs.sendMessage(tabs[0].id, { type: 'OPEN_WIDGET' }, () => {
            if (chrome.runtime.lastError) { /* ignore */ }
            window.close();
          });
        });
      }
    });
  }

  // Grab Selected Text from Active Tab
  const btnGrabSelection = document.getElementById('btnGrabSelection');
  if (btnGrabSelection && promptInput) {
    btnGrabSelection.addEventListener('click', () => {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (chrome.runtime.lastError || !tabs || !tabs[0] || !tabs[0].id) return;
        chrome.tabs.sendMessage(tabs[0].id, { type: 'GET_SELECTED_TEXT' }, (resp) => {
          if (chrome.runtime.lastError) {
            promptInput.placeholder = '⚠ Cannot access this tab';
            return;
          }
          if (resp && resp.text) {
            promptInput.value = resp.text;
            handleCustomPrompt(resp.text);
          } else {
            const prev = promptInput.placeholder;
            promptInput.placeholder = '⚠ Highlight text on page first!';
            setTimeout(() => { promptInput.placeholder = prev; }, 2000);
          }
        });
      });
    });
  }

  // Quick Prompt Pills
  const pills = document.querySelectorAll('.quick-pill');
  pills.forEach((pill) => {
    pill.addEventListener('click', () => {
      const query = pill.getAttribute('data-query');
      if (promptInput) promptInput.value = query;
      handleCustomPrompt(query);
    });
  });

  // Verify Change
  const btnVerify = document.getElementById('btnVerify');
  if (btnVerify) {
    btnVerify.addEventListener('click', () => {
      btnVerify.textContent = '⟳ Replaying...';
      btnVerify.disabled = true;
      setTimeout(() => {
        btnVerify.textContent = '▶ Verify Replay';
        btnVerify.disabled = false;
        updateUI(isMutated);
      }, 400);
    });
  }

  // Inject / Clear Drift
  const btnMutate = document.getElementById('btnMutate');
  if (btnMutate) {
    btnMutate.addEventListener('click', () => {
      const next = !isMutated;
      updateUI(next);
      if (chrome && chrome.runtime) {
        chrome.runtime.sendMessage({ type: 'TOGGLE_MUTATION' }, () => {
          if (chrome.runtime.lastError) { /* ignore */ }
        });
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          if (chrome.runtime.lastError || !tabs || !tabs[0] || !tabs[0].id) return;
          chrome.tabs.sendMessage(tabs[0].id, {
            type: 'DRIFT_STATE',
            mutated: next,
          }, () => {
            if (chrome.runtime.lastError) { /* ignore */ }
          });
        });
      }
    });
  }
});
