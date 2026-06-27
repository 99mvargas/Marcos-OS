"""Pipeline that accepts raw capture text and returns a structured CaptureResult."""

from models.capture import Capture
from models.capture_result import CaptureResult
from services.capture_router import (
    BUCKET_COMMITMENT,
    BUCKET_OBSERVATION,
    BUCKET_QUESTION,
    BUCKET_RELATIONSHIP,
    BUCKET_UNKNOWN,
    CaptureRouter,
)

# Sentence-ending characters used to split raw text into statements.
_TERMINATORS = {".", "!", "?"}


def _split_statements(text: str) -> list[str]:
    """Split raw text into individual logical statements.

    Splits on sentence-ending punctuation (. ! ?) while preserving the
    terminator on the segment so handlers can detect questions via '?'.
    Empty segments are discarded. Lines separated by newlines are treated
    as implicit statement boundaries regardless of punctuation.

    Args:
        text: Raw multi-sentence input text.

    Returns:
        List of non-empty statement strings, stripped of leading/trailing
        whitespace.
    """
    statements: list[str] = []

    # Split on newlines first — each line is treated as a potential statement.
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Within a line, split on sentence terminators.
        buffer: list[str] = []
        for char in line:
            buffer.append(char)
            if char in _TERMINATORS:
                segment = "".join(buffer).strip()
                if segment:
                    statements.append(segment)
                buffer = []

        # Flush any remaining content without a terminator.
        remainder = "".join(buffer).strip()
        if remainder:
            statements.append(remainder)

    return statements


class CapturePipeline:
    """Processes raw capture input and routes each statement to a typed bucket.

    The pipeline is the entry point for all text entering Marcos OS. It
    splits input into logical statements, routes each through the
    CaptureRouter, and assembles a CaptureResult.

    No input is silently dropped. Unclassified statements land in
    unknown_items for review or future AI classification.

    Future evolution:
        - Voice transcripts processed before splitting (speech-to-text service).
        - Telegram messages piped in via n8n webhook.
        - Email summaries ingested via email integration.
        - Home Assistant events formatted and injected as captures.
        - AI classification layer added to CaptureRouter to reduce unknowns.

    Attributes:
        _router: The CaptureRouter instance used to classify statements.
    """

    def __init__(self, router: CaptureRouter | None = None) -> None:
        """Initialise the pipeline with an optional custom router.

        Args:
            router: A CaptureRouter instance. If None, a default router
                is created with the standard handler chain.
        """
        self._router = router or CaptureRouter()

    def process(self, capture: Capture) -> CaptureResult:
        """Process a Capture and return a structured CaptureResult.

        Splits the raw_text into statements, routes each statement, and
        populates the appropriate CaptureResult bucket.

        Args:
            capture: A Capture object containing the raw input text.

        Returns:
            A CaptureResult with statements distributed across buckets.
        """
        result = CaptureResult()
        statements = _split_statements(capture.raw_text)

        _bucket_map: dict[str, list[str]] = {
            BUCKET_COMMITMENT: result.commitments,
            BUCKET_OBSERVATION: result.observations,
            BUCKET_RELATIONSHIP: result.relationship_items,
            BUCKET_QUESTION: result.questions,
            BUCKET_UNKNOWN: result.unknown_items,
        }

        for statement in statements:
            bucket_name = self._router.route(statement)
            _bucket_map[bucket_name].append(statement)

        return result

    def process_text(self, text: str, source: str = "manual") -> CaptureResult:
        """Convenience method — process a raw string directly.

        Args:
            text: Raw input text.
            source: Origin label for the Capture object.

        Returns:
            A CaptureResult with statements distributed across buckets.
        """
        return self.process(Capture(raw_text=text, source=source))
