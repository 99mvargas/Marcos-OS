"""Tests for EventBus and Event model."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import datetime

from core.event_bus import EventBus
from models.event import (
    CAPTURE_CREATED,
    DRAFT_CREATED,
    MEMORY_UPDATED,
    MORNING_BRIEF_CREATED,
    RECOMMENDATIONS_GENERATED,
    Event,
)


# ------------------------------------------------------------------
# Event model
# ------------------------------------------------------------------

def test_event_model_fields() -> None:
    """Event stores id, event_type, payload, and created_at."""
    e = Event(id="abc", event_type=CAPTURE_CREATED, payload={"key": "val"})
    assert e.id == "abc"
    assert e.event_type == CAPTURE_CREATED
    assert e.payload == {"key": "val"}
    assert isinstance(e.created_at, datetime)


def test_event_payload_defaults_to_empty_dict() -> None:
    """Event.payload defaults to empty dict when not provided."""
    e = Event(id="x", event_type=CAPTURE_CREATED)
    assert e.payload == {}


def test_event_type_constants_are_strings() -> None:
    """All event type constants are non-empty strings."""
    for constant in [
        CAPTURE_CREATED,
        DRAFT_CREATED,
        MEMORY_UPDATED,
        RECOMMENDATIONS_GENERATED,
        MORNING_BRIEF_CREATED,
    ]:
        assert isinstance(constant, str)
        assert constant


# ------------------------------------------------------------------
# EventBus — publishing
# ------------------------------------------------------------------

def test_publish_returns_event() -> None:
    """publish() returns an Event object."""
    bus = EventBus()
    event = bus.publish(CAPTURE_CREATED)
    assert isinstance(event, Event)
    assert event.event_type == CAPTURE_CREATED


def test_publish_assigns_unique_ids() -> None:
    """Each published event receives a unique id."""
    bus = EventBus()
    e1 = bus.publish(CAPTURE_CREATED)
    e2 = bus.publish(CAPTURE_CREATED)
    assert e1.id != e2.id


def test_publish_payload_attached() -> None:
    """Published event carries the provided payload."""
    bus = EventBus()
    event = bus.publish(DRAFT_CREATED, payload={"count": 3})
    assert event.payload["count"] == 3


def test_publish_no_subscribers_does_not_raise() -> None:
    """Publishing with no subscribers is a no-op and does not raise."""
    bus = EventBus()
    bus.publish(CAPTURE_CREATED)  # Should not raise.


# ------------------------------------------------------------------
# EventBus — subscription
# ------------------------------------------------------------------

def test_subscribe_and_receive_event() -> None:
    """Subscriber callback is called when matching event is published."""
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(CAPTURE_CREATED, received.append)
    bus.publish(CAPTURE_CREATED)
    assert len(received) == 1


def test_subscribe_receives_correct_event_type() -> None:
    """Subscriber for CAPTURE_CREATED does not receive DRAFT_CREATED."""
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(CAPTURE_CREATED, received.append)
    bus.publish(DRAFT_CREATED)
    assert len(received) == 0


def test_subscriber_receives_payload() -> None:
    """Subscriber receives the full Event including payload."""
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(MEMORY_UPDATED, received.append)
    bus.publish(MEMORY_UPDATED, payload={"object_id": "abc123"})
    assert received[0].payload["object_id"] == "abc123"


# ------------------------------------------------------------------
# EventBus — multiple subscribers
# ------------------------------------------------------------------

def test_multiple_subscribers_all_called() -> None:
    """Multiple subscribers for the same event type are all called."""
    bus = EventBus()
    calls: list[str] = []
    bus.subscribe(RECOMMENDATIONS_GENERATED, lambda e: calls.append("first"))
    bus.subscribe(RECOMMENDATIONS_GENERATED, lambda e: calls.append("second"))
    bus.publish(RECOMMENDATIONS_GENERATED)
    assert calls == ["first", "second"]


def test_subscribers_called_in_registration_order() -> None:
    """Subscribers are called in the order they were registered."""
    bus = EventBus()
    order: list[int] = []
    bus.subscribe(MORNING_BRIEF_CREATED, lambda e: order.append(1))
    bus.subscribe(MORNING_BRIEF_CREATED, lambda e: order.append(2))
    bus.subscribe(MORNING_BRIEF_CREATED, lambda e: order.append(3))
    bus.publish(MORNING_BRIEF_CREATED)
    assert order == [1, 2, 3]


def test_independent_event_types_do_not_cross() -> None:
    """Subscribers for different event types do not receive each other's events."""
    bus = EventBus()
    capture_calls: list[Event] = []
    draft_calls: list[Event] = []
    bus.subscribe(CAPTURE_CREATED, capture_calls.append)
    bus.subscribe(DRAFT_CREATED, draft_calls.append)
    bus.publish(CAPTURE_CREATED)
    assert len(capture_calls) == 1
    assert len(draft_calls) == 0


# ------------------------------------------------------------------
# EventBus — unsubscribe
# ------------------------------------------------------------------

def test_unsubscribe_removes_callback() -> None:
    """Unsubscribed callback is not called on subsequent publishes."""
    bus = EventBus()
    calls: list[Event] = []

    def handler(e: Event) -> None:
        calls.append(e)

    bus.subscribe(CAPTURE_CREATED, handler)
    bus.publish(CAPTURE_CREATED)
    assert len(calls) == 1

    bus.unsubscribe(CAPTURE_CREATED, handler)
    bus.publish(CAPTURE_CREATED)
    assert len(calls) == 1  # Still 1 — not called again.


