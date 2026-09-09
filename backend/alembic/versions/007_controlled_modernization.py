"""
Phase 8 migration: create transformation_proposals and transformation_artifacts tables.

Revision ID: 007_controlled_modernization
Revises: 006_modernization_execution_plan
Create Date: Phase 8
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007_controlled_modernization"
down_revision: Union[str, None] = "006_modernization_execution_plan"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "transformation_proposals",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("plan_id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("analysis_id", sa.String(length=36), nullable=False),
        sa.Column("repository_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PROPOSED"),
        sa.Column("transformation_type", sa.String(length=64), nullable=False),
        sa.Column("target_entity", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("specification", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("rule_ids", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("impacted_entity_ids", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("reviewed_by", sa.String(length=128), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("applied_by", sa.String(length=128), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("storage_workspace_path", sa.String(length=512), nullable=True),
        sa.Column("ai_proposal_status", sa.String(length=32), nullable=False, server_default="NOT_REQUESTED"),
        sa.Column("ai_proposal_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["plan_id"], ["modernization_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["modernization_tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["analysis_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transformation_proposals_plan_id", "transformation_proposals", ["plan_id"], unique=False)
    op.create_index("ix_transformation_proposals_task_id", "transformation_proposals", ["task_id"], unique=False)
    op.create_index("ix_transformation_proposals_analysis_id", "transformation_proposals", ["analysis_id"], unique=False)
    op.create_index("ix_transformation_proposals_status", "transformation_proposals", ["status"], unique=False)

    op.create_table(
        "transformation_artifacts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("proposal_id", sa.String(length=36), nullable=False),
        sa.Column("artifact_category", sa.String(length=64), nullable=False),
        sa.Column("target_file_path", sa.String(length=512), nullable=False),
        sa.Column("source_file_path", sa.String(length=512), nullable=False),
        sa.Column("source_line_start", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("source_line_end", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("generated_code", sa.Text(), nullable=False),
        sa.Column("diff_content", sa.Text(), nullable=False),
        sa.Column("rules_preserved", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("evidence_references", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("storage_relative_path", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["proposal_id"], ["transformation_proposals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transformation_artifacts_proposal_id", "transformation_artifacts", ["proposal_id"], unique=False)
    op.create_index("ix_transformation_artifacts_category", "transformation_artifacts", ["artifact_category"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_transformation_artifacts_category", table_name="transformation_artifacts")
    op.drop_index("ix_transformation_artifacts_proposal_id", table_name="transformation_artifacts")
    op.drop_table("transformation_artifacts")

    op.drop_index("ix_transformation_proposals_status", table_name="transformation_proposals")
    op.drop_index("ix_transformation_proposals_analysis_id", table_name="transformation_proposals")
    op.drop_index("ix_transformation_proposals_task_id", table_name="transformation_proposals")
    op.drop_index("ix_transformation_proposals_plan_id", table_name="transformation_proposals")
    op.drop_table("transformation_proposals")
