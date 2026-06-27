"""Memory object representing an observation or captured insight."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Observation:
    """A recorded insight, pattern, or event captured by Marcos or the system.

    Observations feed the learning model. Over time the executive team
    analyses observation patterns to improve future recommendations.

    Attributes:
        id: Unique identifier. Will map to a UUID primary key in PostgreSQL.
        content: The raw observation text.
        domain: Life domain this observation relates to.
        source: Origin — 'marcos', 'ai', 'system', 'capture_hub'.
        created_at: Timestamp when the observation was recorded.
        tags: Optional descriptive tags for retrieval and pattern analysis.
        related_commitment_id: Optional link to a related Commitment.
        related_project_id: Optional link to a related Project.
    """

    id: str
    content: str
    domain: str = ""
    source: str = "marcos"
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: list[str] = field(default_factory=list)
    related_commitment_id: str | None = None
    related_project_id: str | None = None
