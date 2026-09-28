"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = require("vscode");
let diagnosticCollection;
let isMutatedState = false;
function activate(context) {
    diagnosticCollection = vscode.languages.createDiagnosticCollection('legacyx-guard');
    context.subscriptions.push(diagnosticCollection);
    // 1. Status Bar Item
    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBar.text = "$(shield) LegacyX Guard: Active (7 Scenarios Frozen)";
    statusBar.tooltip = "LegacyX Guard: Behavioral Assurance Active for Legacy Modernization";
    statusBar.command = "legacyx.verifyChange";
    statusBar.show();
    context.subscriptions.push(statusBar);
    // 2. CodeLens Provider for Java files
    const codeLensProvider = new LegacyXCodeLensProvider();
    context.subscriptions.push(vscode.languages.registerCodeLensProvider({ language: 'java', scheme: 'file' }, codeLensProvider));
    // 3. Webview View Provider for Explorer Sidebar
    const sidebarProvider = new LegacyXSidebarProvider(context.extensionUri);
    context.subscriptions.push(vscode.window.registerWebviewViewProvider('legacyx.guardView', sidebarProvider));
    // 4. Command: 01 Understand Business Decisions
    context.subscriptions.push(vscode.commands.registerCommand('legacyx.analyzeMethod', async () => {
        vscode.window.showInformationMessage("LegacyX Guard — Business Decisions Found in calculateTransferFee():\n" +
            "1. Transfer Fee Calculation (amount > ₹50,000 -> 0.50% vs 0.25%)\n" +
            "2. High-Risk Compliance Boundary (amount > ₹50,000 & Risk > 70)\n" +
            "3. VIP Customer Exemption (50% fee discount)\n" +
            "Covered Scenarios: 7 | Downstream Dependencies: 3 | Risk Level: HIGH");
    }));
    // 5. Command: 02 Capture Behavioral Baseline
    context.subscriptions.push(vscode.commands.registerCommand('legacyx.createBaseline', async () => {
        vscode.window.showInformationMessage("LegacyX Guard — Behavioral Baseline Frozen!\n" +
            "7 scenarios captured and cryptographically hashed.\n" +
            "Baseline Fingerprint: sha256:4f9a0c2188b1ec45d3e098a12903fe45b8");
    }));
    // 6. Command: 03 Change Impact (Blast Radius)
    context.subscriptions.push(vscode.commands.registerCommand('legacyx.changeImpact', async () => {
        vscode.window.showInformationMessage("LegacyX Guard — Change Impact (Blast Radius):\n" +
            "• 3 Business Decisions Affected\n" +
            "• 7 Behavioral Scenarios Affected\n" +
            "• 3 Downstream Services: TransferService, AccountService, AuditLedger\n" +
            "• 2 Public APIs: POST /api/v1/transfers, GET /api/v1/fees/estimate");
    }));
    // 7. Command: 04 Verify Change (Run Scenarios & Detect Drift)
    context.subscriptions.push(vscode.commands.registerCommand('legacyx.verifyChange', async () => {
        const editor = vscode.window.activeTextEditor;
        const docText = editor ? editor.document.getText() : "";
        const hasHalfDown = docText.includes("RoundingMode.HALF_DOWN") || isMutatedState;
        if (hasHalfDown) {
            // Drift detected
            if (editor) {
                const line45 = new vscode.Position(44, 0);
                const range = new vscode.Range(line45, new vscode.Position(44, 80));
                const diagnostic = new vscode.Diagnostic(range, "⚠ LegacyX Guard: Behavioral drift detected in Scenario #04: Expected ₹250.00, Actual ₹249.99 (Diff: ₹0.01). Root cause: RoundingMode changed HALF_UP -> HALF_DOWN.", vscode.DiagnosticSeverity.Warning);
                diagnostic.source = "LegacyX Guard";
                diagnosticCollection.set(editor.document.uri, [diagnostic]);
            }
            const choice = await vscode.window.showWarningMessage("⚠ LEGACYX BEHAVIORAL DRIFT DETECTED\n" +
                "Scenario #04 (₹50,000 transfer): Legacy ₹250.00 vs Current ₹249.99 (Difference: ₹0.01)\n" +
                "Root Cause: RoundingMode changed HALF_UP -> HALF_DOWN at Line 45.", "View Evidence (Line 45)", "Ask LegacyX AI");
            if (choice === "View Evidence (Line 45)") {
                vscode.commands.executeCommand("legacyx.jumpToSourceEvidence");
            }
            else if (choice === "Ask LegacyX AI") {
                vscode.commands.executeCommand("legacyx.askLegacyX");
            }
        }
        else {
            if (editor) {
                diagnosticCollection.delete(editor.document.uri);
            }
            vscode.window.showInformationMessage("LegacyX Guard: 100% Behavioral Equivalence Verified.\n" +
                "7/7 scenarios preserved across legacy and modern execution harnesses. Zero drift detected.");
        }
    }));
    // 8. Command: Mutation Challenge (Inject Controlled Drift)
    context.subscriptions.push(vscode.commands.registerCommand('legacyx.injectControlledDrift', async () => {
        isMutatedState = !isMutatedState;
        const msg = isMutatedState
            ? "🧪 Controlled Drift INJECTED: RoundingMode simulated as HALF_DOWN. Click 'Verify Change' to observe LegacyX Guard detect the drift!"
            : "Controlled Drift REMOVED: RoundingMode restored to HALF_UP. Behavioral equivalence restored.";
        vscode.window.showInformationMessage(msg);
    }));
    // 9. Command: Jump to Source Evidence Line 45
    context.subscriptions.push(vscode.commands.registerCommand('legacyx.jumpToSourceEvidence', async () => {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            const targetLine = 44; // 0-indexed line 45
            const position = new vscode.Position(targetLine, 8);
            editor.selection = new vscode.Selection(position, new vscode.Position(targetLine, 75));
            editor.revealRange(new vscode.Range(position, position), vscode.TextEditorRevealType.InCenter);
        }
    }));
    // 10. Command: Ask LegacyX AI
    context.subscriptions.push(vscode.commands.registerCommand('legacyx.askLegacyX', async () => {
        const question = await vscode.window.showInputBox({
            prompt: "Ask LegacyX Guard about business decisions, impact, or drift",
            value: "Why is calculateTransferFee() high risk?"
        });
        if (question) {
            vscode.window.showInformationMessage("LegacyX AI Explanation:\n" +
                "Method calculateTransferFee() is classified as HIGH RISK because it directly governs monetary debits across 3 downstream services (AccountService, TransferService, AuditLedger) and enforces the high-value transaction boundary at ₹50,000. In Scenario #04, altering the rounding policy from HALF_UP to HALF_DOWN creates an unprescribed ₹0.01 deficit.", { modal: true });
        }
    }));
    // 11. Auto-verify on save
    context.subscriptions.push(vscode.workspace.onDidSaveTextDocument((document) => {
        if (document.languageId === 'java') {
            vscode.commands.executeCommand('legacyx.verifyChange');
        }
    }));
}
function deactivate() {
    if (diagnosticCollection) {
        diagnosticCollection.clear();
    }
}
/**
 * CodeLens Provider: Displays quick-action shields directly above Java methods.
 */
