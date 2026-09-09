"""
LEGACYX — Alembic Environment.

Reads database connection URL from the environment (never hardcoded).
Imports all ORM models so autogenerate detects the full schema.

Usage:
  # From backend/ directory:
  alembic revision --autogenerate -m "description"
  alembic upgrade head
"""

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ── Import all models so autogenerate detects them ────────────────────────────
# This must include every model in the project.
from app.models import Base  # noqa: F401 — must import to register metadata
from app.models.user import User  # noqa: F401
from app.models.project import Project  # noqa: F401

# ── Alembic Config ────────────────────────────────────────────────────────────
config = context.config

# Override sqlalchemy.url with the environment variable.
# This ensures secrets are never committed to alembic.ini.
database_sync_url = os.environ.get(
    "DATABASE_SYNC_URL",
    "postgresql+psycopg2://legacyx:legacyx_dev_password@localhost:5432/legacyx",
)
config.set_main_option("sqlalchemy.url", database_sync_url)

# Logging config from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (SQL script output)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with a live DB connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,       # detect column type changes
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
