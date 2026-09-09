"""
LEGACYX — CodeField ORM Model (Phase 3).

Represents a Java class/interface field declaration with type, modifiers, and annotations.
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class CodeField(Base):
    """A Java field inside an entity."""

    __tablename__ = "code_fields"

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
    field_type: Mapped[str] = mapped_column(String(255), nullable=False)
    modifiers: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    annotations: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)

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
        "CodeEntity", back_populates="fields"
    )

    __table_args__ = (
        Index("idx_code_field_entity_name", "entity_id", "name"),
    )

    def __repr__(self) -> str:
        return f"<CodeField name={self.name!r} type={self.field_type!r}>"
