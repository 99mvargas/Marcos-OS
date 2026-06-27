"""Tests for ContextProfileBuilder and typed context profiles."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.context_engine import ContextEngine
from core.context_profile_builder import ContextProfileBuilder
from core.executive_engine import ExecutiveEngine
from core.executives.marriage_executive import MarriageExecutive
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


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _doc(filename: str, category: str, content: str = "") -> KnowledgeDocument:
    return KnowledgeDocument(
        filename=filename,
        relative_path=f"{category}/{filename}",
        absolute_path=f"/fake/{category}/{filename}",
        category=category,
        content=content,
    )


SARA_CONTENT = "# Love Language\nActs of Service.\n# Appreciates\n* Planned dates."
HOUSEHOLD_CONTENT = "# Mission\nClean home.\n# Daily Operations\n* Dishes"


# ------------------------------------------------------------------
# Context profile types
# ------------------------------------------------------------------

def test_marriage_context_is_typed() -> None:
    """MarriageContext is a dataclass with expected fields."""
    ctx = MarriageContext()
    assert ctx.sara_doc is None
    assert ctx.household_doc is None
    assert ctx.love_language == ""


def test_personal_context_defaults() -> None:
    ctx = PersonalContext()
    assert ctx.identity_doc is None
    assert ctx.goals_documents == []


def test_business_context_defaults() -> None:
    assert BusinessContext().business_documents == []


def test_finance_context_defaults() -> None:
    assert FinanceContext().finance_documents == []


def test_health_context_defaults() -> None:
    assert HealthContext().health_documents == []


def test_home_context_defaults() -> None:
    ctx = HomeContext()
    assert ctx.household_doc is None
    assert ctx.chai_doc is None
    assert ctx.home_documents == []


def test_learning_context_defaults() -> None:
    assert LearningContext().learning_documents == []


def test_smart_home_context_defaults() -> None:
    assert SmartHomeContext().tech_documents == []


# ------------------------------------------------------------------
# ContextProfileBuilder — MarriageContext
# ------------------------------------------------------------------

def test_builder_marriage_context_empty_knowledge() -> None:
    """MarriageContext fields are None when no documents are loaded."""
    builder = ContextProfileBuilder(ContextEngine(documents=[]))
    ctx = builder.build_marriage_context()
    assert ctx.sara_doc is None
    assert ctx.household_doc is None
    assert ctx.love_language == ""


def test_builder_marriage_context_with_sara_doc() -> None:
    """MarriageContext.sara_doc is populated when Sara.md is present."""
    sara = _doc("Sara.md", "Relationships", SARA_CONTENT)
    builder = ContextProfileBuilder(ContextEngine(documents=[sara]))
    ctx = builder.build_marriage_context()
    assert ctx.sara_doc is not None
    assert ctx.sara_doc.filename == "Sara.md"


def test_builder_marriage_context_love_language_extracted() -> None:
    """love_language is 'Acts of Service' when present in Sara.md."""
    sara = _doc("Sara.md", "Relationships", SARA_CONTENT)
    builder = ContextProfileBuilder(ContextEngine(documents=[sara]))
    ctx = builder.build_marriage_context()
    assert ctx.love_language == "Acts of Service"


def test_builder_marriage_context_love_language_absent() -> None:
    """love_language is empty when Acts of Service is not in Sara.md."""
    sara = _doc("Sara.md", "Relationships", "# Relationship\nWife of Marcos.")
    builder = ContextProfileBuilder(ContextEngine(documents=[sara]))
    ctx = builder.build_marriage_context()
    assert ctx.love_language == ""


def test_builder_marriage_context_with_household_doc() -> None:
    """MarriageContext.household_doc is populated when Household Operations.md exists."""
    sara = _doc("Sara.md", "Relationships", SARA_CONTENT)
    household = _doc("Household Operations.md", "Home", HOUSEHOLD_CONTENT)
    builder = ContextProfileBuilder(ContextEngine(documents=[sara, household]))
    ctx = builder.build_marriage_context()
    assert ctx.household_doc is not None
    assert ctx.household_doc.filename == "Household Operations.md"


# ------------------------------------------------------------------
# ContextProfileBuilder — other profiles
# ------------------------------------------------------------------

def test_builder_personal_context_identity_doc() -> None:
    """PersonalContext.identity_doc is populated when Identity.md exists."""
    identity = _doc("Identity.md", "Identity", "# Identity\nMarcos Vargas.")
    builder = ContextProfileBuilder(ContextEngine(documents=[identity]))
    ctx = builder.build_personal_context()
    assert ctx.identity_doc is not None


def test_builder_personal_context_goals() -> None:
    """PersonalContext.goals_documents contains Goals category documents."""
    goal = _doc("Goals.md", "Goals", "# Goals")
    builder = ContextProfileBuilder(ContextEngine(documents=[goal]))
    ctx = builder.build_personal_context()
    assert len(ctx.goals_documents) == 1


def test_builder_home_context_splits_docs() -> None:
    """HomeContext separates household_doc and chai_doc from remaining home docs."""
    household = _doc("Household Operations.md", "Home", HOUSEHOLD_CONTENT)
    chai = _doc("Chai.md", "Home", "# Identity\nName: Chai")
    other = _doc("Other.md", "Home", "# Other")
    builder = ContextProfileBuilder(ContextEngine(documents=[household, chai, other]))
    ctx = builder.build_home_context()
    assert ctx.household_doc is not None
    assert ctx.chai_doc is not None
    assert len(ctx.home_documents) == 1
    assert ctx.home_documents[0].filename == "Other.md"


def test_builder_smart_home_uses_ai_technology_category() -> None:
    """SmartHomeContext.tech_documents draws from 'AI & Technology' category."""
    tech = _doc("HomeAssistant.md", "AI & Technology", "# Home Assistant")
    builder = ContextProfileBuilder(ContextEngine(documents=[tech]))
    ctx = builder.build_smart_home_context()
    assert len(ctx.tech_documents) == 1


# ------------------------------------------------------------------
# MarriageExecutive consumes MarriageContext (not dict)
# ------------------------------------------------------------------

def test_marriage_executive_consumes_profile_no_sara() -> None:
    """MarriageExecutive returns empty list when sara_doc is None."""
    executive = MarriageExecutive()
    result = executive.generate_recommendations(MarriageContext())
    assert result == []


def test_marriage_executive_rule1_via_profile() -> None:
    """Rule 1 fires when sara_doc is present in MarriageContext."""
    sara = _doc("Sara.md", "Relationships", SARA_CONTENT)
    ctx = MarriageContext(sara_doc=sara, love_language="Acts of Service")
    executive = MarriageExecutive()
    titles = [r.title for r in executive.generate_recommendations(ctx)]
    assert "Plan Intentional Time with Sara" in titles


def test_marriage_executive_rule2_via_profile() -> None:
    """Rule 2 fires when love_language is 'Acts of Service' in profile."""
    sara = _doc("Sara.md", "Relationships", SARA_CONTENT)
    ctx = MarriageContext(sara_doc=sara, love_language="Acts of Service")
    executive = MarriageExecutive()
    titles = [r.title for r in executive.generate_recommendations(ctx)]
    assert "Look for a Way to Reduce Sara's Mental Load" in titles


def test_marriage_executive_rule2_skipped_wrong_love_language() -> None:
    """Rule 2 is skipped when love_language does not match."""
    sara = _doc("Sara.md", "Relationships", "# Relationship\nWife.")
    ctx = MarriageContext(sara_doc=sara, love_language="Words of Affirmation")
    executive = MarriageExecutive()
    titles = [r.title for r in executive.generate_recommendations(ctx)]
    assert "Look for a Way to Reduce Sara's Mental Load" not in titles


def test_marriage_executive_rule3_via_profile() -> None:
    """Rule 3 fires when household_doc is present in MarriageContext."""
    sara = _doc("Sara.md", "Relationships", SARA_CONTENT)
    household = _doc("Household Operations.md", "Home", HOUSEHOLD_CONTENT)
    ctx = MarriageContext(sara_doc=sara, household_doc=household, love_language="Acts of Service")
    executive = MarriageExecutive()
    titles = [r.title for r in executive.generate_recommendations(ctx)]
    assert "Take Ownership of a Household Task" in titles


# ------------------------------------------------------------------
# ExecutiveEngine injects typed profile
# ------------------------------------------------------------------

def test_executive_engine_marriage_recommendations_via_profile() -> None:
    """Full engine run delivers typed profile to MarriageExecutive."""
    sara = _doc("Sara.md", "Relationships", SARA_CONTENT)
    household = _doc("Household Operations.md", "Home", HOUSEHOLD_CONTENT)
    context = ContextEngine(documents=[sara, household])
    engine = ExecutiveEngine(context)
    result = engine.run()
    marriage_recs = [r for r in result if r.category == "Marriage"]
    assert len(marriage_recs) == 3


def test_executive_engine_run_sorted_by_priority() -> None:
    """Recommendations from the full engine run are sorted by priority ascending."""
    sara = _doc("Sara.md", "Relationships", SARA_CONTENT)
    household = _doc("Household Operations.md", "Home", HOUSEHOLD_CONTENT)
    context = ContextEngine(documents=[sara, household])
    engine = ExecutiveEngine(context)
    result = engine.run()
    priorities = [r.priority for r in result]
    assert priorities == sorted(priorities)


# ------------------------------------------------------------------
# Runner
# ------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_marriage_context_is_typed,
        test_personal_context_defaults,
        test_business_context_defaults,
        test_finance_context_defaults,
        test_health_context_defaults,
        test_home_context_defaults,
        test_learning_context_defaults,
        test_smart_home_context_defaults,
        test_builder_marriage_context_empty_knowledge,
        test_builder_marriage_context_with_sara_doc,
        test_builder_marriage_context_love_language_extracted,
        test_builder_marriage_context_love_language_absent,
        test_builder_marriage_context_with_household_doc,
        test_builder_personal_context_identity_doc,
        test_builder_personal_context_goals,
        test_builder_home_context_splits_docs,
        test_builder_smart_home_uses_ai_technology_category,
        test_marriage_executive_consumes_profile_no_sara,
        test_marriage_executive_rule1_via_profile,
        test_marriage_executive_rule2_via_profile,
        test_marriage_executive_rule2_skipped_wrong_love_language,
        test_marriage_executive_rule3_via_profile,
        test_executive_engine_marriage_recommendations_via_profile,
        test_executive_engine_run_sorted_by_priority,
    ]
    for test in tests:
        test()
        print(f"  PASS  {test.__name__}")
    print(f"\nAll {len(tests)} tests passed.")
