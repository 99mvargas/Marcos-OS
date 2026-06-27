"""Orchestrates the complete Marcos OS Daily Executive Cycle.

The DailyExecutiveCycle is the single class responsible for running
the full Marcos OS pipeline in the correct order. It does not implement
business logic — it coordinates existing services and returns a
structured result.

Pipeline stages:
    1. Load Knowledge   — discover and read all Obsidian vault documents
    2. Build Context    — index documents and build typed executive profiles
    3. Load Memory      — retrieve current Draft Memory count from MemoryStore
    4. Run Executives   — execute all domain executives; collect recommendations
    5. Generate Brief   — produce the Morning Brief from executive output
    6. Return Result    — assemble and return a DailyCycleResult
"""

import time
from datetime import datetime
from pathlib import Path

from core.context_engine import ContextEngine
from core.executive_engine import ExecutiveEngine
from core.knowledge_loader import load_knowledge
from memory.memory_store import MemoryStore
from models.daily_cycle_result import DailyCycleResult
from models.draft_memory import DraftMemory
from models.morning_brief import MorningBrief
from models.recommendation import Recommendation
from services.morning_brief import MorningBriefService


class DailyExecutiveCycle:
    """Orchestrates the complete Marcos OS runtime pipeline.

    Each call to run() executes all six pipeline stages in order and
    returns a DailyCycleResult containing every measurable outcome.

    The cycle does not own business logic. Each stage delegates to the
    relevant service or engine. Adding, removing, or replacing a stage
    requires changes only here, not in the underlying services.

    Future evolution:
        - Stage 3 will write the brief to PostgreSQL before returning.
        - Stage 2 will incorporate Home Assistant state into context profiles.
        - Stage 4 will use OpenRouter LLM reasoning inside each executive.
        - Stage 5 will dispatch the brief via Telegram.
        - A voice capture stage will be inserted before Stage 1.
        - Event Bus hooks will fire at each stage boundary.

    Attributes:
        _vault_path: Absolute path to the Obsidian knowledge vault.
        _store: The MemoryStore instance shared across the cycle.
    """

    def __init__(self, vault_path: Path, store: MemoryStore | None = None) -> None:
        """Initialise the DailyExecutiveCycle.

        Args:
            vault_path: Absolute path to the Obsidian vault directory.
            store: Optional MemoryStore instance. A new empty store is
                created if None is provided. Pass an existing store to
                preserve memory state across multiple cycle runs.
        """
        self._vault_path = vault_path
        self._store = store or MemoryStore()

    def run(self) -> DailyCycleResult:
        """Execute the complete Marcos OS pipeline and return a result.

        Runs all six pipeline stages sequentially. If any stage raises
        an unhandled exception, it propagates to the caller — no partial
        results are returned.

        Returns:
            A fully populated DailyCycleResult.
        """
        result = DailyCycleResult(started_at=datetime.utcnow())
        start_ns = time.perf_counter_ns()

        # Stage 1 — Load Knowledge
        documents = load_knowledge(self._vault_path)
        result.knowledge_documents = len(documents)

        # Stage 2 — Build Context
        context = ContextEngine(documents)

        # Stage 3 — Load Draft Memory count
        result.draft_memory_count = self._store.count(DraftMemory)

        # Stage 4 — Run Executive Engine
        executive_engine = ExecutiveEngine(context)
        result.executives_run = len(executive_engine.executives)
        recommendations: list[Recommendation] = executive_engine.run()
        result.recommendations = recommendations

        # Stage 5 — Generate Morning Brief
        brief_service = MorningBriefService(context, executive_engine)
        brief: MorningBrief = brief_service.generate()
        result.morning_brief = brief

        # Stage 6 — Finalise result
        result.completed_at = datetime.utcnow()
        elapsed_ns = time.perf_counter_ns() - start_ns
        result.execution_time_ms = elapsed_ns / 1_000_000

        return result

    @property
    def store(self) -> MemoryStore:
        """The MemoryStore instance used by this cycle."""
        return self._store
