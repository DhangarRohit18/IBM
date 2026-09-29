// LegacyX Guard — Content Script (Injected on Every Page)
(function () {
  if (document.getElementById('legacyx-guard-badge')) return;

  let mutated = false;

  const badge = document.createElement('div');
  badge.id = 'legacyx-guard-badge';
  badge.innerHTML = `
    <div class="lx-shield">LX</div>
    <span>LegacyX Guard</span>
    <span class="lx-status ok" id="lx-badge-status">7/7 EQUIVALENT</span>
  `;
  badge.title = 'Click to open LegacyX Guard extension popup';
  badge.addEventListener('click', () => {
    // Clicking the badge triggers the extension popup if possible
    // Otherwise show a brief tooltip
    if (chrome && chrome.runtime && chrome.runtime.id) {
      chrome.runtime.sendMessage({ type: 'GET_STATE' }, (state) => {
        if (chrome.runtime.lastError) return;
      });
    }
  });

  document.body.appendChild(badge);

  // Listen for drift state changes from popup
  if (chrome && chrome.runtime && chrome.runtime.onMessage) {
    chrome.runtime.onMessage.addListener((msg) => {
      if (msg.type === 'DRIFT_STATE') {
        mutated = msg.mutated;
        const statusEl = document.getElementById('lx-badge-status');
        if (statusEl) {
          statusEl.textContent = mutated ? '1 DRIFT DETECTED' : '7/7 EQUIVALENT';
          statusEl.className = mutated ? 'lx-status drift' : 'lx-status ok';
        }
      }
    });
  }
})();
