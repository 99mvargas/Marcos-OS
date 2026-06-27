"""Data model for a raw capture entering the Marcos OS intake pipeline."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Capture:
    """A single raw capture submitted to the Capture Pipeline.

    A Capture represents unprocessed input from any source — a typed note,
    voice transcript, Telegram message, email snippet, or automation event.
    The pipeline splits, classifies, and routes the raw_text into structured
    output. The original text is always preserved.

    Attributes:
        raw_text: The unmodified input text as provided by the source.
        captured_at: UTC timestamp when the capture was received.
        source: Origin of the capture — 'manual', 'telegram', 'voice',
            'email', 'home_assistant', 'n8n'.
    """

    raw_text: str
    captured_at: datetime = field(default_factory=datetime.utcnow)
    source: str = "manual"
