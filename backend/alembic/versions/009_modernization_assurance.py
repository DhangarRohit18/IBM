"""
Modernization Assurance migration: Business Rule DNA, Decision Contracts, Decision Replay & Drift Detection.

Revision ID: 009_modernization_assurance
Revises: 008_validation
Create Date: Modernization Assurance
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009_modernization_assurance"
down_revision: Union[str, None] = "008_validation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Enhance business_rules with Business Rule DNA columns ─────────────
    # Use batch_alter_table for SQLite compatibility
    with op.batch_alter_table("business_rules") as batch_op:
        batch_op.add_column(sa.Column("business_meaning", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("inputs", sa.JSON(), nullable=False, server_default="[]"))
        batch_op.add_column(sa.Column("outputs", sa.JSON(), nullable=False, server_default="[]"))
        batch_op.add_column(sa.Column("dependencies", sa.JSON(), nullable=False, server_default="[]"))
        batch_op.add_column(sa.Column("related_apis", sa.JSON(), nullable=False, server_default="[]"))
        batch_op.add_column(sa.Column("related_db_fields", sa.JSON(), nullable=False, server_default="[]"))
        batch_op.add_column(sa.Column("related_business_processes", sa.JSON(), nullable=False, server_default="[]"))
        batch_op.add_column(sa.Column("related_tests", sa.JSON(), nullable=False, server_default="[]"))
        batch_op.add_column(sa.Column("confidence", sa.Float(), nullable=False, server_default="1.0"))
        batch_op.add_column(sa.Column("evidence_snippet", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("is_locked", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column("is_critical", sa.Boolean(), nullable=False, server_default=sa.false()))

    # ── 2. Create decision_contracts table ───────────────────────────────────
    op.create_table(
        "decision_contracts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("contract_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("business_domain", sa.String(length=64), nullable=False, server_default="FINANCIAL_SERVICES"),
        sa.Column("repository_id", sa.String(length=36), sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("analysis_id", sa.String(length=36), sa.ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("business_rule_id", sa.String(length=36), sa.ForeignKey("business_rules.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("inputs", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("conditions", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("expected_decision", sa.String(length=64), nullable=False),
        sa.Column("expected_outputs", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="ACTIVE", index=True),
        sa.Column("is_critical", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("evidence", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )

    # ── 3. Create decision_replay_runs table ─────────────────────────────────
    op.create_table(
        "decision_replay_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("repository_id", sa.String(length=36), sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("proposal_id", sa.String(length=36), sa.ForeignKey("transformation_proposals.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("validation_run_id", sa.String(length=36), sa.ForeignKey("validation_runs.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="COMPLETED", index=True),
        sa.Column("total_scenarios", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("preserved_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("drift_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unknown_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("risk_assessment", sa.String(length=32), nullable=False, server_default="LOW"),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("executed_by", sa.String(length=128), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── 4. Create decision_scenario_results table ────────────────────────────
    op.create_table(
        "decision_scenario_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("replay_run_id", sa.String(length=36), sa.ForeignKey("decision_replay_runs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("scenario_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("scenario_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("scenario_name", sa.String(length=255), nullable=False),
        sa.Column("scenario_category", sa.String(length=64), nullable=False, server_default="BOUNDARY_THRESHOLD"),
        sa.Column("contract_id", sa.String(length=64), nullable=True, index=True),
        sa.Column("business_rule_id", sa.String(length=36), nullable=True, index=True),
        sa.Column("input_payload", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("legacy_decision", sa.String(length=64), nullable=False),
        sa.Column("legacy_output", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("legacy_rule_path", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("legacy_execution_time_ms", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("modern_decision", sa.String(length=64), nullable=False),
        sa.Column("modern_output", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("modern_rule_path", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("modern_execution_time_ms", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("comparison_status", sa.String(length=32), nullable=False, server_default="PRESERVED", index=True),
        sa.Column("drift_type", sa.String(length=32), nullable=False, server_default="NONE", index=True),
        sa.Column("drift_severity", sa.String(length=32), nullable=False, server_default="NONE", index=True),
        sa.Column("drift_details", sa.Text(), nullable=True),
        sa.Column("drift_root_cause", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("remediation_suggestion", sa.Text(), nullable=True),
        sa.Column("evidence_chain", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("reviewed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("reviewed_by", sa.String(length=128), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("decision_scenario_results")
    op.drop_table("decision_replay_runs")
    op.drop_table("decision_contracts")
    with op.batch_alter_table("business_rules") as batch_op:
        batch_op.drop_column("is_critical")
        batch_op.drop_column("is_locked")
        batch_op.drop_column("evidence_snippet")
        batch_op.drop_column("confidence")
        batch_op.drop_column("related_tests")
        batch_op.drop_column("related_business_processes")
        batch_op.drop_column("related_db_fields")
        batch_op.drop_column("related_apis")
        batch_op.drop_column("dependencies")
        batch_op.drop_column("outputs")
        batch_op.drop_column("inputs")
        batch_op.drop_column("business_meaning")
