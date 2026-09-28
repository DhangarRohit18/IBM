"""
LEGACYX — Decision Contract ORM Model (Feature 2).

Represents a language-agnostic behavioral contract specifying expected business decisions,
preconditions, input specifications, and outputs against which modernization is validated.
"""

from datetime import datetime, timezone
import enum
from typing import Any
import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class ContractStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DRAFT = "DRAFT"
    DEPRECATED = "DEPRECATED"
    LOCKED = "LOCKED"


class DecisionContract(Base):
    """
    Decision Contract Model.
    Decouples business specification from implementation code.
    """
    __tablename__ = "decision_contracts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    contract_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # e.g. "CLAIM-ELIGIBILITY-001"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_domain: Mapped[str] = mapped_column(String(64), default="FINANCIAL_SERVICES", nullable=False)
    
    repository_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business_rule_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("business_rules.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Contract Specification
    inputs: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    conditions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    expected_decision: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g. "APPROVE", "MANUAL_REVIEW"
    expected_outputs: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[ContractStatus] = mapped_column(
        String(32), default=ContractStatus.ACTIVE, nullable=False, index=True
    )
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Audit & Evidence
    evidence: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

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

    # Relationships
    repository = relationship("Repository", backref="decision_contracts")
    analysis_run = relationship("AnalysisRun", backref="decision_contracts")
    business_rule = relationship("BusinessRule", backref="decision_contracts")

    def __repr__(self) -> str:
        return f"<DecisionContract id='{self.id}' contract_id='{self.contract_id}' expected='{self.expected_decision}'>"
