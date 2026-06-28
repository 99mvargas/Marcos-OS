"""Data model for the result of a Chief of Staff Engine run."""

from dataclasses import dataclass, field

from models.daily_mission import DailyMission
from models.recommendation import Recommendation


@dataclass
class ChiefOfStaffResult:
    """The curated output of one Chief of Staff Engine run.

    Records every decision made during the selection pipeline: what was
    chosen, what was deferred, what was eliminated as a duplicate, the
    derived daily mission, and the reasoning behind the selection.

    In v1, mission, deferred, reasoning, and confidence are populated by
    deterministic rules. The interface is designed so future AI reasoning
    can populate any of these fields without changing downstream consumers.

    Attributes:
        selected: Final curated list of recommendations for the day,
            sorted by priority ascending then confidence descending.
        grouped: The selected recommendations partitioned by category.
            Insertion order reflects the priority of the first occurrence
            within each category.
        deferred: Recommendations that were valid but excluded because
            the daily cap was reached. Sorted by score (best first).
            Preserved for future review workflows and PostgreSQL persistence.
        mission: The day's primary mission, derived from the top-ranked
            recommendation. None when no recommendations are available.
        total_received: Count of recommendations received from the
            executive team before any processing.
        total_after_dedup: Count after duplicate removal.
        total_selected: Count of recommendations in the curated output.
            Always <= config.max_recommendations.
        duplicates_removed: Count of recommendations dropped as duplicates.
        reasoning: Human-readable explanation of the selection decisions.
            Rule-derived in v1. AI-generated in a future sprint.
        confidence: Aggregate confidence for this run's output, derived
            from the mean confidence of selected recommendations.
            0.0 when no recommendations are selected.
    """

    selected: list[Recommendation] = field(default_factory=list)
    grouped: dict[str, list[Recommendation]] = field(default_factory=dict)
    deferred: list[Recommendation] = field(default_factory=list)
    mission: DailyMission | None = None
    total_received: int = 0
    total_after_dedup: int = 0
    total_selected: int = 0
    duplicates_removed: int = 0
    reasoning: str = ""
    confidence: float = 0.0
