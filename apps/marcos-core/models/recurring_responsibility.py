"""Memory object representing a recurring responsibility that repeats on a schedule."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class RecurringResponsibility:
    """A responsibility that resets and must be completed on a regular schedule.

    Distinct from a Habit in that it is obligation-driven rather than
    behaviour-driven. Examples include Chai's vet visits, bill payments,
    and household deep-cleaning tasks.

    Attributes:
        id: Unique identifier. Will map to a UUID primary key in PostgreSQL.
        title: Short description of the responsibility.
        description: Full context and instructions.
        domain: Life domain (e.g. 'Home', 'Finance', 'Health').
        interval_days: How many days between occurrences.
        status: Current state — 'active', 'paused'.
        created_at: Timestamp when this responsibility was registered.
        last_completed_at: Timestamp of most recent completion.
        next_due_at: Calculated timestamp for the next occurrence.
        owner: Who is responsible — 'marcos', 'sara', 'shared'.
        notes: Optional additional context.
    """

    id: str
    title: str
    description: str = ""
    domain: str = ""
    interval_days: int = 7
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_completed_at: Optional[datetime] = None
    next_due_at: Optional[datetime] = None
    owner: str = "marcos"
    notes: str = ""

    def is_overdue(self) -> bool:
        """Return True if the responsibility is past its next due date."""
        if self.next_due_at is None:
            return False
        if self.status == "paused":
            return False
        return datetime.utcnow() > self.next_due_at
