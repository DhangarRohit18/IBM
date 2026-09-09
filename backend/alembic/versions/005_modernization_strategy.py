"""
Phase 6 migration: create modernization_strategies table.

Revision ID: 005_modernization_strategy
Revises: 004_business_rules
Create Date: Phase 6
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005_modernization_strategy"
down_revision: Union[str, None] = "004_business_rules"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "modernization_strategies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("analysis_id", sa.String(length=36), nullable=False),
        sa.Column("repository_id", sa.String(length=36), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("entity_name", sa.String(length=255), nullable=False),
        sa.Column("relative_file_path", sa.String(length=512), nullable=False),
        sa.Column("recommended_strategy", sa.String(length=64), nullable=False),
        sa.Column("alternative_strategy", sa.String(length=64), nullable=True),
        sa.Column("why_recommended", sa.Text(), nullable=False),
        sa.Column("why_alternative", sa.Text(), nullable=True),
        sa.Column("what_not_to_change", sa.Text(), nullable=True),
        sa.Column("decision_trace", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("observed_responsibilities", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("rules_to_preserve", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("impact_summary", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("qualitative_comparison", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PROPOSED"),
        sa.Column("user_override_strategy", sa.String(length=64), nullable=True),
        sa.Column("user_override_by", sa.String(length=128), nullable=True),
        sa.Column("user_override_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_override_notes", sa.Text(), nullable=True),
        sa.Column("ai_explanation", sa.Text(), nullable=True),
        sa.Column("ai_explanation_status", sa.String(length=32), nullable=False, server_default="NOT_REQUESTED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["analysis_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["entity_id"], ["code_entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_modernization_strategies_analysis_id", "modernization_strategies", ["analysis_id"], unique=False)
    op.create_index("ix_modernization_strategies_repository_id", "modernization_strategies", ["repository_id"], unique=False)
    op.create_index("ix_modernization_strategies_entity_id", "modernization_strategies", ["entity_id"], unique=False)
    op.create_index("ix_modernization_strategies_recommended_strategy", "modernization_strategies", ["recommended_strategy"], unique=False)
    op.create_index("ix_modernization_strategies_status", "modernization_strategies", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_modernization_strategies_status", table_name="modernization_strategies")
    op.drop_index("ix_modernization_strategies_recommended_strategy", table_name="modernization_strategies")
    op.drop_index("ix_modernization_strategies_entity_id", table_name="modernization_strategies")
    op.drop_index("ix_modernization_strategies_repository_id", table_name="modernization_strategies")
    op.drop_index("ix_modernization_strategies_analysis_id", table_name="modernization_strategies")
    op.drop_table("modernization_strategies")
