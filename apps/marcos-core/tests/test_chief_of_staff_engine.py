"""Unit tests for ChiefOfStaffEngine, ChiefOfStaffResult, and DailyMission."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.chief_of_staff_config import (
    DEFAULT_CONFIG,
    VACATION_CONFIG,
    WEEKEND_CONFIG,
    WORKDAY_CONFIG,
    ChiefOfStaffConfig,
)
from core.chief_of_staff_engine import ChiefOfStaffEngine
from models.chief_of_staff_result import ChiefOfStaffResult
from models.daily_mission import DailyMission
from models.recommendation import Recommendation


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _rec(
    title: str = "Do Something",
    category: str = "Personal",
    priority: int = 5,
    confidence: float = 0.9,
    executive: str = "Test Executive",
) -> Recommendation:
    return Recommendation(
        title=title,
        description="Description.",
        category=category,
        priority=priority,
        reasoning="Reasoning.",
        executive=executive,
        confidence=confidence,
    )


def _engine(max_recs: int = 5) -> ChiefOfStaffEngine:
    return ChiefOfStaffEngine(ChiefOfStaffConfig(max_recommendations=max_recs, mode="test"))


# ------------------------------------------------------------------
# ChiefOfStaffConfig
# ------------------------------------------------------------------

def test_default_config_values() -> None:
    """DEFAULT_CONFIG has correct defaults."""
    assert DEFAULT_CONFIG.max_recommendations == 5
    assert DEFAULT_CONFIG.mode == "default"


def test_workday_config_values() -> None:
    """WORKDAY_CONFIG has correct values."""
    assert WORKDAY_CONFIG.max_recommendations == 5
    assert WORKDAY_CONFIG.mode == "workday"


def test_weekend_config_values() -> None:
    """WEEKEND_CONFIG caps at 3 recommendations."""
    assert WEEKEND_CONFIG.max_recommendations == 3
    assert WEEKEND_CONFIG.mode == "weekend"


def test_vacation_config_values() -> None:
    """VACATION_CONFIG caps at 2 recommendations."""
    assert VACATION_CONFIG.max_recommendations == 2
    assert VACATION_CONFIG.mode == "vacation"


def test_config_is_frozen() -> None:
    """ChiefOfStaffConfig instances are immutable."""
    try:
        DEFAULT_CONFIG.max_recommendations = 99  # type: ignore[misc]
        assert False, "Expected FrozenInstanceError"
    except Exception:
        pass


# ------------------------------------------------------------------
# ChiefOfStaffEngine — empty input
# ------------------------------------------------------------------

def test_empty_input_returns_empty_result() -> None:
    """Empty recommendation list produces a zeroed ChiefOfStaffResult."""
    result = ChiefOfStaffEngine().run([])
    assert result.selected == []
    assert result.deferred == []
    assert result.grouped == {}
    assert result.mission is None
    assert result.total_received == 0
    assert result.total_after_dedup == 0
    assert result.total_selected == 0
    assert result.duplicates_removed == 0
    assert result.confidence == 0.0


def test_empty_input_reasoning_mentions_zero() -> None:
    """Reasoning string for empty input references zero recommendations."""
    result = ChiefOfStaffEngine().run([])
    assert "0 recommendations" in result.reasoning or "0 recommendation" in result.reasoning


# ------------------------------------------------------------------
# ChiefOfStaffEngine — deduplication
# ------------------------------------------------------------------

def test_exact_duplicate_titles_removed() -> None:
    """Two recommendations with identical titles: only the first is kept."""
    recs = [_rec(title="Buy milk", priority=3), _rec(title="Buy milk", priority=5)]
    result = ChiefOfStaffEngine().run(recs)
    assert result.total_selected == 1
    assert result.duplicates_removed == 1
    assert result.selected[0].priority == 3


def test_case_insensitive_dedup() -> None:
    """Deduplication normalises titles to lowercase before comparing."""
    recs = [_rec(title="Call Sara"), _rec(title="call sara")]
    result = ChiefOfStaffEngine().run(recs)
    assert result.total_selected == 1
    assert result.duplicates_removed == 1


def test_whitespace_trimmed_in_dedup() -> None:
    """Leading and trailing whitespace is stripped before dedup comparison."""
    recs = [_rec(title="  Fix the leak  "), _rec(title="Fix the leak")]
    result = ChiefOfStaffEngine().run(recs)
    assert result.total_selected == 1
    assert result.duplicates_removed == 1


def test_distinct_titles_not_deduplicated() -> None:
    """Recommendations with distinct titles are all kept."""
    recs = [_rec(title="Task A"), _rec(title="Task B"), _rec(title="Task C")]
    result = ChiefOfStaffEngine().run(recs)
    assert result.total_selected == 3
    assert result.duplicates_removed == 0


def test_dedup_count_in_result() -> None:
    """total_after_dedup equals total_received minus duplicates_removed."""
    recs = [_rec(title="X"), _rec(title="X"), _rec(title="Y")]
    result = ChiefOfStaffEngine().run(recs)
    assert result.total_received == 3
    assert result.total_after_dedup == 2
    assert result.duplicates_removed == 1


# ------------------------------------------------------------------
# ChiefOfStaffEngine — scoring
# ------------------------------------------------------------------

def test_scoring_sorts_by_priority_ascending() -> None:
    """Lower priority number appears first in selected."""
    recs = [_rec(title="Low", priority=8), _rec(title="High", priority=2)]
    result = ChiefOfStaffEngine().run(recs)
    assert result.selected[0].title == "High"
    assert result.selected[1].title == "Low"


def test_scoring_breaks_ties_by_confidence_descending() -> None:
    """When priority is equal, higher confidence comes first."""
    recs = [
        _rec(title="Low Confidence", priority=3, confidence=0.6),
        _rec(title="High Confidence", priority=3, confidence=0.95),
    ]
    result = ChiefOfStaffEngine().run(recs)
    assert result.selected[0].title == "High Confidence"
    assert result.selected[1].title == "Low Confidence"


# ------------------------------------------------------------------
# ChiefOfStaffEngine — daily cap / deferral
# ------------------------------------------------------------------

def test_cap_limits_selected_count() -> None:
    """Selected count does not exceed max_recommendations."""
    recs = [_rec(title=f"Task {i}", priority=i) for i in range(1, 8)]
    result = _engine(max_recs=3).run(recs)
    assert result.total_selected == 3
    assert len(result.selected) == 3


def test_deferred_contains_overflow_recommendations() -> None:
    """Recommendations beyond the cap end up in deferred."""
    recs = [_rec(title=f"Task {i}", priority=i) for i in range(1, 8)]
    result = _engine(max_recs=3).run(recs)
    assert len(result.deferred) == 4


def test_deferred_is_empty_when_under_cap() -> None:
    """No deferral when recommendation count is within the cap."""
    recs = [_rec(title=f"Task {i}") for i in range(3)]
    result = _engine(max_recs=5).run(recs)
    assert result.deferred == []


def test_selected_plus_deferred_equals_total_after_dedup() -> None:
    """selected + deferred always accounts for all post-dedup recommendations."""
    recs = [_rec(title=f"T{i}", priority=i) for i in range(1, 10)]
    result = _engine(max_recs=4).run(recs)
    assert len(result.selected) + len(result.deferred) == result.total_after_dedup


# ------------------------------------------------------------------
# ChiefOfStaffEngine — grouping
# ------------------------------------------------------------------

def test_grouping_by_category() -> None:
    """Selected recommendations are partitioned correctly by category."""
    recs = [
        _rec(title="A", category="Marriage", priority=1),
        _rec(title="B", category="Finance", priority=2),
        _rec(title="C", category="Marriage", priority=3),
    ]
    result = ChiefOfStaffEngine().run(recs)
    assert set(result.grouped.keys()) == {"Marriage", "Finance"}
    assert len(result.grouped["Marriage"]) == 2
    assert len(result.grouped["Finance"]) == 1


def test_grouped_recommendations_match_selected() -> None:
    """Total items across all groups equals total_selected."""
    recs = [_rec(title=f"R{i}", category=f"Cat{i % 3}", priority=i) for i in range(6)]
    result = _engine(max_recs=4).run(recs)
    grouped_total = sum(len(v) for v in result.grouped.values())
    assert grouped_total == result.total_selected


# ------------------------------------------------------------------
# ChiefOfStaffEngine — daily mission
# ------------------------------------------------------------------

def test_mission_derived_from_top_recommendation() -> None:
    """Mission statement references the top-ranked recommendation's title."""
    recs = [
        _rec(title="Lead with Integrity", priority=2, category="Personal"),
        _rec(title="Lower Priority Task", priority=7),
    ]
    result = ChiefOfStaffEngine().run(recs)
    assert result.mission is not None
    assert "Lead with Integrity" in result.mission.statement
    assert result.mission.domain == "Personal"


