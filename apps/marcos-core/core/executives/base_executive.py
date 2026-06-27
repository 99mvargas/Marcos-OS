"""Abstract base class for all Marcos OS domain executives."""

from abc import ABC, abstractmethod
from typing import Any

from models.recommendation import Recommendation


class BaseExecutive(ABC):
    """Defines the contract every domain executive must fulfill.

    Each executive is responsible for a specific life domain. When invoked,
    it receives a typed context profile prepared by the ContextProfileBuilder
    and returns a list of prioritised recommendations.

    Subclasses must implement `name`, `domain`, and
    `generate_recommendations`. Each subclass narrows the `context` type
    annotation to its specific context profile dataclass.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this executive (e.g. 'Marriage Executive')."""

    @property
    @abstractmethod
    def domain(self) -> str:
        """The life domain this executive governs (e.g. 'Marriage')."""

    @abstractmethod
    def generate_recommendations(self, context: Any) -> list[Recommendation]:
        """Analyse a typed context profile and return prioritised recommendations.

        Args:
            context: A typed context profile dataclass prepared by
                ContextProfileBuilder. Each executive subclass declares
                the specific profile type it expects.

        Returns:
            A list of Recommendation objects, ordered by priority ascending
            (1 = highest priority).
        """
