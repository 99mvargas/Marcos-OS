"""Memory object representing a time-bounded project."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Project:
    """A goal-oriented effort composed of multiple tasks and commitments.

    Projects are time-bounded and have a defined outcome. Completed projects
    are archived rather than deleted, preserving history for future AI reasoning.

    Attributes:
        id: Unique identifier. Will map to a UUID primary key in PostgreSQL.
        title: Project name.
        description: Purpose and desired outcome.
        status: Lifecycle state — 'active', 'on_hold', 'completed', 'cancelled'.
        priority: Integer priority (1 = highest).
        domain: Life domain this project belongs to.
        created_at: Timestamp when the project was created.
        started_at: Timestamp when active work began.
        target_completion_at: Desired completion date.
        completed_at: Actual completion timestamp.
        outcome: Description of the result once completed.
        tags: Optional list of descriptive tags for retrieval.
    """

    id: str
    title: str
    description: str = ""
    status: str = "active"
    priority: int = 5
    domain: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    target_completion_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    outcome: str = ""
    tags: list[str] = field(default_factory=list)
