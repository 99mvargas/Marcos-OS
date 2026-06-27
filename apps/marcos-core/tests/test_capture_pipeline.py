"""Tests for CapturePipeline, CaptureRouter, and CaptureResult."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.capture import Capture
from models.capture_result import CaptureResult
from services.capture_pipeline import CapturePipeline, _split_statements
from services.capture_router import (
    BUCKET_COMMITMENT,
    BUCKET_OBSERVATION,
    BUCKET_QUESTION,
    BUCKET_RELATIONSHIP,
    BUCKET_UNKNOWN,
    CaptureRouter,
)


# ------------------------------------------------------------------
# Statement splitter
# ------------------------------------------------------------------

def test_split_single_sentence() -> None:
    result = _split_statements("I need to call the contractor.")
    assert result == ["I need to call the contractor."]


def test_split_multiple_sentences() -> None:
    result = _split_statements("I need to call the contractor. Remember to buy groceries.")
    assert len(result) == 2


def test_split_on_newlines() -> None:
    result = _split_statements("I need to call the contractor\nRemember to buy groceries")
    assert len(result) == 2


def test_split_question_mark_preserved() -> None:
    result = _split_statements("Should I call the plumber?")
    assert result[0].endswith("?")


def test_split_empty_string_returns_empty() -> None:
    assert _split_statements("") == []


def test_split_blank_lines_ignored() -> None:
    result = _split_statements("I need to call.\n\n\nRemember to buy.")
    assert len(result) == 2


# ------------------------------------------------------------------
# CaptureRouter — individual handlers
# ------------------------------------------------------------------

def test_router_commitment_i_need_to() -> None:
    assert CaptureRouter().route("I need to call the contractor") == BUCKET_COMMITMENT


def test_router_commitment_remember_to() -> None:
    assert CaptureRouter().route("Remember to buy groceries") == BUCKET_COMMITMENT


def test_router_commitment_i_will() -> None:
    assert CaptureRouter().route("I will call the plumber tomorrow") == BUCKET_COMMITMENT


def test_router_commitment_i_have_to() -> None:
    assert CaptureRouter().route("I have to fix the light switch") == BUCKET_COMMITMENT


def test_router_commitment_buy() -> None:
    assert CaptureRouter().route("Buy more dog food") == BUCKET_COMMITMENT


def test_router_commitment_follow_up() -> None:
    assert CaptureRouter().route("Follow up with the client") == BUCKET_COMMITMENT


def test_router_relationship_sara_said() -> None:
    assert CaptureRouter().route("Sara said she wants to go to the Maldives") == BUCKET_RELATIONSHIP


def test_router_relationship_sara_wants() -> None:
    assert CaptureRouter().route("Sara wants flowers this week") == BUCKET_RELATIONSHIP


def test_router_relationship_sara_likes() -> None:
    assert CaptureRouter().route("Sara likes when I plan dates in advance") == BUCKET_RELATIONSHIP


def test_router_relationship_sara_needs() -> None:
    assert CaptureRouter().route("Sara needs more help with the dog") == BUCKET_RELATIONSHIP


def test_router_observation_i_noticed() -> None:
    assert CaptureRouter().route("I noticed the living room light is too dim") == BUCKET_OBSERVATION


def test_router_observation_chai() -> None:
    assert CaptureRouter().route("Chai has been pulling less on the leash") == BUCKET_OBSERVATION


def test_router_observation_the_kitchen() -> None:
    assert CaptureRouter().route("The kitchen needs better organization") == BUCKET_OBSERVATION


def test_router_observation_this_morning() -> None:
    assert CaptureRouter().route("This morning I felt behind on everything") == BUCKET_OBSERVATION


def test_router_question() -> None:
    assert CaptureRouter().route("Should I hire a cleaner?") == BUCKET_QUESTION


def test_router_question_no_mark_is_not_question() -> None:
    result = CaptureRouter().route("What if we get a cleaner")
    assert result != BUCKET_QUESTION


def test_router_unknown() -> None:
    assert CaptureRouter().route("Random unclassifiable input xyz") == BUCKET_UNKNOWN


def test_router_empty_string_is_unknown() -> None:
    assert CaptureRouter().route("") == BUCKET_UNKNOWN


def test_router_case_insensitive() -> None:
    assert CaptureRouter().route("I NEED TO call someone") == BUCKET_COMMITMENT
    assert CaptureRouter().route("SARA SAID something") == BUCKET_RELATIONSHIP


# ------------------------------------------------------------------
# CapturePipeline — single commitment
# ------------------------------------------------------------------

def test_pipeline_single_commitment() -> None:
    pipeline = CapturePipeline()
    result = pipeline.process_text("I need to call the electrician.")
    assert len(result.commitments) == 1
    assert result.observations == []
    assert result.unknown_items == []


# ------------------------------------------------------------------
# CapturePipeline — multiple commitments
# ------------------------------------------------------------------

def test_pipeline_multiple_commitments() -> None:
    pipeline = CapturePipeline()
    text = "I need to call the contractor. Remember to buy dog food. I will fix the bathroom light."
    result = pipeline.process_text(text)
    assert len(result.commitments) == 3
    assert result.total == 3


# ------------------------------------------------------------------
# CapturePipeline — relationship parsing
# ------------------------------------------------------------------

def test_pipeline_relationship() -> None:
    pipeline = CapturePipeline()
    result = pipeline.process_text("Sara said she wants to go to Hawaii this year.")
    assert len(result.relationship_items) == 1
    assert result.commitments == []


def test_pipeline_multiple_relationship_items() -> None:
    pipeline = CapturePipeline()
    text = "Sara wants flowers. Sara likes planned dates."
    result = pipeline.process_text(text)
    assert len(result.relationship_items) == 2


# ------------------------------------------------------------------
# CapturePipeline — observation parsing
# ------------------------------------------------------------------

def test_pipeline_observation() -> None:
    pipeline = CapturePipeline()
    result = pipeline.process_text("I noticed the living room lighting is too dim.")
    assert len(result.observations) == 1


def test_pipeline_chai_observation() -> None:
    pipeline = CapturePipeline()
    result = pipeline.process_text("Chai has been eating better this week.")
    assert len(result.observations) == 1


# ------------------------------------------------------------------
# CapturePipeline — questions
# ------------------------------------------------------------------

def test_pipeline_question() -> None:
    pipeline = CapturePipeline()
    result = pipeline.process_text("Should I hire a cleaner?")
    assert len(result.questions) == 1


# ------------------------------------------------------------------
# CapturePipeline — unknown captures
# ------------------------------------------------------------------

def test_pipeline_unknown() -> None:
    pipeline = CapturePipeline()
    result = pipeline.process_text("Completely unclassifiable statement here")
    assert len(result.unknown_items) == 1
    assert result.commitments == []


# ------------------------------------------------------------------
# CapturePipeline — mixed input
# ------------------------------------------------------------------

def test_pipeline_mixed_capture() -> None:
    pipeline = CapturePipeline()
    text = (
        "I need to plan a date for Sara this weekend. "
        "Sara said she wants to go somewhere nice. "
        "I noticed the bedroom could use better lighting. "
        "Remember to pick up flowers. "
        "Should I book a reservation? "
        "Completely random thought."
    )
    result = pipeline.process_text(text)
    assert len(result.commitments) == 2
    assert len(result.relationship_items) == 1
    assert len(result.observations) == 1
    assert len(result.questions) == 1
    assert len(result.unknown_items) == 1
    assert result.total == 6


# ------------------------------------------------------------------
# CaptureResult helpers
# ------------------------------------------------------------------

def test_capture_result_total() -> None:
    r = CaptureResult(commitments=["a", "b"], observations=["c"])
    assert r.total == 3


def test_capture_result_is_empty() -> None:
    assert CaptureResult().is_empty is True
    assert CaptureResult(commitments=["x"]).is_empty is False


# ------------------------------------------------------------------
# Capture model
# ------------------------------------------------------------------

def test_capture_model_defaults() -> None:
    from datetime import datetime
    c = Capture(raw_text="I need to do something.")
    assert c.source == "manual"
    assert isinstance(c.captured_at, datetime)


# ------------------------------------------------------------------
# Runner
# ------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_split_single_sentence,
        test_split_multiple_sentences,
        test_split_on_newlines,
        test_split_question_mark_preserved,
        test_split_empty_string_returns_empty,
        test_split_blank_lines_ignored,
        test_router_commitment_i_need_to,
        test_router_commitment_remember_to,
        test_router_commitment_i_will,
        test_router_commitment_i_have_to,
        test_router_commitment_buy,
        test_router_commitment_follow_up,
        test_router_relationship_sara_said,
        test_router_relationship_sara_wants,
        test_router_relationship_sara_likes,
        test_router_relationship_sara_needs,
        test_router_observation_i_noticed,
        test_router_observation_chai,
        test_router_observation_the_kitchen,
        test_router_observation_this_morning,
        test_router_question,
        test_router_question_no_mark_is_not_question,
        test_router_unknown,
        test_router_empty_string_is_unknown,
        test_router_case_insensitive,
        test_pipeline_single_commitment,
        test_pipeline_multiple_commitments,
        test_pipeline_relationship,
        test_pipeline_multiple_relationship_items,
        test_pipeline_observation,
        test_pipeline_chai_observation,
        test_pipeline_question,
        test_pipeline_unknown,
        test_pipeline_mixed_capture,
        test_capture_result_total,
        test_capture_result_is_empty,
        test_capture_model_defaults,
    ]
    for test in tests:
        test()
        print(f"  PASS  {test.__name__}")
    print(f"\nAll {len(tests)} tests passed.")
