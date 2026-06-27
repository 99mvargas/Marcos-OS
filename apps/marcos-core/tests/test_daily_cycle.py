"""Tests for DailyExecutiveCycle and DailyCycleResult."""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from memory.memory_store import MemoryStore
from models.daily_cycle_result import DailyCycleResult
from models.draft_memory import OBJECT_TYPE_COMMITMENT, STATE_DRAFT, DraftMemory
from models.morning_brief import MorningBrief
from models.recommendation import Recommendation
from services.daily_executive_cycle import DailyExecutiveCycle

# Path to the real Obsidian vault — two levels above tests/ -> marco-core/ -> repo root
_REPO_ROOT = Path(__file__).resolve().parents[3]
_VAULT_PATH = _REPO_ROOT / "obsidian"
_EMPTY_VAULT = Path(__file__).parent  # A directory with no .md files at vault root level


# ------------------------------------------------------------------
# DailyCycleResult model
# ------------------------------------------------------------------

def test_daily_cycle_result_defaults() -> None:
    """DailyCycleResult initialises with sensible defaults."""
    r = DailyCycleResult()
    assert isinstance(r.started_at, datetime)
    assert r.completed_at is None
    assert r.knowledge_documents == 0
    assert r.draft_memory_count == 0
    assert r.executives_run == 0
    assert r.recommendations == []
    assert r.morning_brief is None
    assert r.execution_time_ms == 0.0


def test_daily_cycle_result_total_recommendations() -> None:
    """total_recommendations counts the recommendations list."""
    r = DailyCycleResult(
        recommendations=[
            Recommendation("A", "D", "C", 1, "R", "E", 0.9),
            Recommendation("B", "D", "C", 2, "R", "E", 0.9),
        ]
    )
    assert r.total_recommendations == 2


def test_daily_cycle_result_success_false_when_no_brief() -> None:
    """success is False when morning_brief is None."""
    r = DailyCycleResult(completed_at=datetime.utcnow())
    assert r.success is False


def test_daily_cycle_result_success_false_when_not_completed() -> None:
    """success is False when completed_at is None."""
    r = DailyCycleResult(morning_brief=MorningBrief())
    assert r.success is False


def test_daily_cycle_result_success_true_when_both_set() -> None:
    """success is True when both completed_at and morning_brief are set."""
    r = DailyCycleResult(
        completed_at=datetime.utcnow(),
        morning_brief=MorningBrief(),
    )
    assert r.success is True


# ------------------------------------------------------------------
# DailyExecutiveCycle — with real vault
# ------------------------------------------------------------------

def _make_cycle(store: MemoryStore | None = None) -> DailyExecutiveCycle:
    return DailyExecutiveCycle(vault_path=_VAULT_PATH, store=store)


def test_daily_cycle_completes_successfully() -> None:
    """Daily cycle runs end-to-end without raising."""
    cycle = _make_cycle()
    result = cycle.run()
    assert result.success is True


def test_daily_cycle_loads_knowledge_documents() -> None:
    """Daily cycle reports knowledge documents loaded from real vault."""
    result = _make_cycle().run()
    assert result.knowledge_documents > 0


def test_daily_cycle_runs_all_executives() -> None:
    """Daily cycle executes all 8 registered executives."""
    result = _make_cycle().run()
    assert result.executives_run == 8


def test_daily_cycle_generates_morning_brief() -> None:
    """Daily cycle produces a MorningBrief object."""
    result = _make_cycle().run()
    assert isinstance(result.morning_brief, MorningBrief)


def test_daily_cycle_recommendations_propagated() -> None:
    """Recommendation count in DailyCycleResult matches morning brief."""
    result = _make_cycle().run()
    assert result.total_recommendations == result.morning_brief.total_recommendations


def test_daily_cycle_timestamps_populated() -> None:
    """started_at and completed_at are both datetime instances."""
    result = _make_cycle().run()
    assert isinstance(result.started_at, datetime)
    assert isinstance(result.completed_at, datetime)
    assert result.completed_at >= result.started_at


def test_daily_cycle_execution_time_positive() -> None:
    """Execution time is a positive float in milliseconds."""
    result = _make_cycle().run()
    assert result.execution_time_ms > 0.0


def test_daily_cycle_recommendations_sorted_by_priority() -> None:
    """Recommendations are sorted ascending by priority."""
    result = _make_cycle().run()
    priorities = [r.priority for r in result.recommendations]
    assert priorities == sorted(priorities)


# ------------------------------------------------------------------
# DailyExecutiveCycle — memory store integration
# ------------------------------------------------------------------

def test_daily_cycle_reflects_existing_draft_count() -> None:
    """draft_memory_count reflects DraftMemory objects already in the store."""
    store = MemoryStore()
    store.create(DraftMemory(
        id="d1",
        object_type=OBJECT_TYPE_COMMITMENT,
        title="Test draft",
        content="I need to call someone.",
        state=STATE_DRAFT,
    ))
    result = DailyExecutiveCycle(vault_path=_VAULT_PATH, store=store).run()
    assert result.draft_memory_count == 1


def test_daily_cycle_store_property() -> None:
    """DailyExecutiveCycle.store returns the MemoryStore instance."""
    store = MemoryStore()
    cycle = DailyExecutiveCycle(vault_path=_VAULT_PATH, store=store)
    assert cycle.store is store


def test_daily_cycle_new_store_created_when_none_passed() -> None:
    """A fresh MemoryStore is created when none is provided."""
    cycle = DailyExecutiveCycle(vault_path=_VAULT_PATH)
    assert isinstance(cycle.store, MemoryStore)


# ------------------------------------------------------------------
# DailyExecutiveCycle — empty vault
# ------------------------------------------------------------------

def test_daily_cycle_handles_empty_vault_gracefully() -> None:
    """Daily cycle completes without error when the vault contains no .md files."""
    # Use a path that exists but has no Markdown files matching the vault pattern.
    # The tests/ directory itself works — it has .py files, no .md files.
    cycle = DailyExecutiveCycle(vault_path=_EMPTY_VAULT)
    result = cycle.run()
    assert result.success is True
    assert result.knowledge_documents == 0
    assert result.executives_run == 8
    assert result.total_recommendations == 0


def test_daily_cycle_repeated_runs_are_independent() -> None:
    """Running the cycle twice produces two independent DailyCycleResult objects."""
    cycle = _make_cycle()
    r1 = cycle.run()
    r2 = cycle.run()
    assert r1 is not r2
    assert r1.morning_brief is not r2.morning_brief


# ------------------------------------------------------------------
# Runner
# ------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_daily_cycle_result_defaults,
        test_daily_cycle_result_total_recommendations,
        test_daily_cycle_result_success_false_when_no_brief,
        test_daily_cycle_result_success_false_when_not_completed,
        test_daily_cycle_result_success_true_when_both_set,
        test_daily_cycle_completes_successfully,
        test_daily_cycle_loads_knowledge_documents,
        test_daily_cycle_runs_all_executives,
        test_daily_cycle_generates_morning_brief,
        test_daily_cycle_recommendations_propagated,
        test_daily_cycle_timestamps_populated,
        test_daily_cycle_execution_time_positive,
        test_daily_cycle_recommendations_sorted_by_priority,
        test_daily_cycle_reflects_existing_draft_count,
        test_daily_cycle_store_property,
        test_daily_cycle_new_store_created_when_none_passed,
        test_daily_cycle_handles_empty_vault_gracefully,
        test_daily_cycle_repeated_runs_are_independent,
    ]
    for test in tests:
        test()
        print(f"  PASS  {test.__name__}")
    print(f"\nAll {len(tests)} tests passed.")
