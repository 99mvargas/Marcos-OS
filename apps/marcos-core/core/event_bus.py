"""Synchronous Event Bus for Marcos OS inter-component communication.

The Event Bus allows components to communicate without direct coupling.
Publishers emit events; subscribers react to them. Neither party holds
a reference to the other.

This is a simple synchronous implementation — no threads, no queues,
no networking. Dispatch is immediate and blocking. This is intentional
for v1: the system is single-process and the overhead of async dispatch
is not yet justified.

Future evolution:
    - Async dispatch (asyncio) when I/O-bound subscribers are introduced.
    - Persistent event log written to PostgreSQL for audit and replay.
    - Cross-process or networked dispatch when integrations (Telegram,
      Home Assistant, n8n) communicate through the bus.
    - Dead-letter queue for failed subscriber callbacks.
"""

import uuid
from collections import defaultdict
from datetime import datetime
from typing import Callable

from models.event import Event

# Type alias for subscriber callbacks.
Callback = Callable[[Event], None]


class EventBus:
    """Synchronous publish-subscribe event bus.

    Components subscribe to event types by registering callbacks.
    When an event is published, all registered callbacks for that
    event type are invoked immediately in registration order.

    Subscribers that raise exceptions do not prevent other subscribers
    from receiving the event — errors are collected and re-raised as a
    group after all subscribers have been called.

    Attributes:
        _subscribers: Mapping of event_type -> list of callbacks.
    """

    def __init__(self) -> None:
        """Initialise the EventBus with an empty subscriber registry."""
        self._subscribers: dict[str, list[Callback]] = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callback) -> None:
        """Register a callback for a specific event type.

        A callback may be registered for multiple event types by calling
        this method once per type. Registering the same callback twice
        for the same event type results in it being called twice per dispatch.

        Args:
            event_type: The event type string to subscribe to.
            callback: A callable that accepts a single Event argument.
        """
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callback) -> None:
        """Remove a callback from a specific event type.

        Silently does nothing if the callback was not registered for
        that event type.

        Args:
            event_type: The event type to unsubscribe from.
            callback: The callback to remove.
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
            except ValueError:
                pass

    def publish(self, event_type: str, payload: dict | None = None) -> Event:
        """Create an Event and dispatch it to all registered subscribers.

        Convenience method that constructs the Event object and calls
        dispatch(). Use this when you do not need to hold a reference
        to the Event before dispatching.

        Args:
            event_type: The event type string (use EVENT_TYPE_* constants).
            payload: Optional dict of event data. Defaults to empty dict.

        Returns:
            The Event object that was created and dispatched.
        """
        event = Event(
            id=str(uuid.uuid4()),
            event_type=event_type,
            payload=payload or {},
            created_at=datetime.utcnow(),
        )
        self.dispatch(event)
        return event

    def dispatch(self, event: Event) -> None:
        """Dispatch an existing Event to all registered subscribers.

        All subscribers for the event's event_type are called in
        registration order. If a subscriber raises an exception, remaining
        subscribers still receive the event. All exceptions are collected
        and re-raised together as a RuntimeError after dispatch completes.

        Args:
            event: The Event to dispatch.

        Raises:
            RuntimeError: If one or more subscribers raised exceptions.
        """
        errors: list[tuple[Callback, Exception]] = []

        for callback in list(self._subscribers.get(event.event_type, [])):
            try:
                callback(event)
            except Exception as exc:
                errors.append((callback, exc))

        if errors:
            details = "; ".join(
                f"{cb.__name__}: {exc}" for cb, exc in errors
            )
            raise RuntimeError(
                f"{len(errors)} subscriber(s) raised exceptions during dispatch "
                f"of '{event.event_type}': {details}"
            )

    def subscribers_for(self, event_type: str) -> list[Callback]:
        """Return the list of callbacks registered for an event type.

        Args:
            event_type: The event type to inspect.

        Returns:
            List of registered callbacks. Empty list if none registered.
        """
        return list(self._subscribers.get(event_type, []))

    def clear(self) -> None:
        """Remove all subscribers from all event types.

        Primarily used in tests to reset bus state between test cases
        when a shared bus instance is used.
        """
        self._subscribers.clear()
