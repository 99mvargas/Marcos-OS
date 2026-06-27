"""Data model for a Draft Memory object in the Marcos OS memory lifecycle."""

from dataclasses import dataclass, field
from datetime import datetime

# Valid object types for a DraftMemory.
OBJECT_TYPE_COMMITMENT = "Commitment"
OBJECT_TYPE_OBSERVATION = "Observation"
OBJECT_TYPE_RELATIONSHIP = "Relationship"
OBJECT_TYPE_UNKNOWN = "Unknown"

# The only state a newly created DraftMemory may have.
STATE_DRAFT = "Draft"

# Future states — defined here for documentation; not assigned by this layer.
# STATE_ACTIVE = "Active"
# STATE_COMPLETED = "Completed"
# STATE_ARCHIVED = "Archived"


@dataclass
class DraftMemory:
    """A provisional memory object awaiting review before becoming Active.

    DraftMemory is the first stage in the Marcos OS memory lifecycle.
    Nothing enters the Active layer automatically. Every capture first
    becomes a Draft so that Marcos (or a future AI reviewer) can approve,
    edit, or discard it before it affects the system's long-term knowledge.

    Memory lifecycle:
        Draft → Active → Completed → Archived

    Attributes:
        id: Unique identifier. Will map to a UUID primary key in PostgreSQL.
        object_type: Classification of the draft — one of 'Commitment',
            'Observation', 'Relationship', or 'Unknown'.
        title: Short label derived from the source statement.
        content: The original statement text, preserved verbatim.
        source: Origin of the capture — 'manual', 'telegram', 'voice', etc.
        state: Lifecycle state. Always 'Draft' at creation.
        created_at: UTC timestamp when this draft was created.
        confidence: Router confidence in this classification (0.0–1.0).
            Rule-based classification uses fixed tier values; AI
            classification will return variable scores in a future sprint.
    """

    id: str
    object_type: str
    title: str
    content: str
    source: str = "manual"
    state: str = STATE_DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 1.0

    def __post_init__(self) -> None:
        """Validate field values at construction time."""
        valid_types = {
            OBJECT_TYPE_COMMITMENT,
            OBJECT_TYPE_OBSERVATION,
            OBJECT_TYPE_RELATIONSHIP,
            OBJECT_TYPE_UNKNOWN,
        }
        if self.object_type not in valid_types:
            raise ValueError(
                f"Invalid object_type '{self.object_type}'. "
                f"Must be one of: {sorted(valid_types)}"
            )
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                f"confidence must be between 0.0 and 1.0, got {self.confidence}"
            )
