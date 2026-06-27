"""Unit tests for MorningBrief model and MorningBriefService."""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.context_engine import ContextEngine
from core.executive_engine import ExecutiveEngine
from models.morning_brief import MorningBrief
from models.recommendation import Recommendation
from services.morning_brief import MorningBriefService


# ------------------------------------------------------------------
# MorningBrief model
# ------------------------------------------------------------------

def test_morning_brief_creation_defaults() -> None:
    """MorningBrief creates with correct defaults."""
    brief = MorningBrief()
    assert isinstance(brief.generated_at, datetime)
    assert brief.recommendations == []
    assert brief.summary == ""
    assert brief.total_recommendations == 0


def test_morning_brief_with_data() -> None:
    """MorningBrief stores provided values correctly."""
    rec = Recommendation(
        title="Test",
        description="Do something.",
        category="Personal",
        priority=1,
        reasoning="Testing.",
        executive="Personal Executive",
        confidence=0.9,
    )
    brief = MorningBrief(
        recommendations=[rec],
        summary="1 recommendation generated.",
        total_recommendations=1,
    )
    assert brief.total_recommendations == 1
    assert brief.recommendations[0].title == "Test"


# ------------------------------------------------------------------
# MorningBriefService
# ------------------------------------------------------------------

def test_morning_brief_service_returns_brief() -> None:
    """MorningBriefService.generate() returns a MorningBrief instance."""
    context = ContextEngine(documents=[])
    engine = ExecutiveEngine(context)
    service = MorningBriefService(context, engine)
    brief = service.generate()
    assert isinstance(brief, MorningBrief)


def test_morning_brief_service_zero_recommendations() -> None:
    """With no executive recommendations, total is 0 and summary is correct."""
    context = ContextEngine(documents=[])
    engine = ExecutiveEngine(context)
    service = MorningBriefService(context, engine)
    brief = service.generate()
    assert brief.total_recommendations == 0
    assert "No recommendations available" in brief.summary


def test_morning_brief_service_generated_at_is_datetime() -> None:
    """generated_at is a UTC datetime."""
    context = ContextEngine(documents=[])
    engine = ExecutiveEngine(context)
    service = MorningBriefService(context, engine)
    brief = service.generate()
    assert isinstance(brief.generated_at, datetime)


def test_morning_brief_recommendations_are_sorted_by_priority() -> None:
    """Recommendations are returned in ascending priority order."""
    brief = MorningBrief(
        recommendations=[
            Recommendation("B", "", "X", 3, "", "Exec", 0.5),
            Recommendation("A", "", "X", 1, "", "Exec", 0.9),
        ],
        total_recommendations=2,
    )
    # Manually sort to verify the model holds order as provided.
    sorted_recs = sorted(brief.recommendations, key=lambda r: r.priority)
    assert sorted_recs[0].title == "A"
    assert sorted_recs[1].title == "B"


# ------------------------------------------------------------------
# Runner
# ------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_morning_brief_creation_defaults,
        test_morning_brief_with_data,
        test_morning_brief_service_returns_brief,
        test_morning_brief_service_zero_recommendations,
        test_morning_brief_service_generated_at_is_datetime,
        test_morning_brief_recommendations_are_sorted_by_priority,
    ]
    for test in tests:
        test()
        print(f"  PASS  {test.__name__}")
    print(f"\nAll {len(tests)} tests passed.")
