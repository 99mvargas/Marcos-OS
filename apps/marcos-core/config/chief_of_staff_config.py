"""Configuration profiles for the Chief of Staff Engine.

Each profile controls how the engine selects and limits recommendations
for a given run mode. Adding a new mode requires only a new instance of
ChiefOfStaffConfig — no changes to the engine or downstream consumers.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ChiefOfStaffConfig:
    """Configuration profile for one Chief of Staff Engine run mode.

    Attributes:
        max_recommendations: Maximum recommendations to include in the
            curated Morning Brief output. Recommendations beyond this
            cap are deferred rather than discarded.
        mode: Human-readable label identifying this profile.
    """

    max_recommendations: int
    mode: str


DEFAULT_CONFIG = ChiefOfStaffConfig(max_recommendations=5, mode="default")
WORKDAY_CONFIG = ChiefOfStaffConfig(max_recommendations=5, mode="workday")
WEEKEND_CONFIG = ChiefOfStaffConfig(max_recommendations=3, mode="weekend")
VACATION_CONFIG = ChiefOfStaffConfig(max_recommendations=2, mode="vacation")
