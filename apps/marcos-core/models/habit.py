"""Memory object representing a recurring habit Marcos is building or maintaining."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Habit:
    """A behaviour Marcos is deliberately building or maintaining over time.

    Habits are tracked longitudinally. The Memory Layer monitors consistency
    and the executive team surfaces recommendations when habits are broken.

    Attributes:
        id: Unique identifier. Will map to a UUID primary key in PostgreSQL.
        title: Short name of the habit.
        description: Why this habit matters and what it involves.
        domain: Life domain (e.g. 'Health', 'Personal', 'Marriage').
        frequency: How often the habit should occur — 'daily', 'weekly', 'monthly'.
        status: Current state — 'active', 'paused', 'abandoned'.
        created_at: Timestamp when tracking began.
        last_completed_at: Timestamp of most recent completion.
        current_streak: Number of consecutive successful completions.
        longest_streak: Historical best streak.
        target_streak: Goal streak length.
    """

    id: str
    title: str
    description: str = ""
    domain: str = ""
    frequency: str = "daily"
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_completed_at: Optional[datetime] = None
    current_streak: int = 0
    longest_streak: int = 0
    target_streak: int = 0
