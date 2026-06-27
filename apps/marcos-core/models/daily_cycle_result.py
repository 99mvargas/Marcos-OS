"""Data model for the result of a complete Marcos OS Daily Executive Cycle."""

from dataclasses import dataclass, field
from datetime import datetime

from models.morning_brief import MorningBrief
from models.recommendation import Recommendation


@dataclass
class DailyCycleResult:
    """The complete output of one Daily Executive Cycle run.

    Captures every measurable outcome of a full Marcos OS pipeline
    execution: knowledge load, memory state, executive output, the
    generated brief, and timing.

    Future evolution:
        - Persisted to PostgreSQL for historical cycle comparison.
        - Surfaced on a Dashboard with execution trend graphs.
        - Used by the adaptive scheduling layer to detect consistent failures.

    Attributes:
        started_at: UTC timestamp when the cycle began.
        completed_at: UTC timestamp when the cycle finished. None if
            the cycle has not yet completed or failed before completion.
        knowledge_documents: Number of Markdown files loaded from the vault.
        draft_memory_count: Number of DraftMemory objects in the MemoryStore
            at the end of the cycle.
        executives_run: Number of domain executives that were executed.
        recommendations: Priority-sorted list of Recommendation objects
            produced by the executive team.
        morning_brief: The MorningBrief generated at the end of the cycle.
            None if the cycle failed before the brief was produced.
        execution_time_ms: Total wall-clock execution time in milliseconds.
            Computed from started_at and completed_at when both are set.
    """

    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    knowledge_documents: int = 0
    draft_memory_count: int = 0
    executives_run: int = 0
    recommendations: list[Recommendation] = field(default_factory=list)
    morning_brief: MorningBrief | None = None
    execution_time_ms: float = 0.0

    @property
    def total_recommendations(self) -> int:
        """Total number of recommendations produced this cycle."""
        return len(self.recommendations)

    @property
    def success(self) -> bool:
        """True when the cycle completed and produced a Morning Brief."""
        return self.completed_at is not None and self.morning_brief is not None
