"""Tests for MemoryCommitService and DraftMemory model."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from memory.memory_store import MemoryStore
from models.capture_result import CaptureResult
from models.draft_memory import (
    OBJECT_TYPE_COMMITMENT,
    OBJECT_TYPE_OBSERVATION,
    OBJECT_TYPE_RELATIONSHIP,
    OBJECT_TYPE_UNKNOWN,
    STATE_DRAFT,
    DraftMemory,
)
from services.memory_commit_service import MemoryCommitService


# ------------------------------------------------------------------
# DraftMemory model
# ------------------------------------------------------------------

def test_draft_memory_default_state() -> None:
    """DraftMemory state defaults to Draft."""
    d = DraftMemory(id="x", object_type=OBJECT_TYPE_COMMITMENT, title="Test", content="Test")
    assert d.state == STATE_DRAFT


def test_draft_memory_default_confidence() -> None:
    """DraftMemory confidence defaults to 1.0."""
    d = DraftMemory(id="x", object_type=OBJECT_TYPE_COMMITMENT, title="T", content="T")
    assert d.confidence == 1.0


def test_draft_memory_invalid_object_type_raises() -> None:
    """Invalid object_type raises ValueError."""
    try:
        DraftMemory(id="x", object_type="Invalid", title="T", content="T")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_draft_memory_invalid_confidence_raises() -> None:
    """Confidence outside 0.0–1.0 raises ValueError."""
    try:
        DraftMemory(id="x", object_type=OBJECT_TYPE_COMMITMENT, title="T", content="T", confidence=1.5)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_draft_memory_confidence_zero_is_valid() -> None:
    """Confidence of 0.0 is valid (used for Unknown drafts)."""
    d = DraftMemory(id="x", object_type=OBJECT_TYPE_UNKNOWN, title="T", content="T", confidence=0.0)
    assert d.confidence == 0.0


def test_draft_memory_all_valid_types() -> None:
    """All four object types can be instantiated without error."""
    for obj_type in [OBJECT_TYPE_COMMITMENT, OBJECT_TYPE_OBSERVATION,
                     OBJECT_TYPE_RELATIONSHIP, OBJECT_TYPE_UNKNOWN]:
        d = DraftMemory(id=obj_type, object_type=obj_type, title="T", content="T")
        assert d.object_type == obj_type


# ------------------------------------------------------------------
# MemoryCommitService — single bucket
# ------------------------------------------------------------------

def test_commit_single_commitment() -> None:
    """One commitment produces one Draft Commitment object."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(commitments=["I need to call the contractor."])
    drafts = service.commit(result)
    assert len(drafts) == 1
    assert drafts[0].object_type == OBJECT_TYPE_COMMITMENT
    assert drafts[0].state == STATE_DRAFT


def test_commit_single_observation() -> None:
    """One observation produces one Draft Observation object."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(observations=["I noticed the living room light is dim."])
    drafts = service.commit(result)
    assert len(drafts) == 1
    assert drafts[0].object_type == OBJECT_TYPE_OBSERVATION


def test_commit_single_relationship() -> None:
    """One relationship item produces one Draft Relationship object."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(relationship_items=["Sara said she wants flowers."])
    drafts = service.commit(result)
    assert len(drafts) == 1
    assert drafts[0].object_type == OBJECT_TYPE_RELATIONSHIP


def test_commit_unknown_item() -> None:
    """Unknown items produce Draft Unknown objects."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(unknown_items=["Random unclassifiable input."])
    drafts = service.commit(result)
    assert len(drafts) == 1
    assert drafts[0].object_type == OBJECT_TYPE_UNKNOWN


def test_commit_question_becomes_unknown() -> None:
    """Questions are stored as Draft Unknown objects."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(questions=["Should I hire a cleaner?"])
    drafts = service.commit(result)
    assert len(drafts) == 1
    assert drafts[0].object_type == OBJECT_TYPE_UNKNOWN
    assert "Should I hire a cleaner" in drafts[0].content


# ------------------------------------------------------------------
# Correct object type assignment
# ------------------------------------------------------------------

def test_commit_object_types_assigned_correctly() -> None:
    """Each bucket maps to the correct object_type."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(
        commitments=["I will fix the light."],
        observations=["I noticed the switch is loose."],
        relationship_items=["Sara needs more help around the house."],
        unknown_items=["Something completely unclassifiable."],
    )
    drafts = service.commit(result)
    type_map = {d.content: d.object_type for d in drafts}
    assert type_map["I will fix the light."] == OBJECT_TYPE_COMMITMENT
    assert type_map["I noticed the switch is loose."] == OBJECT_TYPE_OBSERVATION
    assert type_map["Sara needs more help around the house."] == OBJECT_TYPE_RELATIONSHIP
    assert type_map["Something completely unclassifiable."] == OBJECT_TYPE_UNKNOWN


# ------------------------------------------------------------------
# State
# ------------------------------------------------------------------

def test_all_drafts_have_draft_state() -> None:
    """Every object produced by commit() has state='Draft'."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(
        commitments=["I need to call."],
        observations=["I noticed something."],
        relationship_items=["Sara said hello."],
        questions=["What should I do?"],
        unknown_items=["Unclassifiable."],
    )
    drafts = service.commit(result)
    assert all(d.state == STATE_DRAFT for d in drafts)


# ------------------------------------------------------------------
# Confidence values
# ------------------------------------------------------------------