def test_unsubscribe_nonexistent_callback_does_not_raise() -> None:
    """Unsubscribing a callback that was never registered is a no-op."""
    bus = EventBus()
    bus.unsubscribe(CAPTURE_CREATED, lambda e: None)  # Should not raise.


def test_unsubscribe_one_of_two_subscribers() -> None:
    """Unsubscribing one callback leaves the other intact."""
    bus = EventBus()
    calls_a: list[Event] = []
    calls_b: list[Event] = []

    def handler_a(e: Event) -> None:
        calls_a.append(e)

    def handler_b(e: Event) -> None:
        calls_b.append(e)

    bus.subscribe(CAPTURE_CREATED, handler_a)
    bus.subscribe(CAPTURE_CREATED, handler_b)
    bus.unsubscribe(CAPTURE_CREATED, handler_a)
    bus.publish(CAPTURE_CREATED)

    assert len(calls_a) == 0
    assert len(calls_b) == 1


# ------------------------------------------------------------------
# EventBus — dispatch
# ------------------------------------------------------------------

def test_dispatch_existing_event() -> None:
    """dispatch() delivers a pre-constructed Event to subscribers."""
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(CAPTURE_CREATED, received.append)
    event = Event(id="manual-id", event_type=CAPTURE_CREATED, payload={"x": 1})
    bus.dispatch(event)
    assert len(received) == 1
    assert received[0].id == "manual-id"


def test_dispatch_unknown_event_type_does_not_raise() -> None:
    """Dispatching an unknown event type with no subscribers is a no-op."""
    bus = EventBus()
    event = Event(id="x", event_type="unknown.event")
    bus.dispatch(event)  # Should not raise.


# ------------------------------------------------------------------
# EventBus — error handling
# ------------------------------------------------------------------

def test_failing_subscriber_does_not_block_others() -> None:
    """If one subscriber raises, remaining subscribers still receive the event."""
    bus = EventBus()
    second_called: list[bool] = []

    def bad_handler(e: Event) -> None:
        raise ValueError("subscriber error")

    def good_handler(e: Event) -> None:
        second_called.append(True)

    bus.subscribe(CAPTURE_CREATED, bad_handler)
    bus.subscribe(CAPTURE_CREATED, good_handler)

    try:
        bus.publish(CAPTURE_CREATED)
    except RuntimeError:
        pass

    assert second_called == [True]


def test_failing_subscriber_raises_runtime_error() -> None:
    """RuntimeError is raised after dispatch when a subscriber fails."""
    bus = EventBus()
    bus.subscribe(CAPTURE_CREATED, lambda e: (_ for _ in ()).throw(ValueError("boom")))
    try:
        bus.publish(CAPTURE_CREATED)
        assert False, "Expected RuntimeError"
    except RuntimeError as e:
        assert "subscriber" in str(e).lower()


# ------------------------------------------------------------------
# EventBus — introspection and clear
# ------------------------------------------------------------------

def test_subscribers_for_returns_registered_callbacks() -> None:
    """subscribers_for() returns all callbacks for a given event type."""
    bus = EventBus()
    cb = lambda e: None
    bus.subscribe(CAPTURE_CREATED, cb)
    assert cb in bus.subscribers_for(CAPTURE_CREATED)


def test_subscribers_for_unknown_type_returns_empty() -> None:
    """subscribers_for() returns an empty list for an unregistered event type."""
    bus = EventBus()
    assert bus.subscribers_for("no.such.event") == []


def test_clear_removes_all_subscribers() -> None:
    """clear() resets the bus to an empty state."""
    bus = EventBus()
    calls: list[Event] = []
    bus.subscribe(CAPTURE_CREATED, calls.append)
    bus.clear()
    bus.publish(CAPTURE_CREATED)
    assert calls == []


# ------------------------------------------------------------------
# Runner
# ------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_event_model_fields,
        test_event_payload_defaults_to_empty_dict,
        test_event_type_constants_are_strings,
        test_publish_returns_event,
        test_publish_assigns_unique_ids,
        test_publish_payload_attached,
        test_publish_no_subscribers_does_not_raise,
        test_subscribe_and_receive_event,
        test_subscribe_receives_correct_event_type,
        test_subscriber_receives_payload,
        test_multiple_subscribers_all_called,
        test_subscribers_called_in_registration_order,
        test_independent_event_types_do_not_cross,
        test_unsubscribe_removes_callback,
        test_unsubscribe_nonexistent_callback_does_not_raise,
        test_unsubscribe_one_of_two_subscribers,
        test_dispatch_existing_event,
        test_dispatch_unknown_event_type_does_not_raise,
        test_failing_subscriber_does_not_block_others,
        test_failing_subscriber_raises_runtime_error,
        test_subscribers_for_returns_registered_callbacks,
        test_subscribers_for_unknown_type_returns_empty,
        test_clear_removes_all_subscribers,
    ]
    for test in tests:
        test()
        print(f"  PASS  {test.__name__}")
    print(f"\nAll {len(tests)} tests passed.")
