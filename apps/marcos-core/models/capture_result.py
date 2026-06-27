"""Data model for the structured output of the Capture Pipeline."""

from dataclasses import dataclass, field


@dataclass
class CaptureResult:
    """The classified output produced by processing a single Capture.

    Each statement from the raw capture is routed into exactly one bucket.
    No statement is silently dropped — unclassified input lands in
    unknown_items for human review or future AI classification.

    Future evolution:
        - commitments and observations will be promoted to full memory objects
          (with generated ids) when the Memory Layer write path is connected.
        - AI classification will replace or augment rule handlers, reducing
          the volume of unknown_items.
        - relationship_items will link to the Relationships knowledge category.

    Attributes:
        commitments: Statements classified as commitments Marcos must act on.
        observations: Factual observations or noticed patterns.
        relationship_items: Statements relating to Sara or other relationships.
        questions: Statements phrased as questions requiring follow-up.
        unknown_items: Statements that did not match any handler.
    """

    commitments: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    relationship_items: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    unknown_items: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        """Total number of classified statements across all buckets."""
        return (
            len(self.commitments)
            + len(self.observations)
            + len(self.relationship_items)
            + len(self.questions)
            + len(self.unknown_items)
        )

    @property
    def is_empty(self) -> bool:
        """True when no statements were extracted from the input."""
        return self.total == 0
