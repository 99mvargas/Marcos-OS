"""Memory object representing a commitment made by or to Marcos."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Commitment:
    """A promise or obligation that must be tracked until resolved.

    A commitment originates from Marcos stating he will do something, Sara
    requesting something, or Marcos accepting an AI recommendation. It remains
    active until completed, cancelled, or replaced.

    Attributes:
        id: Unique identifier. Will map to a UUID primary key in PostgreSQL.
        title: Short description of the commitment.
        description: Full context and detail.
        status: Lifecycle state — 'active', 'completed', 'cancelled', 'overdue'.
        priority: Integer priority aligned with the Memory Layer priority model
            (1 = Faith, 2 = Family, ... 10 = Convenience).
        created_at: Timestamp when the commitment was recorded.
        due_at: Optional deadline.
        completed_at: Timestamp when the commitment was resolved.
        source: Origin of the commitment — 'marcos', 'sara', 'ai', 'system'.
        domain: Life domain this commitment belongs to (e.g. 'Marriage', 'Business').
    """

    id: str
    title: str
    description: str
    status: str = "active"
    priority: int = 5
    created_at: datetime = field(default_factory=datetime.utcnow)
    due_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    source: str = "marcos"
    domain: str = ""

    def is_overdue(self) -> bool:
        """Return True if the commitment is past its due date and not resolved."""
        if self.due_at is None:
            return False
        if self.status in ("completed", "cancelled"):
            return False
        return datetime.utcnow() > self.due_at
