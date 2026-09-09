"""
Phase 7 migration: create modernization_plans and modernization_tasks tables.

Revision ID: 006_modernization_execution_plan
Revises: 005_modernization_strategy
Create Date: Phase 7
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006_modernization_execution_plan"
down_revision: Union[str, None] = "005_modernization_strategy"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "modernization_plans",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("analysis_id", sa.String(length=36), nullable=False),
        sa.Column("repository_id", sa.String(length=36), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("strategy_id", sa.String(length=36), nullable=True),
        sa.Column("entity_name", sa.String(length=255), nullable=False),
        sa.Column("relative_file_path", sa.String(length=512), nullable=False),
        sa.Column("strategy_type", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PROPOSED"),
        sa.Column("rules_to_preserve", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("impact_summary", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("verification_checkpoints", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("reviewed_by", sa.String(length=128), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("ai_explanation", sa.Text(), nullable=True),
        sa.Column("ai_explanation_status", sa.String(length=32), nullable=False, server_default="NOT_REQUESTED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["analysis_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["entity_id"], ["code_entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["strategy_id"], ["modernization_strategies.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_modernization_plans_analysis_id", "modernization_plans", ["analysis_id"], unique=False)
    op.create_index("ix_modernization_plans_repository_id", "modernization_plans", ["repository_id"], unique=False)
    op.create_index("ix_modernization_plans_entity_id", "modernization_plans", ["entity_id"], unique=False)
    op.create_index("ix_modernization_plans_status", "modernization_plans", ["status"], unique=False)

    op.create_table(
        "modernization_tasks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("plan_id", sa.String(length=36), nullable=False),
        sa.Column("sequence_order", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("task_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PENDING"),
        sa.Column("target_component", sa.String(length=255), nullable=False),
        sa.Column("target_file_path", sa.String(length=512), nullable=False),
        sa.Column("depends_on_task_ids", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("rule_ids", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("evidence_references", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("verification_checkpoint", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["plan_id"], ["modernization_plans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_modernization_tasks_plan_id", "modernization_tasks", ["plan_id"], unique=False)
    op.create_index("ix_modernization_tasks_sequence_order", "modernization_tasks", ["sequence_order"], unique=False)
    op.create_index("ix_modernization_tasks_task_type", "modernization_tasks", ["task_type"], unique=False)
    op.create_index("ix_modernization_tasks_status", "modernization_tasks", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_modernization_tasks_status", table_name="modernization_tasks")
    op.drop_index("ix_modernization_tasks_task_type", table_name="modernization_tasks")
    op.drop_index("ix_modernization_tasks_sequence_order", table_name="modernization_tasks")
    op.drop_index("ix_modernization_tasks_plan_id", table_name="modernization_tasks")
    op.drop_table("modernization_tasks")

    op.drop_index("ix_modernization_plans_status", table_name="modernization_plans")
    op.drop_index("ix_modernization_plans_entity_id", table_name="modernization_plans")
    op.drop_index("ix_modernization_plans_repository_id", table_name="modernization_plans")
    op.drop_index("ix_modernization_plans_analysis_id", table_name="modernization_plans")
    op.drop_table("modernization_plans")