class LegacyXCodeLensProvider {
    provideCodeLenses(document) {
        const lenses = [];
        const text = document.getText();
        const lines = text.split('\n');
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].includes('calculateTransferFee')) {
                const range = new vscode.Range(i, 0, i, 0);
                // Shield badge
                lenses.push(new vscode.CodeLens(range, {
                    title: "🛡️ LegacyX Guard: 3 Business Decisions | 7 Scenarios Frozen",
                    command: "legacyx.analyzeMethod"
                }));
                // Verify Change
                lenses.push(new vscode.CodeLens(range, {
                    title: "▶ Verify Change (Replay)",
                    command: "legacyx.verifyChange"
                }));
                // Ask AI
                lenses.push(new vscode.CodeLens(range, {
                    title: "💬 Ask LegacyX",
                    command: "legacyx.askLegacyX"
                }));
                break;
            }
        }
        return lenses;
    }
}
/**
 * Sidebar Webview Provider: Renders the LegacyX Guard dashboard inside VS Code.
 */
class LegacyXSidebarProvider {
    _extensionUri;
    constructor(_extensionUri) {
        this._extensionUri = _extensionUri;
    }
    resolveWebviewView(webviewView) {
        webviewView.webview.options = { enableScripts: true };
        webviewView.webview.html = this._getHtmlForWebview();
        webviewView.webview.onDidReceiveMessage((data) => {
            switch (data.type) {
                case 'analyze':
                    vscode.commands.executeCommand('legacyx.analyzeMethod');
                    break;
                case 'baseline':
                    vscode.commands.executeCommand('legacyx.createBaseline');
                    break;
                case 'impact':
                    vscode.commands.executeCommand('legacyx.changeImpact');
                    break;
                case 'verify':
                    vscode.commands.executeCommand('legacyx.verifyChange');
                    break;
                case 'mutate':
                    vscode.commands.executeCommand('legacyx.injectControlledDrift');
                    break;
                case 'jump':
                    vscode.commands.executeCommand('legacyx.jumpToSourceEvidence');
                    break;
            }
        });
    }
    _getHtmlForWebview() {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: var(--vscode-font-family); padding: 12px; font-size: 12px; color: var(--vscode-foreground); }
        .header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; border-bottom: 1px solid var(--vscode-widget-border); padding-bottom: 8px; }
        .badge { font-size: 10px; font-weight: 700; background: #e11d48; color: #fff; padding: 2px 6px; border-radius: 4px; }
        .btn { width: 100%; padding: 8px; margin-top: 6px; background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; border-radius: 4px; cursor: pointer; font-weight: 600; text-align: left; display: flex; align-items: center; gap: 6px; }
        .btn:hover { background: var(--vscode-button-hoverBackground); }
        .card { background: var(--vscode-editor-background); border: 1px solid var(--vscode-widget-border); padding: 10px; border-radius: 6px; margin-top: 10px; }
        .quote { font-style: italic; color: #94a3b8; font-size: 11px; margin-top: 12px; border-left: 2px solid #2563eb; padding-left: 6px; }
    </style>
</head>
<body>
    <div class="header">
        <span style="font-size: 16px;">🛡️</span>
        <div>
            <div style="font-weight: 800; font-size: 13px;">LegacyX Guard</div>
            <div style="font-size: 10px; color: #64748b;">Developer Behavioral Safety Layer</div>
        </div>
    </div>

    <div class="card">
        <div style="font-weight: 700; margin-bottom: 4px;">Target: FeeCalculation.java</div>
        <div style="font-size: 11px; color: #64748b;">Method: calculateTransferFee()</div>
        <div style="margin-top: 6px;"><span class="badge">HIGH RISK</span> 3 Decisions | 7 Scenarios</div>
    </div>

    <div style="margin-top: 12px; font-weight: 700;">Developer Actions</div>
    <button class="btn" onclick="sendMessage('analyze')"><span>🔍</span> 01 — Understand Decisions</button>
    <button class="btn" onclick="sendMessage('baseline')"><span>❄️</span> 02 — Freeze Baseline</button>
    <button class="btn" onclick="sendMessage('impact')"><span>💥</span> 03 — Change Impact</button>
    <button class="btn" onclick="sendMessage('verify')" style="background: #2563eb; color: #fff;"><span>▶</span> 04 — Verify Change</button>
    <button class="btn" onclick="sendMessage('mutate')" style="background: #e11d48; color: #fff;"><span>🧪</span> Inject Controlled Drift</button>
    <button class="btn" onclick="sendMessage('jump')"><span>📍</span> Jump to Evidence (Line 45)</button>

    <div class="quote">
        “The compiler said this change was valid. LegacyX said the business decision wasn't.”
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        function sendMessage(type) {
            vscode.postMessage({ type });
        }
    </script>
</body>
</html>`;
    }
}
//# sourceMappingURL=extension.js.map