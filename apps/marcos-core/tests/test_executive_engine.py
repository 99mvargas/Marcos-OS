"""Unit tests for the ExecutiveEngine and MarriageExecutive."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.context_engine import ContextEngine
from core.executive_engine import ExecutiveEngine
from core.executives.marriage_executive import MarriageExecutive
from models.knowledge_document import KnowledgeDocument


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _make_doc(filename: str, category: str, content: str) -> KnowledgeDocument:
    return KnowledgeDocument(
        filename=filename,
        relative_path=f"{category}/{filename}",
        absolute_path=f"/fake/{category}/{filename}",
        category=category,
        content=content,
    )


SARA_CONTENT = """
# Relationship
Wife of Marcos Vargas.
# Love Language
Acts of Service.
# Appreciates
* Planned dates.
"""

HOUSEHOLD_CONTENT = """
# Mission
Create a clean, peaceful, organized home.
# Daily Operations
* Dishes
* Kitchen counters
"""


# ------------------------------------------------------------------
# ExecutiveEngine registration
# ------------------------------------------------------------------

def test_executive_engine_registers_all_executives() -> None:
    """ExecutiveEngine must register exactly 8 domain executives."""
    context = ContextEngine(documents=[])
    engine = ExecutiveEngine(context)

    expected_names = {
        "Personal Executive",
        "Marriage Executive",
        "Business Executive",
        "Finance Executive",
        "Health Executive",
        "Home Executive",
        "Learning Executive",
        "Smart Home Executive",
    }

    registered_names = {e.name for e in engine.executives}
    assert registered_names == expected_names, (
        f"Registered executives do not match expected.\n"
        f"Missing: {expected_names - registered_names}\n"
        f"Extra: {registered_names - expected_names}"
    )


def test_executive_engine_run_returns_list() -> None:
    """ExecutiveEngine.run() must return a list (empty is valid with no knowledge)."""
    context = ContextEngine(documents=[])
    engine = ExecutiveEngine(context)
    result = engine.run()
    assert isinstance(result, list)


# ------------------------------------------------------------------
# MarriageExecutive — no knowledge
# ------------------------------------------------------------------

def test_marriage_executive_no_documents_returns_empty() -> None:
    """No recommendations when no relationship knowledge exists."""
    executive = MarriageExecutive()
    result = executive.generate_recommendations({"documents": [], "search": lambda k: []})
    assert result == []


# ------------------------------------------------------------------
# MarriageExecutive — Sara document present
# ------------------------------------------------------------------

def test_marriage_executive_produces_recommendations_with_sara_doc() -> None:
    """Recommendations are produced when Sara.md is present."""
    sara = _make_doc("Sara.md", "Relationships", SARA_CONTENT)
    context = ContextEngine(documents=[sara])
    executive = MarriageExecutive()
    result = executive.generate_recommendations({
        "documents": [],
        "search": context.search,
    })
    assert len(result) >= 1


def test_marriage_executive_rule1_intentional_time() -> None:
    """Rule 1 produces 'Plan Intentional Time with Sara' when Sara.md exists."""
    sara = _make_doc("Sara.md", "Relationships", SARA_CONTENT)
    context = ContextEngine(documents=[sara])
    executive = MarriageExecutive()
    result = executive.generate_recommendations({
        "documents": [],
        "search": context.search,
    })
    titles = [r.title for r in result]
    assert "Plan Intentional Time with Sara" in titles


def test_marriage_executive_rule2_acts_of_service() -> None:
    """Rule 2 produces Acts of Service recommendation when love language is present."""
    sara = _make_doc("Sara.md", "Relationships", SARA_CONTENT)
    context = ContextEngine(documents=[sara])
    executive = MarriageExecutive()
    result = executive.generate_recommendations({
        "documents": [],
        "search": context.search,
    })
    titles = [r.title for r in result]
    assert "Look for a Way to Reduce Sara's Mental Load" in titles


def test_marriage_executive_rule2_absent_without_love_language() -> None:
    """Rule 2 is skipped when Acts of Service is not in the document."""
    sara = _make_doc("Sara.md", "Relationships", "# Relationship\nWife of Marcos.")
    context = ContextEngine(documents=[sara])
    executive = MarriageExecutive()
    result = executive.generate_recommendations({
        "documents": [],
        "search": context.search,
    })
    titles = [r.title for r in result]
    assert "Look for a Way to Reduce Sara's Mental Load" not in titles


def test_marriage_executive_rule3_household_task() -> None:
    """Rule 3 produces household task recommendation when Household Operations.md exists."""
    sara = _make_doc("Sara.md", "Relationships", SARA_CONTENT)
    household = _make_doc("Household Operations.md", "Home", HOUSEHOLD_CONTENT)
    context = ContextEngine(documents=[sara, household])
    executive = MarriageExecutive()
    result = executive.generate_recommendations({
        "documents": [],
        "search": context.search,
    })
    titles = [r.title for r in result]
    assert "Take Ownership of a Household Task" in titles


def test_marriage_executive_rule3_absent_without_household_doc() -> None:
    """Rule 3 is skipped when no Household Operations document exists."""
    sara = _make_doc("Sara.md", "Relationships", SARA_CONTENT)
    context = ContextEngine(documents=[sara])
    executive = MarriageExecutive()
    result = executive.generate_recommendations({
        "documents": [],
        "search": context.search,
    })
    titles = [r.title for r in result]
    assert "Take Ownership of a Household Task" not in titles


# ------------------------------------------------------------------
# Recommendation structure and sorting
# ------------------------------------------------------------------

def test_marriage_executive_recommendations_have_required_fields() -> None:
    """Every recommendation contains all required fields with valid values."""
    sara = _make_doc("Sara.md", "Relationships", SARA_CONTENT)
    context = ContextEngine(documents=[sara])
    executive = MarriageExecutive()
    result = executive.generate_recommendations({
        "documents": [],
        "search": context.search,
    })
    for rec in result:
        assert rec.title
        assert rec.description
        assert rec.category == "Marriage"
        assert isinstance(rec.priority, int)
        assert rec.reasoning
        assert rec.executive == "Marriage Executive"
        assert 0.0 <= rec.confidence <= 1.0


def test_marriage_executive_recommendations_sorted_by_priority() -> None:
    """Recommendations are returned in ascending priority order."""
    sara = _make_doc("Sara.md", "Relationships", SARA_CONTENT)
    household = _make_doc("Household Operations.md", "Home", HOUSEHOLD_CONTENT)
    context = ContextEngine(documents=[sara, household])
    executive = MarriageExecutive()
    result = executive.generate_recommendations({
        "documents": [],
        "search": context.search,
    })
    priorities = [r.priority for r in result]
    assert priorities == sorted(priorities)


def test_executive_engine_run_includes_marriage_recommendations() -> None:
    """Full ExecutiveEngine.run() surfaces Marriage Executive recommendations."""
    sara = _make_doc("Sara.md", "Relationships", SARA_CONTENT)
    household = _make_doc("Household Operations.md", "Home", HOUSEHOLD_CONTENT)
    context = ContextEngine(documents=[sara, household])
    engine = ExecutiveEngine(context)
    result = engine.run()
    marriage_recs = [r for r in result if r.category == "Marriage"]
    assert len(marriage_recs) >= 1


# ------------------------------------------------------------------
# Runner
# ------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_executive_engine_registers_all_executives,
        test_executive_engine_run_returns_list,
        test_marriage_executive_no_documents_returns_empty,
        test_marriage_executive_produces_recommendations_with_sara_doc,
        test_marriage_executive_rule1_intentional_time,
        test_marriage_executive_rule2_acts_of_service,
        test_marriage_executive_rule2_absent_without_love_language,
        test_marriage_executive_rule3_household_task,
        test_marriage_executive_rule3_absent_without_household_doc,
        test_marriage_executive_recommendations_have_required_fields,
        test_marriage_executive_recommendations_sorted_by_priority,
        test_executive_engine_run_includes_marriage_recommendations,
    ]
    for test in tests:
        test()
        print(f"  PASS  {test.__name__}")
    print(f"\nAll {len(tests)} tests passed.")
