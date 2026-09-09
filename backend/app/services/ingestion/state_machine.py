"""
LEGACYX — Ingestion State Machine (Phase 2).

Manages valid transitions for RepositoryStatus:
UPLOADED -> VALIDATING -> EXTRACTING -> INDEXING -> COMPLETED (or FAILED).
"""

from app.models.repository import RepositoryStatus


class IngestionStateException(Exception):
    """Raised when an invalid ingestion state transition is attempted."""

    def __init__(self, current_status: RepositoryStatus, target_status: RepositoryStatus) -> None:
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(
            f"Invalid ingestion state transition from {current_status.value} to {target_status.value}"
        )


ALLOWED_TRANSITIONS: dict[RepositoryStatus, set[RepositoryStatus]] = {
    RepositoryStatus.UPLOADED: {RepositoryStatus.VALIDATING, RepositoryStatus.FAILED},
    RepositoryStatus.VALIDATING: {RepositoryStatus.EXTRACTING, RepositoryStatus.FAILED},
    RepositoryStatus.EXTRACTING: {RepositoryStatus.INDEXING, RepositoryStatus.FAILED},
    RepositoryStatus.INDEXING: {RepositoryStatus.COMPLETED, RepositoryStatus.FAILED},
    RepositoryStatus.COMPLETED: set(),  # Terminal state
    RepositoryStatus.FAILED: {RepositoryStatus.VALIDATING},  # Retry allowed
}


def validate_transition(current_status: RepositoryStatus, target_status: RepositoryStatus) -> None:
    """Validate that moving from current_status to target_status is permitted."""
    allowed = ALLOWED_TRANSITIONS.get(current_status, set())
    if target_status not in allowed:
        raise IngestionStateException(current_status, target_status)
