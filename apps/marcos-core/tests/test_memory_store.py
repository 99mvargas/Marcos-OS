"""Unit tests for memory object creation and MemoryStore CRUD operations."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from memory.memory_store import MemoryStore
from models.commitment import Commitment
from models.habit import Habit
from models.observation import Observation
from models.project import Project
from models.recurring_responsibility import RecurringResponsibility
from models.task import Task


# ------------------------------------------------------------------
# Object creation
# ------------------------------------------------------------------

def test_commitment_creation() -> None:
    """Commitment is created with correct defaults."""
    c = Commitment(id="c1", title="Call contractor", domain="Business")
    assert c.status == "active"
    assert c.source == "marcos"
    assert c.is_overdue() is False


def test_commitment_overdue() -> None:
    """Commitment with past due_at and active status is overdue."""
    c = Commitment(
        id="c2",
        title="Overdue task",
        description="",
        due_at=datetime.utcnow() - timedelta(hours=1),
    )
    assert c.is_overdue() is True


def test_commitment_not_overdue_when_completed() -> None:
    """Completed commitment is never overdue regardless of due_at."""
    c = Commitment(
        id="c3",
        title="Done task",
        description="",
        status="completed",
        due_at=datetime.utcnow() - timedelta(hours=1),
    )
    assert c.is_overdue() is False


def test_task_creation() -> None:
    """Task is created with correct defaults."""
    t = Task(id="t1", title="Buy flowers for Sara")
    assert t.status == "pending"
    assert t.domain == ""


def test_project_creation() -> None:
    """Project is created with correct defaults."""
    p = Project(id="p1", title="Bathroom Renovation")
    assert p.status == "active"
    assert p.tags == []


def test_habit_creation() -> None:
    """Habit is created with correct defaults."""
    h = Habit(id="h1", title="Morning prayer", frequency="daily")
    assert h.current_streak == 0
    assert h.status == "active"


def test_recurring_responsibility_creation() -> None:
    """RecurringResponsibility is created with correct defaults."""
    r = RecurringResponsibility(id="r1", title="Chai vet visit", interval_days=180)
    assert r.owner == "marcos"
    assert r.is_overdue() is False


def test_observation_creation() -> None:
    """Observation is created with correct defaults."""
    o = Observation(id="o1", content="Marcos tends to postpone household tasks until guests arrive.")
    assert o.source == "marcos"
    assert o.tags == []


# ------------------------------------------------------------------
# MemoryStore CRUD
# ------------------------------------------------------------------

def test_store_create_and_get() -> None:
    """Create then retrieve an object by id."""
    store = MemoryStore()
    c = Commitment(id="c10", title="Test commitment", description="")
    store.create(c)
    result = store.get(Commitment, "c10")
    assert result is not None
    assert result.title == "Test commitment"


def test_store_create_duplicate_raises() -> None:
    """Creating an object with a duplicate id raises ValueError."""
    store = MemoryStore()
    c = Commitment(id="dup", title="Original", description="")
    store.create(c)
    try:
        store.create(Commitment(id="dup", title="Duplicate", description=""))
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_store_update() -> None:
    """Update replaces an existing object."""
    store = MemoryStore()
    c = Commitment(id="c20", title="Original", description="")
    store.create(c)
    c.title = "Updated"
    store.update(c)
    assert store.get(Commitment, "c20").title == "Updated"


def test_store_update_missing_raises() -> None:
    """Updating a non-existent object raises KeyError."""
    store = MemoryStore()
    c = Commitment(id="missing", title="Ghost", description="")
    try:
        store.update(c)
        assert False, "Expected KeyError"
    except KeyError:
        pass


def test_store_delete() -> None:
    """Delete removes an object and returns True."""
    store = MemoryStore()
    c = Commitment(id="c30", title="To delete", description="")
    store.create(c)
    assert store.delete(Commitment, "c30") is True
    assert store.get(Commitment, "c30") is None


def test_store_delete_missing_returns_false() -> None:
    """Deleting a non-existent id returns False."""
    store = MemoryStore()
    assert store.delete(Commitment, "nonexistent") is False


def test_store_list() -> None:
    """List returns all objects of a given type."""
    store = MemoryStore()
    store.create(Commitment(id="l1", title="A", description=""))
    store.create(Commitment(id="l2", title="B", description=""))
    store.create(Task(id="t1", title="Unrelated task"))
    assert store.count(Commitment) == 2
    assert store.count(Task) == 1


def test_store_list_by() -> None:
    """list_by filters objects by field value."""
    store = MemoryStore()
    store.create(Commitment(id="f1", title="Marriage task", description="", domain="Marriage"))
    store.create(Commitment(id="f2", title="Business task", description="", domain="Business"))
    results = store.list_by(Commitment, domain="Marriage")
    assert len(results) == 1
    assert results[0].id == "f1"


def test_store_namespaces_are_isolated() -> None:
    """Different model types do not share storage buckets."""
    store = MemoryStore()
    store.create(Commitment(id="shared_id", title="Commitment", description=""))
    store.create(Task(id="shared_id", title="Task"))
    assert store.get(Commitment, "shared_id").title == "Commitment"
    assert store.get(Task, "shared_id").title == "Task"


# ------------------------------------------------------------------
# Runner
# ------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_commitment_creation,
        test_commitment_overdue,
        test_commitment_not_overdue_when_completed,
        test_task_creation,
        test_project_creation,
        test_habit_creation,
        test_recurring_responsibility_creation,
        test_observation_creation,
        test_store_create_and_get,
        test_store_create_duplicate_raises,
        test_store_update,
        test_store_update_missing_raises,
        test_store_delete,
        test_store_delete_missing_returns_false,
        test_store_list,
        test_store_list_by,
        test_store_namespaces_are_isolated,
    ]
    for test in tests:
        test()
        print(f"  PASS  {test.__name__}")
    print(f"\nAll {len(tests)} tests passed.")
