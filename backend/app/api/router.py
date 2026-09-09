"""
LEGACYX — API v1 Router.

Aggregates all route modules under the /api/v1 prefix.
"""

from fastapi import APIRouter

from app.api import analysis, business_rules, health, impact, modernization, projects, repositories, validation

api_router = APIRouter(prefix="/api/v1")

# ── Phase 1 ───────────────────────────────────────────────────────────────────
api_router.include_router(health.router)

# ── Phase 2 ───────────────────────────────────────────────────────────────────
api_router.include_router(projects.router)
api_router.include_router(repositories.router)

# ── Phase 3 ───────────────────────────────────────────────────────────────────
api_router.include_router(analysis.router)

# ── Phase 4 ───────────────────────────────────────────────────────────────────
api_router.include_router(business_rules.router)

# ── Phase 5 ───────────────────────────────────────────────────────────────────
api_router.include_router(impact.router)

# ── Phase 6 & 7 & 8 ─────────────────────────────────────────────────────────
api_router.include_router(modernization.router)

# ── Phase 9 ───────────────────────────────────────────────────────────────────
api_router.include_router(validation.router)



