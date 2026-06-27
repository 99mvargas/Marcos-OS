"""Prepares and surfaces relevant knowledge for AI reasoning in Marcos OS."""

from models.knowledge_document import KnowledgeDocument


class ContextEngine:
    """Indexes loaded knowledge documents and provides retrieval methods.

    The ContextEngine is the query interface over the knowledge base. It does
    not perform AI reasoning — it organises documents so that future AI layers
    can retrieve focused, relevant context efficiently.

    Attributes:
        _documents: The full list of loaded KnowledgeDocuments.
        _by_category: Documents grouped by top-level vault category.
        _by_path: Documents indexed by relative path for O(1) lookup.
    """

    def __init__(self, documents: list[KnowledgeDocument]) -> None:
        """Initialise the ContextEngine with a loaded knowledge base.

        Args:
            documents: All KnowledgeDocument objects returned by the
                KnowledgeLoader.
        """
        self._documents: list[KnowledgeDocument] = documents
        self._by_category: dict[str, list[KnowledgeDocument]] = {}
        self._by_path: dict[str, KnowledgeDocument] = {}

        for doc in documents:
            self._by_category.setdefault(doc.category, []).append(doc)
            self._by_path[doc.relative_path] = doc

    def get_documents_by_category(self, category: str) -> list[KnowledgeDocument]:
        """Return every document belonging to a top-level vault category.

        Args:
            category: The folder name exactly as it appears in the vault
                (e.g. "Identity", "Business", "Capture Hub").

        Returns:
            A list of matching KnowledgeDocuments, or an empty list if the
            category does not exist.
        """
        return self._by_category.get(category, [])

    def get_document(self, relative_path: str) -> KnowledgeDocument | None:
        """Return a single document by its path relative to the vault root.

        Args:
            relative_path: The relative path used when the document was loaded
                (e.g. "Identity/Identity.md").

        Returns:
            The matching KnowledgeDocument, or None if not found.
        """
        return self._by_path.get(relative_path)

    def search(self, keyword: str) -> list[KnowledgeDocument]:
        """Case-insensitive full-text search across all document contents.

        Args:
            keyword: The term to search for within document content.

        Returns:
            All KnowledgeDocuments whose content contains the keyword,
            in load order.
        """
        keyword_lower = keyword.lower()
        return [doc for doc in self._documents if keyword_lower in doc.content.lower()]

    def summary(self) -> dict:
        """Return a high-level summary of the loaded knowledge base.

        Returns:
            A dictionary with keys:
                total_documents: int — total number of documents loaded.
                categories: list[str] — sorted list of category names.
                documents_per_category: dict[str, int] — document count per
                    category.
        """
        return {
            "total_documents": len(self._documents),
            "categories": sorted(self._by_category.keys()),
            "documents_per_category": {
                category: len(docs)
                for category, docs in sorted(self._by_category.items())
            },
        }
