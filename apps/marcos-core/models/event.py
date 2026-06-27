"""Data model and type constants for the Marcos OS Event Bus."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# ---------------------------------------------------------------------------
# Event type constants
# ---------------------------------------------------------------------------

CAPTURE_CREATED = "capture.created"
DRAFT_CREATED = "draft.created"
MEMORY_UPDATED = "memory.updated"
RECOMMENDATIONS_GENERATED = "recommendations.generated"
MORNING_BRIEF_CREATED = "morning_brief.created"


@dataclass
class Event:
    """A single runtime event published on the Marcos OS Event Bus.

    Events are the communication primitive between system components.
    Any component may publish an event; any number of subscribers may
    react to it. The Event Bus is intentionally synchronous in v1.

    Future evolution:
        - Async dispatch when I/O-bound subscribers are introduced.
        - Persistent event log (PostgreSQL) for audit and replay.
        - Event sourcing for memory state reconstruction.
        - Distributed dispatch when Telegram, Home Assistant, and
          other integrations communicate through the bus.

    Attributes:
        id: Unique identifier for this event instance.
        event_type: One of the EVENT_TYPE_* constants. Subscribers
            filter on this value.
        payload: Arbitrary data associated with the event. Structure
            is defined by the publisher and documented per event type.
        created_at: UTC timestamp when the event was created.
    """

    id: str
    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
