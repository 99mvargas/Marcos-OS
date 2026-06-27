"""Data model for a single knowledge document loaded from the Obsidian vault."""

from dataclasses import dataclass


@dataclass
class KnowledgeDocument:
    """Represents a single Markdown file from the Marcos OS knowledge base.

    Attributes:
        filename: The name of the file including extension.
        relative_path: Path relative to the obsidian/ vault root.
        absolute_path: Absolute filesystem path to the file.
        category: Top-level folder within the vault (e.g. Identity, Business).
        content: Full text content of the file.
    """

    filename: str
    relative_path: str
    absolute_path: str
    category: str
    content: str
