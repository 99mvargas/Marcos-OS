"""Converts CaptureResults into DraftMemory objects and stores them.

The MemoryCommitService is the bridge between the Capture Pipeline and the
Memory Layer. It takes the classified output of a capture cycle and produces
Draft Memory objects — one per statement — which are stored in MemoryStore
for future review and promotion.

Nothing becomes Active automatically. This service is intentionally limited
to Draft creation. Approval, editing, and promotion are handled by future
services (human review UI or AI reviewer).
"""

import uuid
from datetime import datetime

from memory.memory_store import MemoryStore
from models.capture_result import CaptureResult
from models.draft_memory import (
    STATE_DRAFT,
    OBJECT_TYPE_COMMITMENT,
    OBJECT_TYPE_OBSERVATION,
    OBJECT_TYPE_RELATIONSHIP,
    OBJECT_TYPE_UNKNOWN,
    DraftMemory,
)

# Confidence tiers assigned by rule-based classification.
# These will be replaced by variable scores when AI classification is active.
_CONFIDENCE_COMMITMENT = 0.85
_CONFIDENCE_OBSERVATION = 0.80
_CONFIDENCE_RELATIONSHIP = 0.90
_CONFIDENCE_UNKNOWN = 0.0


def _make_title(content: str, max_length: int = 60) -> str:
    """Derive a short title from the source statement.

    Truncates to max_length characters and appends an ellipsis if the
    statement exceeds that length. Strips trailing punctuation from the title.

    Args:
        content: The original statement text.
        max_length: Maximum character length of the title.

    Returns:
        A short, readable title string.
    """
    stripped = content.strip().rstrip(".!?,;:")
    if len(stripped) <= max_length:
        return stripped
    return stripped[:max_length].rstrip() + "…"


def _new_id() -> str:
    """Generate a unique identifier for a DraftMemory object.

    Returns:
        A UUID4 string. Will become a UUID primary key in PostgreSQL.
    """
    return str(uuid.uuid4())


class MemoryCommitService:
    """Converts a CaptureResult into DraftMemory objects stored in MemoryStore.

    Each statement from the CaptureResult is converted to a single DraftMemory
    with the appropriate object_type and confidence tier. All drafts enter
    the store with state='Draft' and are never promoted automatically.

    Questions from the capture pipeline have no dedicated DraftMemory type in
    the current spec. They are stored as Unknown drafts so no input is lost.

    Future evolution:
        - AI reviewer service promotes high-confidence drafts to Active.
        - Human review UI surfaces drafts for Marcos to approve or discard.
        - Confidence values replaced by AI-generated scores.
        - Questions get a dedicated object_type when the spec defines one.

    Attributes:
        _store: The MemoryStore instance used to persist DraftMemory objects.
    """

    def __init__(self, store: MemoryStore) -> None:
        """Initialise the service with a MemoryStore.

        Args:
            store: The MemoryStore instance. All drafts are written here.
        """
        self._store = store

    def commit(self, capture_result: CaptureResult, source: str = "manual") -> list[DraftMemory]:
        """Convert a CaptureResult into DraftMemory objects and store them.

        Processes all five CaptureResult buckets. Questions are stored as
        Unknown drafts. No bucket is silently ignored.

        Args:
            capture_result: The classified output from the CapturePipeline.
            source: Origin label propagated to each DraftMemory.

        Returns:
            List of all DraftMemory objects created and stored this cycle,
            in the order they were processed.
        """
        drafts: list[DraftMemory] = []

        mapping: list[tuple[list[str], str, float]] = [
            (capture_result.commitments, OBJECT_TYPE_COMMITMENT, _CONFIDENCE_COMMITMENT),
            (capture_result.observations, OBJECT_TYPE_OBSERVATION, _CONFIDENCE_OBSERVATION),
            (capture_result.relationship_items, OBJECT_TYPE_RELATIONSHIP, _CONFIDENCE_RELATIONSHIP),
            (capture_result.questions, OBJECT_TYPE_UNKNOWN, _CONFIDENCE_UNKNOWN),
            (capture_result.unknown_items, OBJECT_TYPE_UNKNOWN, _CONFIDENCE_UNKNOWN),
        ]

        for statements, object_type, confidence in mapping:
            for statement in statements:
                draft = DraftMemory(
                    id=_new_id(),
                    object_type=object_type,
                    title=_make_title(statement),
                    content=statement,
                    source=source,
                    state=STATE_DRAFT,
                    created_at=datetime.utcnow(),
                    confidence=confidence,
                )
                self._store.create(draft)
                drafts.append(draft)

        return drafts
