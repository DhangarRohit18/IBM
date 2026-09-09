"""
LEGACYX — Analysis Run State Machine (Phase 3).

Manages valid transitions for AnalysisRunStatus:
PENDING -> RUNNING -> COMPLETED (or FAILED).
"""

from app.models.analysis_run import AnalysisRunStatus


class AnalysisStateException(Exception):
    """Raised when an invalid analysis state transition is attempted."""

    def __init__(self, current_status: AnalysisRunStatus, target_status: AnalysisRunStatus) -> None:
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(
            f"Invalid analysis state transition from {current_status.value} to {target_status.value}"
        )


ALLOWED_TRANSITIONS: dict[AnalysisRunStatus, set[AnalysisRunStatus]] = {
    AnalysisRunStatus.PENDING: {AnalysisRunStatus.RUNNING, AnalysisRunStatus.FAILED},
    AnalysisRunStatus.RUNNING: {AnalysisRunStatus.COMPLETED, AnalysisRunStatus.FAILED},
    AnalysisRunStatus.COMPLETED: set(),  # Terminal state
    AnalysisRunStatus.FAILED: {AnalysisRunStatus.PENDING},  # Retry allowed
}


def validate_analysis_transition(
    current_status: AnalysisRunStatus, target_status: AnalysisRunStatus
) -> None:
    """Validate that moving from current_status to target_status is permitted."""
    allowed = ALLOWED_TRANSITIONS.get(current_status, set())
    if target_status not in allowed:
        raise AnalysisStateException(current_status, target_status)