def test_mission_is_none_when_no_recommendations() -> None:
    """Mission is None when the executive team produced nothing."""
    result = ChiefOfStaffEngine().run([])
    assert result.mission is None


def test_mission_confidence_matches_top_recommendation() -> None:
    """Mission confidence equals the confidence of the top recommendation."""
    recs = [_rec(title="Top Task", priority=1, confidence=0.87)]
    result = ChiefOfStaffEngine().run(recs)
    assert result.mission is not None
    assert result.mission.confidence == 0.87


def test_mission_source_executive_set() -> None:
    """Mission carries the source executive name from the top recommendation."""
    recs = [_rec(title="Task", executive="Marriage Executive")]
    result = ChiefOfStaffEngine().run(recs)
    assert result.mission is not None
    assert result.mission.source_executive == "Marriage Executive"


# ------------------------------------------------------------------
# ChiefOfStaffEngine — confidence aggregation
# ------------------------------------------------------------------

def test_aggregate_confidence_is_mean_of_selected() -> None:
    """Confidence is the mean confidence of selected recommendations."""
    recs = [
        _rec(title="A", confidence=0.8),
        _rec(title="B", confidence=0.6),
    ]
    result = ChiefOfStaffEngine().run(recs)
    assert result.confidence == 0.7


def test_aggregate_confidence_rounded_to_four_decimals() -> None:
    """Confidence is rounded to four decimal places."""
    recs = [
        _rec(title="A", confidence=1.0),
        _rec(title="B", confidence=0.0),
        _rec(title="C", confidence=0.5),
    ]
    result = ChiefOfStaffEngine().run(recs)
    assert result.confidence == round(1.5 / 3, 4)


