"""Discovers and loads the Marcos OS Obsidian knowledge base from disk."""

from pathlib import Path

from models.knowledge_document import KnowledgeDocument


def load_knowledge(vault_path: Path) -> list[KnowledgeDocument]:
    """Recursively find and load every Markdown file in the Obsidian vault.

    Args:
        vault_path: Absolute path to the obsidian/ directory.

    Returns:
        A list of KnowledgeDocument objects, one per .md file found.

    Raises:
        FileNotFoundError: If vault_path does not exist.
    """
    if not vault_path.exists():
        raise FileNotFoundError(f"Obsidian vault not found: {vault_path}")

    documents: list[KnowledgeDocument] = []

    for md_file in sorted(vault_path.rglob("*.md")):
        relative = md_file.relative_to(vault_path)
        parts = relative.parts
        category = parts[0] if len(parts) > 1 else ""

        documents.append(
            KnowledgeDocument(
                filename=md_file.name,
                relative_path=str(relative),
                absolute_path=str(md_file.resolve()),
                category=category,
                content=md_file.read_text(encoding="utf-8"),
            )
        )

    return documents
