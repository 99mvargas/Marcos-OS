"""Routes individual statements to their appropriate capture bucket.

The CaptureRouter applies an ordered list of rule handlers to each statement.
The first handler that matches wins — no statement is classified twice.

Extending the router:
    Add a new handler function with the signature:
        def handle_<name>(statement: str) -> str | None
    returning the bucket name if matched, or None to pass to the next handler.
    Register it in CaptureRouter._handlers in the desired priority order.

Future evolution:
    - AI classification handler inserted at the end of the chain to capture
      what rules miss, reducing the volume of unknown_items.
    - Confidence scoring per handler to support ambiguous classification.
    - Handler registry loaded from configuration to allow runtime extension.
"""

from typing import Callable

# Bucket names — must match CaptureResult field names.
BUCKET_COMMITMENT = "commitments"
BUCKET_OBSERVATION = "observations"
BUCKET_RELATIONSHIP = "relationship_items"
BUCKET_QUESTION = "questions"
BUCKET_UNKNOWN = "unknown_items"

# ---------------------------------------------------------------------------
# Rule handlers
# Each returns a bucket name string if the statement matches, else None.
# ---------------------------------------------------------------------------

# Prefixes are lowercase for case-insensitive matching.
_COMMITMENT_PREFIXES: tuple[str, ...] = (
    "i need to",
    "i need ",
    "remember to",
    "i will",
    "i have to",
    "i must",
    "don't forget to",
    "don't forget ",
    "make sure to",
    "make sure ",
    "schedule ",
    "book ",
    "buy ",
    "pick up ",
    "follow up",
    "call ",
    "text ",
    "email ",
    "pay ",
    "fix ",
    "order ",
)

_RELATIONSHIP_PREFIXES: tuple[str, ...] = (
    "sara said",
    "sara wants",
    "sara likes",
    "sara needs",
    "sara asked",
    "sara mentioned",
    "sara feels",
    "sara is",
    "sara was",
    "sara loves",
    "sara doesn't",
    "sara does",
    "sara has",
)

_OBSERVATION_PREFIXES: tuple[str, ...] = (
    "i noticed",
    "i notice",
    "i observed",
    "i realized",
    "i realised",
    "i think",
    "i feel like",
    "it seems",
    "it looks like",
    "the living room",
    "the kitchen",
    "the bedroom",
    "the bathroom",
    "the garage",
    "the yard",
    "the office",
    "chai ",
    "the dog",
    "at work",
    "on the job",
    "today i",
    "this morning",
    "this evening",
    "this week",
    "lately ",
    "recently ",
)


def _handle_commitment(statement: str) -> str | None:
    """Match commitment-signalling prefixes."""
    lower = statement.lower()
    if any(lower.startswith(p) for p in _COMMITMENT_PREFIXES):
        return BUCKET_COMMITMENT
    return None


def _handle_relationship(statement: str) -> str | None:
    """Match statements about Sara or named relationships."""
    lower = statement.lower()
    if any(lower.startswith(p) for p in _RELATIONSHIP_PREFIXES):
        return BUCKET_RELATIONSHIP
    return None


def _handle_observation(statement: str) -> str | None:
    """Match observation or noticed-pattern statements."""
    lower = statement.lower()
    if any(lower.startswith(p) for p in _OBSERVATION_PREFIXES):
        return BUCKET_OBSERVATION
    return None


def _handle_question(statement: str) -> str | None:
    """Match statements phrased as questions."""
    if statement.strip().endswith("?"):
        return BUCKET_QUESTION
    return None


class CaptureRouter:
    """Routes a single statement to its capture bucket using ordered handlers.

    Handlers are evaluated in registration order. The first match wins.
    Unmatched statements fall through to the unknown bucket.

    Adding a handler:
        Pass additional callables to the constructor, or subclass and
        override _default_handlers. Each callable receives the raw
        statement string and returns a bucket name or None.

    Attributes:
        _handlers: Ordered list of (handler_fn, bucket_name) pairs.
            bucket_name is the fallback if the handler returns a string
            directly; handlers may also return the bucket name themselves.
    """

    Handler = Callable[[str], str | None]

    def __init__(self, extra_handlers: list[Handler] | None = None) -> None:
        """Initialise the router with the default handler chain.

        Args:
            extra_handlers: Optional additional handlers appended before the
                unknown fallback. Useful for extending without subclassing.
        """
        self._handlers: list[CaptureRouter.Handler] = [
            _handle_commitment,
            _handle_relationship,
            _handle_observation,
            _handle_question,
        ]
        if extra_handlers:
            self._handlers.extend(extra_handlers)

    def route(self, statement: str) -> str:
        """Classify a single statement and return its bucket name.

        Evaluates each handler in order. Returns the bucket name from the
        first handler that matches. Unmatched statements return BUCKET_UNKNOWN.

        Args:
            statement: A single logical statement to classify.

        Returns:
            One of the BUCKET_* constants defined in this module.
        """
        cleaned = statement.strip()
        if not cleaned:
            return BUCKET_UNKNOWN

        for handler in self._handlers:
            result = handler(cleaned)
            if result is not None:
                return result

        return BUCKET_UNKNOWN
