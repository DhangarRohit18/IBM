"""
LEGACYX — Database Initialization Helper.

Checks database connectivity and can run basic setup tasks.
Used in the application lifespan hook to fail fast if the DB is unreachable.
"""

from sqlalchemy import text

from app.db.base import async_engine
from app.core.logging import get_logger

logger = get_logger(__name__)


async def check_db_connection() -> bool:
    """Verify that the database is reachable.

    Returns:
        True if connection succeeds.

    Raises:
        Exception: If the database is not reachable.
    """
    async with async_engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("database_connection_ok")
    return True
