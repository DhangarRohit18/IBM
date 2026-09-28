# LegacyX Guard — Behavioral Assurance Inside the IDE

> *“Know what your code change changes. Catch behavioral drift before it reaches production.”*
>
> *“The compiler said this change was valid. LegacyX said the business decision wasn't.”*

---

## What is LegacyX Guard?

LegacyX Guard is a developer-side behavioral safety layer that connects directly into your IDE. While the **LegacyX Web Platform** is used by architects to map dependencies and orchestrate modernizations, **LegacyX Guard** sits directly inside the developer's everyday workflow.

It ensures that when legacy code is modernized or refactored, the underlying **business decisions and invariants are preserved**—even when unit tests pass and compilers succeed.

---

## The 4 Developer Moments

| Moment | Capability | What Happens in the IDE |
|---|---|---|
| **01 — Before changing code** | **Understand** | Right-click a method $\to$ **Analyze with LegacyX**: Discovers extracted business decisions, dependencies, and risk level. |
| **02 — Before modernization** | **Capture** | Right-click $\to$ **Create Behavioral Baseline**: Freezes canonical execution paths into an immutable baseline. |
| **03 — While changing code** | **Change Impact** | Modifying code updates **Blast Radius**: Displays affected decisions, downstream services, public APIs, and scenarios. |
| **04 — Before release** | **Prove (Verify)** | Click **Verify Change**: Executes dual-runtime replay, compares legacy vs current, and highlights silent drift down to the exact source diff. |

---

## The Hero Demonstration & Wow Moment

1. Open `demo-workspace/FeeCalculation.java`.
2. Notice the **CodeLens** above `calculateTransferFee()`:
   `[🛡️ LegacyX Guard: 3 Business Decisions | 7 Scenarios Frozen | ▶ Verify Change | 💬 Ask LegacyX]`
3. Alter line 45 from:
   ```java
   - BigDecimal fee = amount.multiply(feeRate).setScale(2, RoundingMode.HALF_UP);
   ```
   to:
   ```java
   + BigDecimal fee = amount.multiply(feeRate).setScale(2, RoundingMode.HALF_DOWN);
   ```
4. Click **Verify Change** or save the file.
5. **LegacyX Guard immediately raises a behavioral warning**:
   - **Scenario #04**: ₹50,000 transfer
   - **Legacy Runtime**: ₹250.00
   - **Current Runtime**: ₹249.99
   - **Difference**: ₹0.01 (Rounding drift)
   - **Root Cause**: RoundingMode changed HALF_UP $\to$ HALF_DOWN at Line 45.

---

## Mutation Challenge

Click the **🧪 Inject Controlled Drift** button in the sidebar or command palette. LegacyX Guard deliberately mutates the modern runtime rounding behavior, allowing you to prove live to judges that verification is dynamic and deterministic rather than pre-recorded!

---

## How to Test / Run the Extension in VS Code

1. Open this repository in VS Code.
2. In a terminal:
   ```bash
   cd vscode-extension
   npm install
   npm run compile
   ```
3. Press `F5` (or go to `Run and Debug` $\to$ `Launch Extension`).
4. In the new Extension Development Host window, open `vscode-extension/demo-workspace/FeeCalculation.java`.
5. Enjoy real-time behavioral assurance directly in your editor!