def test_confidence_values_are_valid_floats() -> None:
    """All confidence values are in [0.0, 1.0]."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(
        commitments=["I need to call."],
        observations=["I noticed something."],
        relationship_items=["Sara said hello."],
        unknown_items=["Unknown."],
    )
    drafts = service.commit(result)
    for d in drafts:
        assert 0.0 <= d.confidence <= 1.0, f"Invalid confidence {d.confidence} on {d.title}"


def test_unknown_confidence_is_zero() -> None:
    """Unknown and question drafts have confidence 0.0."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(
        unknown_items=["Random."],
        questions=["Why?"],
    )
    drafts = service.commit(result)
    for d in drafts:
        assert d.confidence == 0.0


def test_relationship_confidence_higher_than_commitment() -> None:
    """Relationship confidence tier is higher than commitment tier."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(
        commitments=["I need to call."],
        relationship_items=["Sara said hello."],
    )
    drafts = service.commit(result)
    commitment_conf = next(d.confidence for d in drafts if d.object_type == OBJECT_TYPE_COMMITMENT)
    relationship_conf = next(d.confidence for d in drafts if d.object_type == OBJECT_TYPE_RELATIONSHIP)
    assert relationship_conf > commitment_conf


# ------------------------------------------------------------------
# Storage
# ------------------------------------------------------------------

def test_drafts_stored_in_memory_store() -> None:
    """All produced drafts are retrievable from MemoryStore."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(commitments=["I need to fix the outlet.", "I will call tomorrow."])
    drafts = service.commit(result)
    assert store.count(DraftMemory) == 2
    for d in drafts:
        assert store.get(DraftMemory, d.id) is not None


def test_drafts_have_unique_ids() -> None:
    """Every DraftMemory object has a unique id."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(
        commitments=["I need to call.", "I will fix this."],
        observations=["I noticed a problem."],
    )
    drafts = service.commit(result)
    ids = [d.id for d in drafts]
    assert len(ids) == len(set(ids))


def test_drafts_preserve_original_content() -> None:
    """DraftMemory.content exactly matches the original statement."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    original = "Sara said she wants to visit Hawaii."
    result = CaptureResult(relationship_items=[original])
    drafts = service.commit(result)
    assert drafts[0].content == original


# ------------------------------------------------------------------
# Mixed CaptureResult
# ------------------------------------------------------------------

def test_mixed_capture_result_produces_correct_draft_count() -> None:
    """Mixed CaptureResult produces one DraftMemory per statement."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(
        commitments=["I need to plan a date.", "Remember to pick up flowers."],
        observations=["I noticed the bedroom needs better lighting."],
        relationship_items=["Sara said she wants to go somewhere nice."],
        questions=["Should I book a reservation?"],
        unknown_items=["Completely random thought."],
    )
    drafts = service.commit(result)
    assert len(drafts) == 6
    assert store.count(DraftMemory) == 6


def test_empty_capture_result_produces_no_drafts() -> None:
    """An empty CaptureResult produces zero DraftMemory objects."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    drafts = service.commit(CaptureResult())
    assert drafts == []
    assert store.count(DraftMemory) == 0


def test_source_propagated_to_drafts() -> None:
    """The source label is propagated to every DraftMemory."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(commitments=["I need to call."])
    drafts = service.commit(result, source="telegram")
    assert drafts[0].source == "telegram"


# ------------------------------------------------------------------
# Title generation
# ------------------------------------------------------------------

def test_title_derived_from_content() -> None:
    """DraftMemory.title is a non-empty string derived from content."""
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(commitments=["I need to call the electrician."])
    drafts = service.commit(result)
    assert drafts[0].title
    assert drafts[0].title != drafts[0].content or len(drafts[0].content) <= 60


def test_long_content_title_is_truncated() -> None:
    """Titles longer than 60 chars are truncated with an ellipsis."""
    long_statement = "I need to remember to call the contractor about the bathroom renovation project tomorrow morning."
    store = MemoryStore()
    service = MemoryCommitService(store)
    result = CaptureResult(commitments=[long_statement])
    drafts = service.commit(result)
    assert len(drafts[0].title) <= 63  # 60 chars + potential ellipsis
    assert "…" in drafts[0].title


# ------------------------------------------------------------------
# Runner
# ------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_draft_memory_default_state,
        test_draft_memory_default_confidence,
        test_draft_memory_invalid_object_type_raises,
        test_draft_memory_invalid_confidence_raises,
        test_draft_memory_confidence_zero_is_valid,
        test_draft_memory_all_valid_types,
        test_commit_single_commitment,
        test_commit_single_observation,
        test_commit_single_relationship,
        test_commit_unknown_item,
        test_commit_question_becomes_unknown,
        test_commit_object_types_assigned_correctly,
        test_all_drafts_have_draft_state,
        test_confidence_values_are_valid_floats,
        test_unknown_confidence_is_zero,
        test_relationship_confidence_higher_than_commitment,
        test_drafts_stored_in_memory_store,
        test_drafts_have_unique_ids,
        test_drafts_preserve_original_content,
        test_mixed_capture_result_produces_correct_draft_count,
        test_empty_capture_result_produces_no_drafts,
        test_source_propagated_to_drafts,
        test_title_derived_from_content,
        test_long_content_title_is_truncated,
    ]
    for test in tests:
        test()
        print(f"  PASS  {test.__name__}")
    print(f"\nAll {len(tests)} tests passed.")
