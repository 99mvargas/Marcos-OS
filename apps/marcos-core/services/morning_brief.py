"""Service responsible for generating and rendering the Marcos OS Morning Brief."""

from datetime import datetime

from core.context_engine import ContextEngine
from core.executive_engine import ExecutiveEngine
from models.morning_brief import MorningBrief
from models.recommendation import Recommendation

_DIVIDER = "=" * 36


def render_brief(brief: MorningBrief, knowledge_documents: int, executives_run: int) -> None:
    """Render a MorningBrief to the console without requiring a service instance.

    Standalone function for use by callers that already hold the relevant
    counts (e.g. DailyExecutiveCycle), avoiding the need to reconstruct a
    ContextEngine or ExecutiveEngine purely for display.

    Args:
        brief: The MorningBrief to render.
        knowledge_documents: Number of knowledge documents loaded this cycle.
        executives_run: Number of executives that ran this cycle.
    """
    print(_DIVIDER)
    print("MARCOS OS")
    print("Morning Brief")
    print(_DIVIDER)
    print(f"Knowledge Documents: {knowledge_documents}")
    print(f"Executives: {executives_run}")
    print(f"Recommendations: {brief.total_recommendations}")
    print()

    if brief.total_recommendations == 0:
        print("No recommendations available.")
        print()
        print("Have a productive day.")
    else:
        for rec in brief.recommendations:
            print(_DIVIDER)
            print(f"[Priority {rec.priority}]")
            print(f"Title:      {rec.title}")
            print(f"Description:{rec.description}")
            print(f"Reasoning:  {rec.reasoning}")
            print(f"Executive:  {rec.executive}")

    print(_DIVIDER)


class MorningBriefService:
    """Orchestrates a full executive cycle and produces a Morning Brief.

    The MorningBriefService is the top-level entry point for generating
    Marcos's daily output. It coordinates the ExecutiveEngine, collects
    all Recommendation objects, builds a MorningBrief, and renders a
    human-readable console summary.

    Future evolution:
        - Send brief via Telegram integration.
        - Persist brief to PostgreSQL for historical tracking.
        - Enrich recommendations with LLM reasoning via OpenRouter.
        - Push to Dashboard when frontend is available.
        - Incorporate Home Assistant state into context.

    Attributes:
        _context: The loaded ContextEngine.
        _executive_engine: The ExecutiveEngine instance to run.
    """

    def __init__(self, context: ContextEngine, executive_engine: ExecutiveEngine) -> None:
        """Initialise the MorningBriefService.

        Args:
            context: The ContextEngine loaded with the current knowledge base.
            executive_engine: The ExecutiveEngine with all executives registered.
        """
        self._context = context
        self._executive_engine = executive_engine

    def generate(self) -> MorningBrief:
        """Run the executive team and produce a MorningBrief.

        Executes all executives via the ExecutiveEngine, collects the
        resulting recommendations, and constructs a MorningBrief with
        a human-readable summary.

        Returns:
            A fully populated MorningBrief object.
        """
        recommendations: list[Recommendation] = self._executive_engine.run()
        total = len(recommendations)

        if total == 0:
            summary = "No recommendations available.\n\nHave a productive day."
        else:
            summary = f"{total} recommendation{'s' if total != 1 else ''} generated."

        return MorningBrief(
            generated_at=datetime.utcnow(),
            recommendations=recommendations,
            summary=summary,
            total_recommendations=total,
        )

    def print_brief(self, brief: MorningBrief) -> None:
        """Render a MorningBrief to the console in human-readable format.

        Delegates to the standalone render_brief() function using counts
        derived from this service's context and executive engine.

        Args:
            brief: The MorningBrief to render.
        """
        render_brief(
            brief=brief,
            knowledge_documents=self._context.summary()["total_documents"],
            executives_run=len(self._executive_engine.executives),
        )
