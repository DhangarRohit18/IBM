// LegacyX Guard — Background Service Worker
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    guardActive: true,
    mutationState: false,
    activeRounding: 'HALF_UP',
    scenariosFrozen: 7,
    decisionsFound: 3,
    lastVerification: null,
  });
});

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'GET_STATE') {
    chrome.storage.local.get(null, (data) => sendResponse(data));
    return true;
  }
  if (msg.type === 'TOGGLE_MUTATION') {
    chrome.storage.local.get(['mutationState'], (data) => {
      const next = !data.mutationState;
      chrome.storage.local.set({
        mutationState: next,
        activeRounding: next ? 'HALF_DOWN' : 'HALF_UP',
      });
      // Broadcast state to all open tabs
      chrome.tabs.query({}, (tabs) => {
        if (tabs && tabs.length) {
          tabs.forEach((tab) => {
            if (tab && tab.id) {
              chrome.tabs.sendMessage(tab.id, {
                type: 'DRIFT_STATE',
                mutated: next,
              }).catch(() => {});
            }
          });
        }
      });
      sendResponse({ mutated: next });
    });
    return true;
  }
  if (msg.type === 'VERIFY_CHANGE') {
    chrome.storage.local.get(['mutationState'], (data) => {
      const result = data.mutationState
        ? {
            status: 'BEHAVIORAL_DRIFT_DETECTED',
            equivalence: false,
            total: 7,
            equivalent: 6,
            drift: 1,
            hero: {
              scenario: 'SCEN-04',
              name: 'Fee Calculation & Rounding Precision',
              legacy: '₹250.00',
              current: '₹249.99',
              diff: '₹0.01',
              rootCause: 'RoundingMode changed HALF_UP → HALF_DOWN at Line 45',
              file: 'FeeCalculation.java',
              line: 45,
            },
          }
        : {
            status: 'BEHAVIORALLY_EQUIVALENT',
            equivalence: true,
            total: 7,
            equivalent: 7,
            drift: 0,
            hero: null,
          };
      chrome.storage.local.set({ lastVerification: result });
      sendResponse(result);
    });
    return true;
  }
});
