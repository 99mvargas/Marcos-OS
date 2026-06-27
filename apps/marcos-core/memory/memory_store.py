"""In-memory implementation of the Marcos OS memory store.

This module provides a generic CRUD abstraction over memory objects. The
current implementation holds all data in Python dicts. When PostgreSQL is
connected in a future sprint, this class will be replaced (or subclassed)
with a persistent backend — all callers will use the same interface.

PostgreSQL migration notes:
    - Each stored type will map to a dedicated table.
    - `id` fields will become UUID primary keys.
    - `created_at` / `due_at` / `completed_at` will use TIMESTAMPTZ columns.
    - The `list_by` helper will become a parameterised SQL WHERE clause.
    - An async variant (asyncpg) will be introduced at integration time.
"""

from typing import Any, Optional, TypeVar

T = TypeVar("T")


class MemoryStore:
    """Generic in-memory CRUD store for Marcos OS memory objects.

    All memory objects are stored in a single dict keyed by their `id`
    field. Type discrimination is handled by the caller — pass the model
    class or a string namespace to keep collections separate.

    Attributes:
        _store: Nested dict mapping namespace -> id -> object.
    """

    def __init__(self) -> None:
        """Initialise an empty in-memory store."""
        # Future: replace with database connection pool initialisation.
        self._store: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _namespace(self, model_type: type) -> str:
        """Derive a storage namespace from a model class name.

        Args:
            model_type: The dataclass type (e.g. Commitment, Task).

        Returns:
            Lowercase class name used as the storage bucket key.
        """
        return model_type.__name__.lower()

    def _bucket(self, model_type: type) -> dict[str, Any]:
        """Return (or create) the storage bucket for a model type.

        Args:
            model_type: The dataclass type.

        Returns:
            Dict mapping id -> object for this type.
        """
        ns = self._namespace(model_type)
        if ns not in self._store:
            self._store[ns] = {}
        return self._store[ns]

    # ------------------------------------------------------------------
    # CRUD interface
    # Future: each method becomes an async DB call via asyncpg.
    # ------------------------------------------------------------------

    def create(self, obj: Any) -> Any:
        """Persist a new memory object.

        Args:
            obj: Any memory dataclass instance with an `id` attribute.

        Returns:
            The stored object.

        Raises:
            ValueError: If an object with the same id already exists.
        """
        bucket = self._bucket(type(obj))
        if obj.id in bucket:
            raise ValueError(
                f"{type(obj).__name__} with id '{obj.id}' already exists."
            )
        bucket[obj.id] = obj
        return obj

    def get(self, model_type: type[T], id: str) -> Optional[T]:
        """Retrieve a single memory object by id.

        Args:
            model_type: The dataclass type to retrieve.
            id: The unique identifier.

        Returns:
            The matching object, or None if not found.
        """
        return self._bucket(model_type).get(id)

    def update(self, obj: Any) -> Any:
        """Replace an existing memory object with an updated version.

        Args:
            obj: Updated dataclass instance. Must already exist in the store.

        Returns:
            The updated object.

        Raises:
            KeyError: If no object with the given id exists.
        """
        bucket = self._bucket(type(obj))
        if obj.id not in bucket:
            raise KeyError(
                f"{type(obj).__name__} with id '{obj.id}' does not exist."
            )
        bucket[obj.id] = obj
        return obj

    def delete(self, model_type: type, id: str) -> bool:
        """Remove a memory object by id.

        Args:
            model_type: The dataclass type to delete from.
            id: The unique identifier.

        Returns:
            True if the object was deleted, False if it did not exist.
        """
        bucket = self._bucket(model_type)
        if id in bucket:
            del bucket[id]
            return True
        return False

    def list(self, model_type: type[T]) -> list[T]:
        """Return all stored objects of a given type.

        Args:
            model_type: The dataclass type to list.

        Returns:
            List of all stored objects of that type, in insertion order.
        """
        return list(self._bucket(model_type).values())

    def list_by(self, model_type: type[T], **filters: Any) -> list[T]:
        """Return objects matching all provided field filters.

        Args:
            model_type: The dataclass type to filter.
            **filters: Field name / expected value pairs. All must match
                (AND logic). Future: becomes a SQL WHERE clause.

        Returns:
            Filtered list of matching objects.
        """
        results = []
        for obj in self._bucket(model_type).values():
            if all(getattr(obj, k, None) == v for k, v in filters.items()):
                results.append(obj)
        return results

    def count(self, model_type: type) -> int:
        """Return the number of stored objects of a given type.

        Args:
            model_type: The dataclass type to count.

        Returns:
            Integer count.
        """
        return len(self._bucket(model_type))

    # ------------------------------------------------------------------
    # Adaptive scheduling interface (architecture only — not yet implemented)
    # ------------------------------------------------------------------
    # Future implementation will follow this algorithm:
    #
    # 1. Detect overdue: query all active objects where due_at < utcnow().
    # 2. Determine importance: apply the priority model from Memory Layer spec.
    # 3. Check future availability: inspect calendar integration for open slots.
    # 4. Recommend a better time: propose a new due_at based on priority + availability.
    # 5. Avoid repeating failed patterns: track prior reschedule history per object.
    # 6. Learn from completions: update scheduling heuristics based on what succeeded.
    #
    # This will be implemented when the executive AI reasoning layer is connected.
    # ------------------------------------------------------------------
