"""
Phase 4 migration: create business_rules table.

Revision ID: 004_business_rules
Revises: 003_system_xray
Create Date: Phase 4
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_business_rules"
down_revision: Union[str, None] = "003_system_xray"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "business_rules",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("analysis_id", sa.String(length=36), nullable=False),
        sa.Column("repository_id", sa.String(length=36), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=True),
        sa.Column("method_id", sa.String(length=36), nullable=True),
        sa.Column("rule_type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="EXTRACTED"),
        sa.Column("condition_expression", sa.Text(), nullable=True),
        sa.Column("action_expression", sa.Text(), nullable=True),
        sa.Column("outcome_expression", sa.Text(), nullable=True),
        sa.Column("threshold_value", sa.String(length=128), nullable=True),
        sa.Column("threshold_operator", sa.String(length=16), nullable=True),
        sa.Column("calculation_formula", sa.Text(), nullable=True),
        sa.Column("previous_state", sa.String(length=128), nullable=True),
        sa.Column("new_state", sa.String(length=128), nullable=True),
        sa.Column("rule_trace", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("relative_file_path", sa.String(length=512), nullable=False),
        sa.Column("line_start", sa.Integer(), nullable=False),
        sa.Column("line_end", sa.Integer(), nullable=False),
        sa.Column("source_construct", sa.String(length=128), nullable=False),
        sa.Column("extraction_reason", sa.Text(), nullable=False),
        sa.Column("ai_explanation", sa.Text(), nullable=True),
        sa.Column("ai_explanation_status", sa.String(length=32), nullable=False, server_default="NOT_REQUESTED"),
        sa.Column("reviewed_by", sa.String(length=128), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["analysis_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["entity_id"], ["code_entities.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["method_id"], ["code_methods.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_business_rules_analysis_id", "business_rules", ["analysis_id"], unique=False)
    op.create_index("ix_business_rules_repository_id", "business_rules", ["repository_id"], unique=False)
    op.create_index("ix_business_rules_entity_id", "business_rules", ["entity_id"], unique=False)
    op.create_index("ix_business_rules_method_id", "business_rules", ["method_id"], unique=False)
    op.create_index("ix_business_rules_rule_type", "business_rules", ["rule_type"], unique=False)
    op.create_index("ix_business_rules_status", "business_rules", ["status"], unique=False)
    op.create_index("ix_business_rules_relative_file_path", "business_rules", ["relative_file_path"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_business_rules_relative_file_path", table_name="business_rules")
    op.drop_index("ix_business_rules_status", table_name="business_rules")
    op.drop_index("ix_business_rules_rule_type", table_name="business_rules")
    op.drop_index("ix_business_rules_method_id", table_name="business_rules")
    op.drop_index("ix_business_rules_entity_id", table_name="business_rules")
    op.drop_index("ix_business_rules_repository_id", table_name="business_rules")
    op.drop_index("ix_business_rules_analysis_id", table_name="business_rules")
    op.drop_table("business_rules")