# ------------------------------------------------------------------
# ChiefOfStaffEngine — reasoning
# ------------------------------------------------------------------

def test_reasoning_mentions_received_count() -> None:
    """Reasoning string includes the number of received recommendations."""
    recs = [_rec(title=f"T{i}") for i in range(4)]
    result = ChiefOfStaffEngine().run(recs)
    assert "4 recommendations" in result.reasoning


def test_reasoning_mentions_duplicates_when_present() -> None:
    """Reasoning mentions duplicate removal when it occurs."""
    recs = [_rec(title="Same"), _rec(title="Same"), _rec(title="Different")]
    result = ChiefOfStaffEngine().run(recs)
    assert "duplicate" in result.reasoning.lower()


def test_reasoning_mentions_deferral_when_cap_exceeded() -> None:
    """Reasoning mentions deferred recommendations when cap is exceeded."""
    recs = [_rec(title=f"T{i}", priority=i) for i in range(1, 8)]
    result = _engine(max_recs=3).run(recs)
    assert "deferred" in result.reasoning.lower()


def test_reasoning_omits_deferral_when_under_cap() -> None:
    """Reasoning does not mention deferral when all recommendations fit."""
    recs = [_rec(title=f"T{i}") for i in range(3)]
    result = _engine(max_recs=5).run(recs)
    assert "deferred" not in result.reasoning.lower()


def test_reasoning_includes_mode() -> None:
    """Reasoning string includes the active config mode."""
    engine = ChiefOfStaffEngine(ChiefOfStaffConfig(max_recommendations=5, mode="weekend"))
    result = engine.run([_rec()])
    assert "weekend" in result.reasoning


