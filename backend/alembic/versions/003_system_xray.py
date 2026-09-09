"""
Phase 3 migration: create analysis_runs, code_packages, code_entities, code_methods, code_fields, and code_relationships tables.

Revision ID: 003_system_xray
Revises: 002_repository_ingestion
Create Date: Phase 3
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_system_xray"
down_revision: Union[str, None] = "002_repository_ingestion"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:


    # ── analysis_runs ──────────────────────────────────────────────────────────
    op.create_table(
        "analysis_runs",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("repository_id", sa.String(36), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "RUNNING", "COMPLETED", "FAILED", name="analysis_run_status"),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("parser_name", sa.String(64), nullable=False, server_default="javalang"),
        sa.Column("parser_version", sa.String(32), nullable=False, server_default="0.13.0"),
        sa.Column("files_analyzed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("packages_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("classes_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("interfaces_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enums_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("methods_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fields_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("relationships_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_code", sa.String(64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analysis_runs_id", "analysis_runs", ["id"], unique=False)
    op.create_index("ix_analysis_runs_repository_id", "analysis_runs", ["repository_id"], unique=False)
    op.create_index("ix_analysis_runs_status", "analysis_runs", ["status"], unique=False)

    # ── code_packages ──────────────────────────────────────────────────────────
    op.create_table(
        "code_packages",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("analysis_id", sa.String(36), nullable=False),
        sa.Column("repository_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_code_packages_id", "code_packages", ["id"], unique=False)
    op.create_index("ix_code_packages_analysis_id", "code_packages", ["analysis_id"], unique=False)
    op.create_index("ix_code_packages_repository_id", "code_packages", ["repository_id"], unique=False)
    op.create_index("idx_code_pkg_analysis_name", "code_packages", ["analysis_id", "name"], unique=False)

    # ── code_entities ──────────────────────────────────────────────────────────
    op.create_table(
        "code_entities",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("analysis_id", sa.String(36), nullable=False),
        sa.Column("repository_id", sa.String(36), nullable=False),
        sa.Column("package_id", sa.String(36), nullable=True),
        sa.Column("entity_type", sa.Enum("CLASS", "INTERFACE", "ENUM", name="entity_type"), nullable=False, server_default="CLASS"),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("fully_qualified_name", sa.String(512), nullable=False),
        sa.Column("relative_file_path", sa.String(1024), nullable=False),
        sa.Column("line_start", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("line_end", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("extends_name", sa.String(512), nullable=True),
        sa.Column("implements_names", sa.JSON(), nullable=False),
        sa.Column("annotations", sa.JSON(), nullable=False),
        sa.Column("modifiers", sa.JSON(), nullable=False),
        sa.Column("component_type", sa.Enum("CONTROLLER", "SERVICE", "REPOSITORY", "MODEL", "CONFIG", "UTILITY", "OTHER", name="component_type"), nullable=False, server_default="OTHER"),
        sa.Column("classification_evidence", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["package_id"], ["code_packages.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_code_entities_id", "code_entities", ["id"], unique=False)
    op.create_index("ix_code_entities_analysis_id", "code_entities", ["analysis_id"], unique=False)
    op.create_index("ix_code_entities_name", "code_entities", ["name"], unique=False)
    op.create_index("idx_code_entity_fqn", "code_entities", ["analysis_id", "fully_qualified_name"], unique=False)
    op.create_index("idx_code_entity_component", "code_entities", ["analysis_id", "component_type"], unique=False)

    # ── code_methods ───────────────────────────────────────────────────────────
    op.create_table(
        "code_methods",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("analysis_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("return_type", sa.String(255), nullable=False, server_default="void"),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("modifiers", sa.JSON(), nullable=False),
        sa.Column("annotations", sa.JSON(), nullable=False),
        sa.Column("is_constructor", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("line_start", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("line_end", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["code_entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["analysis_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_code_methods_id", "code_methods", ["id"], unique=False)
    op.create_index("idx_code_method_entity_name", "code_methods", ["entity_id", "name"], unique=False)

    # ── code_fields ────────────────────────────────────────────────────────────
    op.create_table(
        "code_fields",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("analysis_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("field_type", sa.String(255), nullable=False),
        sa.Column("modifiers", sa.JSON(), nullable=False),
        sa.Column("annotations", sa.JSON(), nullable=False),
        sa.Column("line_start", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("line_end", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["code_entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["analysis_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_code_fields_id", "code_fields", ["id"], unique=False)
    op.create_index("idx_code_field_entity_name", "code_fields", ["entity_id", "name"], unique=False)

    # ── code_relationships ─────────────────────────────────────────────────────
    op.create_table(
        "code_relationships",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("analysis_id", sa.String(36), nullable=False),
        sa.Column("source_entity_id", sa.String(36), nullable=False),
        sa.Column("source_method_id", sa.String(36), nullable=True),
        sa.Column("target_entity_id", sa.String(36), nullable=True),
        sa.Column("target_entity_name", sa.String(512), nullable=False),
        sa.Column("relationship_type", sa.Enum("IMPORTS", "EXTENDS", "IMPLEMENTS", "DEPENDS_ON", "CALLS", name="relationship_type"), nullable=False),
        sa.Column("relative_file_path", sa.String(1024), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("source_construct", sa.String(512), nullable=False, server_default=""),
        sa.Column("evidence_reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("is_resolved", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_entity_id"], ["code_entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_method_id"], ["code_methods.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_entity_id"], ["code_entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_code_relationships_id", "code_relationships", ["id"], unique=False)
    op.create_index("idx_code_rel_src_target", "code_relationships", ["source_entity_id", "target_entity_id"], unique=False)
    op.create_index("idx_code_rel_type", "code_relationships", ["analysis_id", "relationship_type"], unique=False)


def downgrade() -> None:
    op.drop_table("code_relationships")
    op.drop_table("code_fields")
    op.drop_table("code_methods")
    op.drop_table("code_entities")
    op.drop_table("code_packages")
    op.drop_table("analysis_runs")

    sa.Enum(name="relationship_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="component_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="entity_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="analysis_run_status").drop(op.get_bind(), checkfirst=True)
