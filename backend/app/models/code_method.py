"""
LEGACYX — CodeMethod ORM Model (Phase 3).

Represents a Java method or constructor declaration with parameter types, return types,
annotations, and exact line number evidence.
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class CodeMethod(Base):
    """A Java method or constructor inside an entity."""

    __tablename__ = "code_methods"

    # ── Primary Key ────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )

    # ── Foreign Keys ───────────────────────────────────────────────────────────
    entity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("code_entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    analysis_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Attributes ─────────────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    return_type: Mapped[str] = mapped_column(String(255), nullable=False, default="void")
    parameters: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    modifiers: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    annotations: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    is_constructor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ── Source Evidence ────────────────────────────────────────────────────────
    line_start: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    line_end: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # ── Timestamp ──────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    entity: Mapped["CodeEntity"] = relationship(  # noqa: F821
        "CodeEntity", back_populates="methods"
    )

    __table_args__ = (
        Index("idx_code_method_entity_name", "entity_id", "name"),
    )

    def __repr__(self) -> str:
        return f"<CodeMethod name={self.name!r} return={self.return_type!r}>"
