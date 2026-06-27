"""Typed context profiles delivered to each Marcos OS domain executive.

Each profile contains only the knowledge relevant to one executive's domain.
Executives consume profiles rather than searching the repository directly,
keeping repository access logic centralised in the ContextProfileBuilder.
"""

from dataclasses import dataclass, field
from typing import Optional

from models.knowledge_document import KnowledgeDocument


@dataclass
class MarriageContext:
    """Context delivered to the Marriage Executive.

    Attributes:
        sara_doc: The Sara.md knowledge document, if present.
        household_doc: The Household Operations.md document, if present.
        love_language: Sara's love language extracted from her document.
            Empty string when Sara.md is absent.
    """

    sara_doc: Optional[KnowledgeDocument] = None
    household_doc: Optional[KnowledgeDocument] = None
    love_language: str = ""


@dataclass
class PersonalContext:
    """Context delivered to the Personal Executive.

    Attributes:
        identity_doc: The Identity.md knowledge document, if present.
        goals_documents: All documents from the Goals vault category.
    """

    identity_doc: Optional[KnowledgeDocument] = None
    goals_documents: list[KnowledgeDocument] = field(default_factory=list)


@dataclass
class BusinessContext:
    """Context delivered to the Business Executive.

    Attributes:
        business_documents: All documents from the Business vault category.
    """

    business_documents: list[KnowledgeDocument] = field(default_factory=list)


@dataclass
class FinanceContext:
    """Context delivered to the Finance Executive.

    Attributes:
        finance_documents: All documents from the Finances vault category.
    """

    finance_documents: list[KnowledgeDocument] = field(default_factory=list)


@dataclass
class HealthContext:
    """Context delivered to the Health Executive.

    Attributes:
        health_documents: All documents from the Health vault category.
    """

    health_documents: list[KnowledgeDocument] = field(default_factory=list)


@dataclass
class HomeContext:
    """Context delivered to the Home Executive.

    Attributes:
        household_doc: The Household Operations.md document, if present.
        chai_doc: The Chai.md document, if present.
        home_documents: All remaining documents from the Home vault category.
    """

    household_doc: Optional[KnowledgeDocument] = None
    chai_doc: Optional[KnowledgeDocument] = None
    home_documents: list[KnowledgeDocument] = field(default_factory=list)


@dataclass
class LearningContext:
    """Context delivered to the Learning Executive.

    Attributes:
        learning_documents: All documents from the Learning vault category.
    """

    learning_documents: list[KnowledgeDocument] = field(default_factory=list)


@dataclass
class SmartHomeContext:
    """Context delivered to the Smart Home Executive.

    Attributes:
        tech_documents: All documents from the 'AI & Technology' vault category.
    """

    tech_documents: list[KnowledgeDocument] = field(default_factory=list)
