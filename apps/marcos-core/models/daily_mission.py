"""Data model for the Marcos OS Daily Mission.

The DailyMission is the long-term architectural endpoint of the Marcos OS
intelligence layer: rather than delivering a list of recommendations, the
system will eventually deliver a single, synthesised mission for the day
supported by those recommendations.

In v1 the mission is derived deterministically from the highest-priority
recommendation selected by the Chief of Staff Engine. Future AI integration
will replace this with cross-domain reasoning over the full recommendation set.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DailyMission:
    """The primary mission for Marcos's day.

    Designed so that rule-derived values today and AI-derived values in a
    future sprint populate the same fields. Downstream consumers (Morning
    Brief renderer, Telegram, Dashboard) do not need to change when the
    derivation method changes.

    Attributes:
        statement: One-sentence description of the day's primary focus.
        domain: The life domain this mission belongs to.
        source_executive: Name of the executive whose recommendation
            drove this mission.
        generated_at: UTC timestamp when this mission was derived.
        confidence: Confidence score between 0.0 and 1.0.
            Rule-derived missions inherit the confidence of the source
            recommendation. AI-derived missions will reflect model confidence.
        reasoning: Explanation of why this is the day's top priority.
            Rule-derived: propagated from the source recommendation.
            AI-derived: LLM-generated synthesis.
    """

    statement: str = ""
    domain: str = ""
    source_executive: str = ""
    generated_at: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 0.0
    reasoning: str = ""
