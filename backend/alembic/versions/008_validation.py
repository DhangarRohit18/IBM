"""
Phase 9 migration: create validation_runs, validation_evidences, and behavioral_scenarios tables.

Revision ID: 008_validation
Revises: 007_controlled_modernization
Create Date: Phase 9
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "008_validation"
down_revision: Union[str, None] = "007_controlled_modernization"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "validation_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("transformation_proposal_id", sa.String(length=36), nullable=False),
        sa.Column("plan_id", sa.String(length=36), nullable=False),
        sa.Column("repository_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PROPOSED"),
        sa.Column("environment_status", sa.String(length=32), nullable=False, server_default="ENVIRONMENT_READY"),
        sa.Column("build_status", sa.String(length=32), nullable=False, server_default="NOT_RUN"),
        sa.Column("test_status", sa.String(length=32), nullable=False, server_default="NOT_RUN"),
        sa.Column("behavioral_status", sa.String(length=32), nullable=False, server_default="NOT_RUN"),
        sa.Column("overall_status", sa.String(length=32), nullable=False, server_default="VALIDATION_BLOCKED"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.String(length=128), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("ai_explanation", sa.Text(), nullable=True),
        sa.Column("ai_explanation_status", sa.String(length=32), nullable=False, server_default="NOT_REQUESTED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["transformation_proposal_id"], ["transformation_proposals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["modernization_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_validation_runs_proposal_id", "validation_runs", ["transformation_proposal_id"], unique=False)
    op.create_index("ix_validation_runs_plan_id", "validation_runs", ["plan_id"], unique=False)
    op.create_index("ix_validation_runs_status", "validation_runs", ["status"], unique=False)
    op.create_index("ix_validation_runs_overall_status", "validation_runs", ["overall_status"], unique=False)

    op.create_table(
        "validation_evidences",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("validation_run_id", sa.String(length=36), nullable=False),
        sa.Column("stage", sa.String(length=32), nullable=False),
        sa.Column("command", sa.Text(), nullable=False),
        sa.Column("exit_code", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("stdout", sa.Text(), nullable=False, server_default=""),
        sa.Column("stderr", sa.Text(), nullable=False, server_default=""),
        sa.Column("duration_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["validation_run_id"], ["validation_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_validation_evidences_run_id", "validation_evidences", ["validation_run_id"], unique=False)
    op.create_index("ix_validation_evidences_stage", "validation_evidences", ["stage"], unique=False)

    op.create_table(
        "behavioral_scenarios",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("validation_run_id", sa.String(length=36), nullable=False),
        sa.Column("business_rule_id", sa.String(length=36), nullable=False),
        sa.Column("scenario_name", sa.String(length=255), nullable=False),
        sa.Column("input_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("legacy_output_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("modernized_output_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("comparison_result", sa.String(length=32), nullable=False, server_default="UNABLE_TO_VALIDATE"),
        sa.Column("evidence_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["validation_run_id"], ["validation_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_behavioral_scenarios_run_id", "behavioral_scenarios", ["validation_run_id"], unique=False)
    op.create_index("ix_behavioral_scenarios_rule_id", "behavioral_scenarios", ["business_rule_id"], unique=False)
    op.create_index("ix_behavioral_scenarios_result", "behavioral_scenarios", ["comparison_result"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_behavioral_scenarios_result", table_name="behavioral_scenarios")
    op.drop_index("ix_behavioral_scenarios_rule_id", table_name="behavioral_scenarios")
    op.drop_index("ix_behavioral_scenarios_run_id", table_name="behavioral_scenarios")
    op.drop_table("behavioral_scenarios")

    op.drop_index("ix_validation_evidences_stage", table_name="validation_evidences")
    op.drop_index("ix_validation_evidences_run_id", table_name="validation_evidences")
    op.drop_table("validation_evidences")

    op.drop_index("ix_validation_runs_overall_status", table_name="validation_runs")
    op.drop_index("ix_validation_runs_status", table_name="validation_runs")
    op.drop_index("ix_validation_runs_plan_id", table_name="validation_runs")
    op.drop_index("ix_validation_runs_proposal_id", table_name="validation_runs")
    op.drop_table("validation_runs")
