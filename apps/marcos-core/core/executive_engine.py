"""Orchestrates all Marcos OS domain executives and aggregates recommendations."""

from core.context_engine import ContextEngine
from core.context_profile_builder import ContextProfileBuilder
from core.executives.base_executive import BaseExecutive
from core.executives.business_executive import BusinessExecutive
from core.executives.finance_executive import FinanceExecutive
from core.executives.health_executive import HealthExecutive
from core.executives.home_executive import HomeExecutive
from core.executives.learning_executive import LearningExecutive
from core.executives.marriage_executive import MarriageExecutive
from core.executives.personal_executive import PersonalExecutive
from core.executives.smart_home_executive import SmartHomeExecutive
from models.recommendation import Recommendation


class ExecutiveEngine:
    """Registers, runs, and aggregates all domain executives.

    The ExecutiveEngine coordinates the ContextProfileBuilder and the
    executive team. It builds a typed context profile for each executive
    and collects the resulting recommendations into a single prioritised list.

    Executives never access the ContextEngine directly. All knowledge
    pre-processing is handled by the ContextProfileBuilder before
    recommendations are requested.

    Attributes:
        _context: The ContextEngine providing access to the knowledge base.
        _builder: The ContextProfileBuilder that constructs typed profiles.
        _executives: Ordered list of registered BaseExecutive instances.
    """

    def __init__(self, context: ContextEngine) -> None:
        """Initialise the ExecutiveEngine and register all domain executives.

        Args:
            context: The ContextEngine loaded with the current knowledge base.
        """
        self._context = context
        self._builder = ContextProfileBuilder(context)
        self._executives: list[BaseExecutive] = self._register_executives()

    def _register_executives(self) -> list[BaseExecutive]:
        """Instantiate and return all domain executives in priority order.

        Returns:
            Ordered list of BaseExecutive instances.
        """
        return [
            PersonalExecutive(),
            MarriageExecutive(),
            BusinessExecutive(),
            FinanceExecutive(),
            HealthExecutive(),
            HomeExecutive(),
            LearningExecutive(),
            SmartHomeExecutive(),
        ]

    @property
    def executives(self) -> list[BaseExecutive]:
        """Return the list of registered executives."""
        return self._executives

    def _build_context(self, executive: BaseExecutive):
        """Build the typed context profile for a given executive.

        Dispatches to the correct ContextProfileBuilder method based on the
        executive type. Adding a new executive requires a corresponding entry
        here and a new builder method in ContextProfileBuilder.

        Args:
            executive: The executive instance requiring a context profile.

        Returns:
            A typed context profile dataclass for the executive.
        """
        if isinstance(executive, PersonalExecutive):
            return self._builder.build_personal_context()
        if isinstance(executive, MarriageExecutive):
            return self._builder.build_marriage_context()
        if isinstance(executive, BusinessExecutive):
            return self._builder.build_business_context()
        if isinstance(executive, FinanceExecutive):
            return self._builder.build_finance_context()
        if isinstance(executive, HealthExecutive):
            return self._builder.build_health_context()
        if isinstance(executive, HomeExecutive):
            return self._builder.build_home_context()
        if isinstance(executive, LearningExecutive):
            return self._builder.build_learning_context()
        if isinstance(executive, SmartHomeExecutive):
            return self._builder.build_smart_home_context()
        raise NotImplementedError(
            f"No context profile builder registered for {type(executive).__name__}."
        )

    def run(self) -> list[Recommendation]:
        """Execute every executive and return a combined, prioritised recommendation list.

        Builds a typed context profile for each executive, invokes it, and
        merges all recommendations. The final list is sorted by priority
        ascending (1 = highest priority).

        Returns:
            A sorted list of all Recommendation objects produced this cycle.
        """
        all_recommendations: list[Recommendation] = []

        for executive in self._executives:
            profile = self._build_context(executive)
            recommendations = executive.generate_recommendations(profile)
            all_recommendations.extend(recommendations)

        return sorted(all_recommendations, key=lambda r: r.priority)
