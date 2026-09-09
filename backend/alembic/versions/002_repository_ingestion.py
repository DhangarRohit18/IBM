"""
Phase 2 migration: create repositories, repository_files, and ingestion_runs tables.

Revision ID: 002_repository_ingestion
Revises: 001_initial
Create Date: Phase 2
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_repository_ingestion"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:


    # ── repositories ───────────────────────────────────────────────────────────
    op.create_table(
        "repositories",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("project_id", sa.String(36), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("artifact_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("storage_key", sa.String(512), nullable=False),
        sa.Column("extracted_path", sa.String(512), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "UPLOADED", "VALIDATING", "EXTRACTING", "INDEXING", "COMPLETED", "FAILED",
                name="repository_status",
            ),
            nullable=False,
            server_default="UPLOADED",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_repositories_id", "repositories", ["id"], unique=False)
    op.create_index("ix_repositories_project_id", "repositories", ["project_id"], unique=True)
    op.create_index("ix_repositories_sha256", "repositories", ["sha256"], unique=False)
    op.create_index("ix_repositories_status", "repositories", ["status"], unique=False)

    # ── repository_files ───────────────────────────────────────────────────────
    op.create_table(
        "repository_files",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("repository_id", sa.String(36), nullable=False),
        sa.Column("relative_path", sa.String(1024), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("extension", sa.String(64), nullable=False, server_default=""),
        sa.Column("size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_directory", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("checksum", sa.String(64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_repository_files_id", "repository_files", ["id"], unique=False)
    op.create_index("ix_repository_files_repository_id", "repository_files", ["repository_id"], unique=False)
    op.create_index("idx_repo_file_repo_relpath", "repository_files", ["repository_id", "relative_path"], unique=False)
    op.create_index("idx_repo_file_extension", "repository_files", ["extension"], unique=False)

    # ── ingestion_runs ─────────────────────────────────────────────────────────
    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("repository_id", sa.String(36), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "STARTED", "COMPLETED", "FAILED",
                name="ingestion_status",
            ),
            nullable=False,
            server_default="STARTED",
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("files_discovered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("directories_discovered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bytes_extracted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_code", sa.String(64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ingestion_runs_id", "ingestion_runs", ["id"], unique=False)
    op.create_index("ix_ingestion_runs_repository_id", "ingestion_runs", ["repository_id"], unique=False)
    op.create_index("ix_ingestion_runs_status", "ingestion_runs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ingestion_runs_status", table_name="ingestion_runs")
    op.drop_index("ix_ingestion_runs_repository_id", table_name="ingestion_runs")
    op.drop_index("ix_ingestion_runs_id", table_name="ingestion_runs")
    op.drop_table("ingestion_runs")

    op.drop_index("idx_repo_file_extension", table_name="repository_files")
    op.drop_index("idx_repo_file_repo_relpath", table_name="repository_files")
    op.drop_index("ix_repository_files_repository_id", table_name="repository_files")
    op.drop_index("ix_repository_files_id", table_name="repository_files")
    op.drop_table("repository_files")

    op.drop_index("ix_repositories_status", table_name="repositories")
    op.drop_index("ix_repositories_sha256", table_name="repositories")
    op.drop_index("ix_repositories_project_id", table_name="repositories")
    op.drop_index("ix_repositories_id", table_name="repositories")
    op.drop_table("repositories")

    sa.Enum(name="ingestion_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="repository_status").drop(op.get_bind(), checkfirst=True)
