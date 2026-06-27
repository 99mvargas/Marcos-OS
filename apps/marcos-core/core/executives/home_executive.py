"""Executive responsible for household operations and Chai's care."""

from core.executives.base_executive import BaseExecutive
from models.context_profiles import HomeContext
from models.recommendation import Recommendation


class HomeExecutive(BaseExecutive):
    """Manages household maintenance, cleaning operations, and Chai's care.

    Future responsibilities:
        - Surface overdue cleaning and household tasks.
        - Adapt cleaning schedules when tasks are missed.
        - Recommend highest-impact household action rather than overwhelming lists.
        - Track Chai's care responsibilities (vet visits, grooming, training progress).
        - Reduce Sara's mental load by prompting Marcos proactively.
        - Identify recurring household bottlenecks and recommend system improvements.
    """

    @property
    def name(self) -> str:
        return "Home Executive"

    @property
    def domain(self) -> str:
        return "Home"

    def generate_recommendations(self, context: HomeContext) -> list[Recommendation]:
        """Generate household maintenance and pet care recommendations.

        TODO: Implement LLM reasoning over Household Operations.md and Chai.md.
        TODO: Detect overdue tasks from memory layer.
        TODO: Adapt schedule when tasks are postponed.
        TODO: Surface Chai care reminders based on last-logged dates.
        """
        return []
