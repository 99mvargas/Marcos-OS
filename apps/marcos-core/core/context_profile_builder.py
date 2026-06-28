"""Builds typed context profiles for each Marcos OS domain executive.

The ContextProfileBuilder is the single point of contact between the knowledge
base and the executive team. Executives never call ContextEngine methods
directly — the builder fetches, filters, and pre-processes knowledge so that
each executive receives only what it needs in a typed, predictable form.

This separation means:
  - Repository access logic lives in one place.
  - Executives are testable without a real knowledge base.
  - Adding a new knowledge source requires changes only here, not in executives.
"""

from core.context_engine import ContextEngine
from models.context_profiles import (
    BusinessContext,
    FinanceContext,
    HealthContext,
    HomeContext,
    LearningContext,
    MarriageContext,
    PersonalContext,
    SmartHomeContext,
)
from models.knowledge_document import KnowledgeDocument


def _find(docs: list[KnowledgeDocument], filename: str) -> KnowledgeDocument | None:
    """Return the first document matching a filename, or None."""
    return next((d for d in docs if d.filename == filename), None)


class ContextProfileBuilder:
    """Constructs typed context profiles from the loaded knowledge base.

    Each build method fetches documents via the ContextEngine and returns
    a strongly-typed profile dataclass. No raw dicts are produced.

    Attributes:
        _engine: The ContextEngine instance providing document access.
    """

    def __init__(self, engine: ContextEngine) -> None:
        """Initialise the builder with a loaded ContextEngine.

        Args:
            engine: The ContextEngine loaded with the current knowledge base.
        """
        self._engine = engine

    # ------------------------------------------------------------------
    # Public profile builders — one per executive
    # ------------------------------------------------------------------

    def build_marriage_context(self) -> MarriageContext:
        """Build the context profile for the Marriage Executive.

        Locates Sara.md by searching the Relationships vault category and
        Household Operations.md by searching the Home vault category.
        Extracts love language text from Sara.md when present.

        Returns:
            A populated MarriageContext.
        """
        relationship_docs = self._engine.get_documents_by_category("Relationships")
        sara_doc = _find(relationship_docs, "Sara.md")

        love_language = ""
        if sara_doc is not None:
            if "acts of service" in sara_doc.content.lower():
                love_language = "Acts of Service"

        home_docs = self._engine.get_documents_by_category("Home")
        household_doc = _find(home_docs, "Household Operations.md")

        return MarriageContext(
            sara_doc=sara_doc,
            household_doc=household_doc,
            love_language=love_language,
        )

    def build_personal_context(self) -> PersonalContext:
        """Build the context profile for the Personal Executive.

        Returns:
            A populated PersonalContext.
        """
        identity_results = self._engine.search("Identity.md")
        identity_doc = _find(identity_results, "Identity.md")
        goals_documents = self._engine.get_documents_by_category("Goals")

        return PersonalContext(
            identity_doc=identity_doc,
            goals_documents=goals_documents,
        )

    def build_business_context(self) -> BusinessContext:
        """Build the context profile for the Business Executive.

        Returns:
            A populated BusinessContext.
        """
        return BusinessContext(
            business_documents=self._engine.get_documents_by_category("Business"),
        )

    def build_finance_context(self) -> FinanceContext:
        """Build the context profile for the Finance Executive.

        Returns:
            A populated FinanceContext.
        """
        return FinanceContext(
            finance_documents=self._engine.get_documents_by_category("Finances"),
        )

    def build_health_context(self) -> HealthContext:
        """Build the context profile for the Health Executive.

        Returns:
            A populated HealthContext.
        """
        return HealthContext(
            health_documents=self._engine.get_documents_by_category("Health"),
        )

    def build_home_context(self) -> HomeContext:
        """Build the context profile for the Home Executive.

        Returns:
            A populated HomeContext.
        """
        home_docs = self._engine.get_documents_by_category("Home")
        household_doc = _find(home_docs, "Household Operations.md")
        chai_doc = _find(home_docs, "Chai.md")
        remaining = [d for d in home_docs if d not in (household_doc, chai_doc)]

        return HomeContext(
            household_doc=household_doc,
            chai_doc=chai_doc,
            home_documents=remaining,
        )

    def build_learning_context(self) -> LearningContext:
        """Build the context profile for the Learning Executive.

        Returns:
            A populated LearningContext.
        """
        return LearningContext(
            learning_documents=self._engine.get_documents_by_category("Learning"),
        )

    def build_smart_home_context(self) -> SmartHomeContext:
        """Build the context profile for the Smart Home Executive.

        Returns:
            A populated SmartHomeContext.
        """
        return SmartHomeContext(
            tech_documents=self._engine.get_documents_by_category("AI & Technology"),
        )
