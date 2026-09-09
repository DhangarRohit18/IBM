"""
LEGACYX — User ORM Model.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class User(Base, TimestampMixin):
    """Platform user account."""

    __tablename__ = "users"

    # ── Primary Key ────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )

    # ── Identity ───────────────────────────────────────────────────────────────
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # ── Authentication ─────────────────────────────────────────────────────────
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    # ── Soft Delete ────────────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    projects: Mapped[list["Project"]] = relationship(  # noqa: F821
        "Project", back_populates="owner", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id!r} email={self.email!r}>"
