"""Integration tests for Phase 2 Projects & Repositories API endpoints."""

from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.mark.asyncio
async def test_project_creation_and_repository_upload():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        # 1. Create project
        resp = await client.post(
            "/api/v1/projects",
            json={"name": "Test Legacy Bank", "description": "Bank App Analysis"},
        )
        assert resp.status_code == 201
        project_data = resp.json()
        project_id = project_data["id"]

        # 2. Upload valid Spring Maven ZIP repository
        zip_path = FIXTURES_DIR / "valid-spring-maven.zip"
        with open(zip_path, "rb") as f:
            files = {"file": ("valid-spring-maven.zip", f, "application/zip")}
            upload_resp = await client.post(
                f"/api/v1/projects/{project_id}/repositories",
                files=files,
            )

        assert upload_resp.status_code == 201
        repo_data = upload_resp.json()
        repo_id = repo_data["id"]
        assert repo_data["status"] == "COMPLETED"
        assert len(repo_data["sha256"]) == 64

        # 3. Get repository manifest
        manifest_resp = await client.get(f"/api/v1/repositories/{repo_id}/manifest")
        assert manifest_resp.status_code == 200
        manifest = manifest_resp.json()
        assert manifest["summary"]["total_files"] >= 3
        tech_names = [t["name"] for t in manifest["technologies"]]
        assert "Java" in tech_names
        assert "Maven" in tech_names
        assert "Spring" in tech_names

        # 4. Get file list
        files_resp = await client.get(f"/api/v1/repositories/{repo_id}/files")
        assert files_resp.status_code == 200
        files_list = files_resp.json()
        assert len(files_list) >= 3

        # 5. Read file content
        content_resp = await client.get(
            f"/api/v1/repositories/{repo_id}/files/content?path=pom.xml"
        )
        assert content_resp.status_code == 200
        content_data = content_resp.json()
        assert "spring-boot-starter-web" in content_data["content"]


@pytest.mark.asyncio
async def test_upload_malicious_zip_slip_rejected():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        # Create project
        resp = await client.post(
            "/api/v1/projects",
            json={"name": "Malicious Test Project"},
        )
        project_id = resp.json()["id"]

        # Upload malicious Zip Slip
        zip_path = FIXTURES_DIR / "malicious-zip-slip.zip"
        with open(zip_path, "rb") as f:
            files = {"file": ("malicious-zip-slip.zip", f, "application/zip")}
            upload_resp = await client.post(
                f"/api/v1/projects/{project_id}/repositories",
                files=files,
            )

        assert upload_resp.status_code == 400
        assert "PATH_TRAVERSAL_DETECTED" in upload_resp.json()["detail"]
