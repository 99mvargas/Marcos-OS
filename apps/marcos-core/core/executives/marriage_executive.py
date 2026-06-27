"""Executive responsible for supporting Marcos's marriage with Sara."""

from core.executives.base_executive import BaseExecutive
from models.context_profiles import MarriageContext
from models.recommendation import Recommendation

# Priority constants aligned with the Memory Layer priority model.
# Family = 2, which maps to "high priority" recommendations in this domain.
_PRIORITY_HIGH = 2
_PRIORITY_MEDIUM = 4

_EXECUTIVE_NAME = "Marriage Executive"


class MarriageExecutive(BaseExecutive):
    """Helps Marcos grow as a husband and support Sara's wellbeing.

    Version 1 is rule-based. Rules are derived exclusively from the
    MarriageContext profile prepared by ContextProfileBuilder. The executive
    does not access the repository directly.

    When AI reasoning is connected in a future sprint, rules will be
    augmented or replaced by LLM analysis over the same context profile.

    Current rules (v1):
        Rule 1 — sara_doc present: recommend intentional relationship investment.
        Rule 2 — love_language is Acts of Service: recommend reducing Sara's mental load.
        Rule 3 — household_doc present: recommend taking ownership of a household task.
        Rule 4 — sara_doc absent: return no recommendations.

    Future responsibilities:
        - Detect unplanned date gaps from the memory layer.
        - Surface commitments to Sara that are overdue.
        - Encourage Marcos to lead spiritually as the family grows.
        - Protect dedicated family time from work displacement.
    """

    @property
    def name(self) -> str:
        return _EXECUTIVE_NAME

    @property
    def domain(self) -> str:
        return "Marriage"

    def generate_recommendations(self, context: MarriageContext) -> list[Recommendation]:
        """Generate rule-based marriage and relationship recommendations.

        Consumes a MarriageContext profile. Does not perform any repository
        searching — all data pre-fetching is handled by ContextProfileBuilder.

        Args:
            context: A MarriageContext profile containing sara_doc,
                household_doc, and love_language.

        Returns:
            Priority-sorted list of Recommendation objects. Empty if
            sara_doc is absent.
        """
        # Rule 4 — no relationship knowledge found.
        if context.sara_doc is None:
            return []

        recommendations: list[Recommendation] = []

        # Rule 1 — Sara document exists.
        recommendations.append(
            Recommendation(
                title="Plan Intentional Time with Sara",
                description=(
                    "Schedule a planned date or meaningful activity with Sara. "
                    "Sara values thoughtful effort and intentional planning "
                    "over expensive gifts or spontaneous gestures."
                ),
                category="Marriage",
                priority=_PRIORITY_HIGH,
                reasoning=(
                    "Sara values thoughtful effort, planned dates, and quality "
                    "time more than expensive gifts."
                ),
                executive=_EXECUTIVE_NAME,
                confidence=0.95,
            )
        )

        # Rule 2 — Sara's love language is Acts of Service.
        if context.love_language.lower() == "acts of service":
            recommendations.append(
                Recommendation(
                    title="Look for a Way to Reduce Sara's Mental Load",
                    description=(
                        "Identify one thing Sara is carrying today — a task, "
                        "a worry, or a responsibility — and take it off her plate "
                        "without being asked."
                    ),
                    category="Marriage",
                    priority=_PRIORITY_HIGH,
                    reasoning=(
                        "Acts of Service is Sara's primary love language. "
                        "Reducing her mental load is a direct expression of love."
                    ),
                    executive=_EXECUTIVE_NAME,
                    confidence=0.95,
                )
            )

        # Rule 3 — Household Operations document exists.
        if context.household_doc is not None:
            recommendations.append(
                Recommendation(
                    title="Take Ownership of a Household Task",
                    description=(
                        "Choose one household task from the weekly or daily operations "
                        "list and complete it proactively, before Sara has to ask."
                    ),
                    category="Marriage",
                    priority=_PRIORITY_MEDIUM,
                    reasoning=(
                        "Reducing household mental load strengthens the marriage. "
                        "Organization directly impacts Sara's stress level."
                    ),
                    executive=_EXECUTIVE_NAME,
                    confidence=0.9,
                )
            )

        return sorted(recommendations, key=lambda r: r.priority)
