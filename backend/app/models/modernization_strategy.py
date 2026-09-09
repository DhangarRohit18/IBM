"""
LEGACYX — ModernizationStrategy ORM Model (Phase 6).

Stores evidence-backed modernization strategy recommendations, decision traces,
observed AST responsibilities, preserved business rules, impact summaries,
and auditable human review/override history.
"""

from datetime import datetime, timezone
import enum
from typing import Any
import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class StrategyStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    REVIEWED = "REVIEWED"
    OVERRIDDEN = "OVERRIDDEN"


class ModernizationStrategy(Base):
    """
    ModernizationStrategy ORM Model.
    Stores deterministic strategy recommendation, decision trace, and auditable human override.
    """
    __tablename__ = "modernization_strategies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    repository_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("code_entities.id", ondelete="CASCADE"), nullable=False, index=True
    )

    entity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    relative_file_path: Mapped[str] = mapped_column(String(512), nullable=False)

    recommended_strategy: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    alternative_strategy: Mapped[str] = mapped_column(String(64), nullable=True)

    why_recommended: Mapped[str] = mapped_column(Text, nullable=False)
    why_alternative: Mapped[str] = mapped_column(Text, nullable=True)
    what_not_to_change: Mapped[str] = mapped_column(Text, nullable=True)

    # Deterministic Traces & Evidence
    decision_trace: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    observed_responsibilities: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    rules_to_preserve: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    impact_summary: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    qualitative_comparison: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)

    # Auditable Human Override Workflow
    status: Mapped[StrategyStatus] = mapped_column(
        String(32), default=StrategyStatus.PROPOSED, nullable=False, index=True
    )
    user_override_strategy: Mapped[str] = mapped_column(String(64), nullable=True)
    user_override_by: Mapped[str] = mapped_column(String(128), nullable=True)
    user_override_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    user_override_notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Optional AI Gateway Narrative Explanation
    ai_explanation: Mapped[str] = mapped_column(Text, nullable=True)
    ai_explanation_status: Mapped[str] = mapped_column(String(32), default="NOT_REQUESTED", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
