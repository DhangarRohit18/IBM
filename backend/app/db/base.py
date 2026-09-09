"""
LEGACYX — Database Engine & Session Factory.

Uses SQLAlchemy 2.x async engine with asyncpg driver.
Alembic uses a separate sync engine (psycopg2) — see alembic/env.py.

All database access from the application layer must go through
get_async_session(), never through direct engine access.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# ── Async Engine ───────────────────────────────────────────────────────────────
engine_kwargs: dict = {
    "pool_pre_ping": True,
    "echo": False,
}
if "sqlite" not in settings.database_url:
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

async_engine = create_async_engine(
    settings.database_url,
    **engine_kwargs,
)

# ── Session Factory ────────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session.

    Usage in route:
        async def my_route(db: AsyncSession = Depends(get_async_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
