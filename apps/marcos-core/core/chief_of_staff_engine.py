"""Decision layer that curates executive output into a daily action set."""

from datetime import datetime

from config.chief_of_staff_config import DEFAULT_CONFIG, ChiefOfStaffConfig
from models.chief_of_staff_result import ChiefOfStaffResult
from models.daily_mission import DailyMission
from models.recommendation import Recommendation


class ChiefOfStaffEngine:
    """Curates raw executive output into a daily action set.

    Receives all Recommendation objects from the ExecutiveEngine, applies
    a deterministic five-stage decision pipeline, and returns a
    ChiefOfStaffResult containing a curated selection, groupings, deferred
    items, a daily mission, and a reasoning trace.

    Decision pipeline (always runs in this order):
        1. Deduplicate — drop recommendations with identical normalized titles.
        2. Score       — sort by priority ASC, then confidence DESC.
        3. Select      — take the top N per config.max_recommendations.
        4. Group       — partition selected recommendations by category.
        5. Derive      — produce a DailyMission from the top recommendation.

    No external dependencies. No AI. Fully deterministic.

    Future evolution:
        - Stage 5 will call an LLM to synthesise the mission across domains.
        - Stage 1 will use semantic similarity for deduplication instead of
          exact title matching.
        - A scheduling stage will resurface high-value deferred recommendations
          on later days.

    Attributes:
        _config: The ChiefOfStaffConfig profile controlling this run.
    """

    def __init__(self, config: ChiefOfStaffConfig | None = None) -> None:
        """Initialise the ChiefOfStaffEngine.

        Args:
            config: Configuration profile. DEFAULT_CONFIG is used when None.
        """
        self._config = config or DEFAULT_CONFIG

    @property
    def config(self) -> ChiefOfStaffConfig:
        """The configuration profile active for this engine instance."""
        return self._config

    def run(self, recommendations: list[Recommendation]) -> ChiefOfStaffResult:
        """Apply the decision pipeline to raw executive output.

        Args:
            recommendations: All Recommendation objects produced by the
                executive team this cycle. May be empty.

        Returns:
            A fully populated ChiefOfStaffResult.
        """
        total_received = len(recommendations)

        deduped = self._deduplicate(recommendations)
        total_after_dedup = len(deduped)
        duplicates_removed = total_received - total_after_dedup

        scored = self._score(deduped)

        cap = self._config.max_recommendations
        selected = scored[:cap]
        deferred = scored[cap:]

        grouped = self._group(selected)
        mission = self._derive_mission(selected)
        confidence = self._aggregate_confidence(selected)
        reasoning = self._build_reasoning(
            total_received=total_received,
            duplicates_removed=duplicates_removed,
            total_selected=len(selected),
            total_deferred=len(deferred),
        )

        return ChiefOfStaffResult(
            selected=selected,
            grouped=grouped,
            deferred=deferred,
            mission=mission,
            total_received=total_received,
            total_after_dedup=total_after_dedup,
            total_selected=len(selected),
            duplicates_removed=duplicates_removed,
            reasoning=reasoning,
            confidence=confidence,
        )

    # ------------------------------------------------------------------
    # Private pipeline stages
    # ------------------------------------------------------------------

    def _deduplicate(self, recommendations: list[Recommendation]) -> list[Recommendation]:
        """Remove recommendations with identical normalized titles.

        When duplicates are present the first occurrence (earlier in the
        input list) is kept. Because the ExecutiveEngine delivers input
        already sorted by priority, the kept item is always the
        higher-priority one.

        Args:
            recommendations: Raw recommendation list in any order.

        Returns:
            Deduplicated list preserving relative input ordering.
        """
        seen: set[str] = set()
        result: list[Recommendation] = []
        for rec in recommendations:
            key = rec.title.lower().strip()
            if key not in seen:
                seen.add(key)
                result.append(rec)
        return result

    def _score(self, recommendations: list[Recommendation]) -> list[Recommendation]:
        """Sort recommendations by composite score.

        Sorting criteria (applied in order):
            1. Priority ascending — lower numbers are more important.
            2. Confidence descending — higher confidence wins ties.

        Args:
            recommendations: Deduplicated recommendation list.

        Returns:
            New sorted list. Input is not mutated.
        """
        return sorted(recommendations, key=lambda r: (r.priority, -r.confidence))

    def _group(
        self, recommendations: list[Recommendation]
    ) -> dict[str, list[Recommendation]]:
        """Partition recommendations by category.

        Category insertion order reflects the priority of the first
        occurrence within each category.

        Args:
            recommendations: Score-ordered selected recommendations.

        Returns:
            Dict mapping category name to its recommendations.
        """
        groups: dict[str, list[Recommendation]] = {}
        for rec in recommendations:
            groups.setdefault(rec.category, []).append(rec)
        return groups

    def _derive_mission(
        self, selected: list[Recommendation]
    ) -> DailyMission | None:
        """Derive a daily mission from the top-ranked recommendation.

        In v1 the mission is a deterministic restatement of the
        highest-priority selected recommendation. Future AI integration
        will synthesise a mission from across all selected domains without
        changing this method's signature or return type.

        Args:
            selected: Score-ordered selected recommendations.

        Returns:
            A DailyMission instance, or None when selected is empty.
        """
        if not selected:
            return None

        top = selected[0]
        return DailyMission(
            statement=f"Today, focus on: {top.title}.",
            domain=top.category,
            source_executive=top.executive,
            generated_at=datetime.utcnow(),
            confidence=top.confidence,
            reasoning=top.reasoning,
        )

    def _aggregate_confidence(self, selected: list[Recommendation]) -> float:
        """Compute mean confidence across selected recommendations.

        Args:
            selected: The final curated recommendation list.

        Returns:
            Mean confidence as a float rounded to four decimal places,
            or 0.0 when selected is empty.
        """
        if not selected:
            return 0.0
        return round(sum(r.confidence for r in selected) / len(selected), 4)

    def _build_reasoning(
        self,
        total_received: int,
        duplicates_removed: int,
        total_selected: int,
        total_deferred: int,
    ) -> str:
        """Build a human-readable explanation of the selection decisions.

        Args:
            total_received: Recommendations received from the executive team.
            duplicates_removed: Recommendations removed as duplicates.
            total_selected: Recommendations in the curated output.
            total_deferred: Recommendations that exceeded the daily cap.

        Returns:
            A plain-English reasoning string.
        """
        parts: list[str] = [
            f"Received {total_received} "
            f"recommendation{'s' if total_received != 1 else ''} "
            f"from the executive team."
        ]
        if duplicates_removed:
            parts.append(
                f"Removed {duplicates_removed} "
                f"duplicate{'s' if duplicates_removed != 1 else ''}."
            )
        parts.append(
            f"Selected {total_selected} for today "
            f"(cap: {self._config.max_recommendations}, "
            f"mode: {self._config.mode})."
        )
        if total_deferred:
            parts.append(
                f"Deferred {total_deferred} "
                f"recommendation{'s' if total_deferred != 1 else ''} "
                f"to a future cycle."
            )
        return " ".join(parts)