# ------------------------------------------------------------------
# ChiefOfStaffEngine — config injection
# ------------------------------------------------------------------

def test_default_config_used_when_none_passed() -> None:
    """Engine uses DEFAULT_CONFIG when no config is provided."""
    engine = ChiefOfStaffEngine()
    assert engine.config is DEFAULT_CONFIG


def test_custom_config_applied() -> None:
    """Custom config is applied correctly."""
    config = ChiefOfStaffConfig(max_recommendations=2, mode="test")
    engine = ChiefOfStaffEngine(config)
    recs = [_rec(title=f"T{i}", priority=i) for i in range(5)]
    result = engine.run(recs)
    assert result.total_selected == 2
    assert len(result.deferred) == 3


# ------------------------------------------------------------------
# DailyMission model
# ------------------------------------------------------------------

def test_daily_mission_defaults() -> None:
    """DailyMission initialises with correct empty defaults."""
    mission = DailyMission()
    assert mission.statement == ""
    assert mission.domain == ""
    assert mission.source_executive == ""
    assert mission.confidence == 0.0
    assert mission.reasoning == ""


def test_daily_mission_stores_values() -> None:
    """DailyMission stores provided field values correctly."""
    mission = DailyMission(
        statement="Today, focus on: Lead well.",
        domain="Business",
        source_executive="Business Executive",
        confidence=0.9,
        reasoning="Business is the top priority today.",
    )
    assert mission.statement == "Today, focus on: Lead well."
    assert mission.domain == "Business"
    assert mission.confidence == 0.9


# ------------------------------------------------------------------
# ChiefOfStaffResult model
# ------------------------------------------------------------------

def test_chief_of_staff_result_defaults() -> None:
    """ChiefOfStaffResult initialises with correct empty defaults."""
    result = ChiefOfStaffResult()
    assert result.selected == []
    assert result.grouped == {}
    assert result.deferred == []
    assert result.mission is None
    assert result.total_received == 0
    assert result.total_after_dedup == 0
    assert result.total_selected == 0
    assert result.duplicates_removed == 0
    assert result.reasoning == ""
    assert result.confidence == 0.0


# ------------------------------------------------------------------
# Runner
# ------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_default_config_values,
        test_workday_config_values,
        test_weekend_config_values,
        test_vacation_config_values,
        test_config_is_frozen,
        test_empty_input_returns_empty_result,
        test_empty_input_reasoning_mentions_zero,
        test_exact_duplicate_titles_removed,
        test_case_insensitive_dedup,
        test_whitespace_trimmed_in_dedup,
        test_distinct_titles_not_deduplicated,
        test_dedup_count_in_result,
        test_scoring_sorts_by_priority_ascending,
        test_scoring_breaks_ties_by_confidence_descending,
        test_cap_limits_selected_count,
        test_deferred_contains_overflow_recommendations,
        test_deferred_is_empty_when_under_cap,
        test_selected_plus_deferred_equals_total_after_dedup,
        test_grouping_by_category,
        test_grouped_recommendations_match_selected,
        test_mission_derived_from_top_recommendation,
        test_mission_is_none_when_no_recommendations,
        test_mission_confidence_matches_top_recommendation,
        test_mission_source_executive_set,
        test_aggregate_confidence_is_mean_of_selected,
        test_aggregate_confidence_rounded_to_four_decimals,
        test_reasoning_mentions_received_count,
        test_reasoning_mentions_duplicates_when_present,
        test_reasoning_mentions_deferral_when_cap_exceeded,
        test_reasoning_omits_deferral_when_under_cap,
        test_reasoning_includes_mode,
        test_default_config_used_when_none_passed,
        test_custom_config_applied,
        test_daily_mission_defaults,
        test_daily_mission_stores_values,
        test_chief_of_staff_result_defaults,
    ]
    for test in tests:
        test()
        print(f"  PASS  {test.__name__}")
    print(f"\nAll {len(tests)} tests passed.")
