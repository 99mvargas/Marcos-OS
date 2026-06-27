"""Executive responsible for personal productivity, habits, and time."""

from core.executives.base_executive import BaseExecutive
from models.context_profiles import PersonalContext
from models.recommendation import Recommendation


class PersonalExecutive(BaseExecutive):
    """Manages Marcos's personal effectiveness across productivity, habits, and time.

    Future responsibilities:
        - Detect patterns of procrastination or inconsistent follow-through.
        - Surface high-ROI tasks that align with Marcos's identity and goals.
        - Recommend habit adjustments based on observed behaviour trends.
        - Protect time for high-priority commitments.
        - Flag time wasted on low-value activities.
    """

    @property
    def name(self) -> str:
        return "Personal Executive"

    @property
    def domain(self) -> str:
        return "Personal"

    def generate_recommendations(self, context: PersonalContext) -> list[Recommendation]:
        """Generate personal productivity and habit recommendations.

        TODO: Implement LLM reasoning over Identity and Goals knowledge objects.
        TODO: Detect procrastination patterns from memory layer.
        TODO: Recommend daily priorities aligned with Decision Framework.
        """
        return []
