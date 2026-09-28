"""
LEGACYX 2.0 — Deterministic Demo Seeder.

Seeds the canonical LegacyBank Enterprise Core application:
1. Ingestion of valid-legacybank-app.zip
2. System X-Ray AST analysis (packages, classes, methods, call graph)
3. Business Rule DNA recovery with full evidence snippets
4. Decision Contract synthesis & enforcement
5. Decision Replay Lab execution (96 Preserved, 3 Silent Drift, 1 Inconclusive)
6. Three-Layer Impact Analysis (Code + Business + Behavioral)
7. Risk Scorecard & Executive Assurance Report generation
"""

import asyncio
import os
import sys
from pathlib import Path
import httpx

API_BASE = "http://127.0.0.1:8002/api/v1"
FIXTURES_DIR = Path(__file__).parent / "tests" / "fixtures"
LEGACY_BANK_ZIP = FIXTURES_DIR / "valid-legacybank-app.zip"


async def seed_demo():
    print(f"Connecting to LegacyX Backend at {API_BASE}...")
    async with httpx.AsyncClient(base_url=API_BASE, timeout=60.0) as client:
        # Check backend health
        try:
            h = await client.get("/health")
            print(f"[OK] Health check passed: {h.json().get('status')}")
        except Exception as e:
            print(f"[ERROR] Could not connect to backend at {API_BASE}: {e}")
            return

        # 1. Check or Create Project
        projects_res = await client.get("/projects")
        projects = projects_res.json()
        target_proj = next((p for p in projects if p["name"] == "LegacyBank Enterprise Core"), None)

        if not target_proj:
            print("Creating 'LegacyBank Enterprise Core' project...")
            create_res = await client.post(
                "/projects",
                json={
                    "name": "LegacyBank Enterprise Core",
                    "description": "National-level showcase: Core transaction processing, risk evaluation, and silent business drift detection.",
                },
            )
            target_proj = create_res.json()
            print(f"[OK] Project created: {target_proj['id']}")
        else:
            print(f"[OK] Found existing project: {target_proj['id']}")

        project_id = target_proj["id"]

        # 2. Check or Upload Repository
        repo_res = await client.get(f"/repositories/{project_id}")
        repository = None
        if repo_res.status_code == 200:
            repository = repo_res.json()
            print(f"[OK] Found existing repository: {repository['id']} (status: {repository['status']})")
        else:
            print(f"Uploading fixture {LEGACY_BANK_ZIP}...")
            with open(LEGACY_BANK_ZIP, "rb") as f:
                upload_res = await client.post(
                    f"/projects/{project_id}/repositories",
                    files={"file": ("legacybank.zip", f, "application/zip")},
                )
            repository = upload_res.json()
            print(f"[OK] Repository uploaded: {repository['id']}")

        repo_id = repository["id"]

        # 3. System X-Ray Analysis
        runs_res = await client.get(f"/repositories/{repo_id}/analysis")
        runs = runs_res.json() if runs_res.status_code == 200 else []
        analysis_run = runs[0] if runs else None

        if not analysis_run or analysis_run.get("status") != "COMPLETED":
            print("Triggering System X-Ray AST Analysis...")
            start_res = await client.post(f"/repositories/{repo_id}/analysis")
            analysis_run = start_res.json()
            print(f"[OK] Analysis completed: {analysis_run['id']} (Classes: {analysis_run.get('total_classes', 0)})")
        else:
            print(f"[OK] Analysis already complete: {analysis_run['id']}")

        analysis_id = analysis_run["id"]

        # 4. Generate Decision Contracts from Rule DNA
        print("Synthesizing Decision Contracts from Business Rule DNA...")
        contracts_res = await client.post(
            f"/analysis/{analysis_id}/contracts/generate?repository_id={repo_id}"
        )
        contracts = contracts_res.json()
        print(f"[OK] Generated {len(contracts)} Decision Contracts.")

        # 5. Execute Decision Replay Session
        print("Running Decision Replay Lab Session (Legacy vs Modern)...")
        replay_res = await client.post(
            f"/repositories/{repo_id}/decision-replay",
            json={"include_deliberate_drift": True},
        )
        replay = replay_res.json()
        print(
            f"[OK] Replay Completed: {replay['total_scenarios']} scenarios "
            f"({replay['preserved_count']} PRESERVED, {replay['drift_count']} DRIFT, {replay['unknown_count']} UNKNOWN)."
        )

        # 6. Verify Three-Layer Impact
        print("Computing Three-Layer Impact Analysis...")
        impact_res = await client.get(f"/analysis/{analysis_id}/impact/three-layer")
        impact = impact_res.json()
        print(f"[OK] Impact nodes: {len(impact.get('nodes', []))}, risk level: {impact.get('risk_level')}")

        # 7. Verify Modernization Risk Scorecard
        print("Evaluating 6-Dimensional Risk Scorecard...")
        risk_res = await client.get(f"/repositories/{repo_id}/risk-score")
        risk = risk_res.json()
        print(f"[OK] Overall Risk Score: {risk.get('overall_risk_score')} ({risk.get('overall_status')})")

        # 8. Generate Modernization Assurance Report
        print("Generating Executive Assurance Report...")
        report_res = await client.get(f"/repositories/{repo_id}/assurance-report")
        report = report_res.json()
        print(
            f"[OK] Executive Report Generated: {report['report_id']}\n"
            f"     Motto: '{report['motto']}'\n"
            f"     Sign-off Status: {report['signoff_status']}\n"
            f"     Evidence Hash Tree Nodes: {len(report.get('evidence_hash_tree', []))}"
        )

        print("\n=======================================================")
        print("LEGACYX 2.0 DEMO DATASET READY!")
        print(f"Open in browser: http://localhost:5190/projects/{project_id}?tab=replay")
        print("=======================================================\n")


if __name__ == "__main__":
    asyncio.run(seed_demo())
