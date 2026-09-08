# Contributing to Marcos OS

This document defines the standards for all contributors — human and AI.

---

## Roles

| Role | Responsibility |
|---|---|
| Chief Systems Architect (ChatGPT) | Designs architecture, writes specifications, defines sprints |
| Chief Builder (Claude Code) | Implements specifications, maintains documentation, preserves consistency |
| Repository Owner (Marcos Vargas) | Approves sprints, provides direction, makes architectural decisions |

The Chief Builder **never redesigns**. If a specification is unclear or conflicts with existing architecture, stop and request clarification.

As of the Autonomous Agent Protocol v1.0, these three roles are extended
(not replaced) by seven formal roles — Chairman, Architect, Researcher,
Builder, Reviewer, Tester, Orchestrator — with explicit allowed/prohibited
actions and handoff conditions. See `docs/AGENT_ROLES.md` and
`docs/AUTONOMOUS_AGENT_PROTOCOL.md`.

---

## Python Conventions

### Version

Python 3.11+ is required. Use modern type hints throughout.

```python
# Correct
def get(self, model_type: type, id: str) -> object | None: ...
def run(self) -> list[Recommendation]: ...

# Incorrect
from typing import Optional, List
def get(self, model_type: type, id: str) -> Optional[object]: ...
def run(self) -> List[Recommendation]: ...
```

### Data models

All models are `@dataclass` with explicit type hints and defaults.

```python
@dataclass
class DraftMemory:
    id: str
    object_type: str
    title: str
    content: str
    source: str = "manual"
    state: str = STATE_DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 1.0
```

- Use `field(default_factory=...)` for mutable defaults (lists, dicts)
- Use `__post_init__` for validation only — no business logic in models
- Never add methods to models beyond computed properties and `__post_init__`

### Constants

```python
# Module-level constants: UPPER_SNAKE_CASE
_PRIORITY_HIGH = 2
_EXECUTIVE_NAME = "Marriage Executive"

# Exported constants (used in tests or by callers): no leading underscore
STATE_DRAFT = "Draft"
OBJECT_TYPE_COMMITMENT = "Commitment"
```

### Naming

| Pattern | Convention |
|---|---|
| Files | `snake_case.py` |
| Classes | `PascalCase` |
| Methods and functions | `snake_case` |
| Private attributes | `_leading_underscore` |
| Constants | `UPPER_SNAKE_CASE` |
| Test functions | `test_<description>` |

### Imports

- Stdlib first, then internal imports
- Absolute imports from `apps/marcos-core/` root (e.g., `from core.context_engine import ContextEngine`)
- No relative imports
- No wildcard imports

### Filesystem

- Use `pathlib.Path` exclusively — never string concatenation for paths
- Use `rglob("*.md")` for vault discovery
- Use `path.read_text(encoding="utf-8")` for reading files

### IDs and timing

```python
import uuid
import time

id = str(uuid.uuid4())
elapsed_ns = time.perf_counter_ns()
elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
```

### Dependencies

**No external dependencies.** Marcos Core uses Python stdlib only.

Do not add packages to `requirements.txt` without an explicit architectural decision.
When PostgreSQL, OpenRouter, and Telegram are integrated, they will be added at that time — not before.

---

## Docstrings

All public classes and functions require Google-style docstrings.

```python
class ContextProfileBuilder:
    """Assembles typed context profiles from ContextEngine data.

    Acts as the single point of contact between the knowledge base and the
    executive team. All vault access logic lives here.

    Attributes:
        _engine: The ContextEngine to query.
    """

def build_marriage_context(self) -> MarriageContext:
    """Build a MarriageContext from available knowledge.

    Searches for Sara.md in the Relationships category, extracts the
    detected love language, and finds the Household Operations document.

    Returns:
        A populated MarriageContext. Fields are None or empty string
        if the corresponding documents are not found.
    """
```

Private methods: one-line docstring only.

```python
def _find(self, docs: list[KnowledgeDocument], filename: str) -> KnowledgeDocument | None:
    """Return the first document whose filename matches, or None."""
```

**Never write comments that describe what the code does.** Write comments only when the **why** is non-obvious.

---

## Testing Expectations

### One test file per module

```
services/capture_pipeline.py  →  tests/test_capture_pipeline.py
core/event_bus.py             →  tests/test_event_bus.py
models/draft_memory.py        →  (covered by test_memory_commit_service.py)
```

### Test structure

```python
def test_<what_it_does>() -> None:
    """One sentence: what this test verifies."""
    # Arrange
    ...
    # Act
    result = ...
    # Assert
    assert result == expected
```

- Tests are functions, not classes (no `unittest.TestCase`)
- No pytest required — tests run with `python tests/test_<module>.py`
- Each test file has a `if __name__ == "__main__":` runner at the bottom
- Tests must be independent — no shared state between test functions
- Tests must not depend on network, database, or external services

### Vault integration tests

Tests that use the real vault must handle it gracefully:

```python
_REPO_ROOT = Path(__file__).resolve().parents[3]
_VAULT_PATH = _REPO_ROOT / "obsidian"
```

If the vault does not contain a required document, the test must still pass — return empty profiles, not errors.

### Definition of Done for tests

- Every new public method has at least one test
- Every new model has tests for defaults, validation, and computed properties
- Every new executive has tests for: no context → no recommendations, minimum context → expected recommendations
- All edge cases handled: empty vault, missing documents, empty strings

---

## Repository Structure

Do not create new top-level directories without an explicit architectural decision.
Do not create new files inside existing directories without a spec or direct instruction.

When adding a new executive:
1. `core/executives/new_executive.py`
2. Entry in `models/context_profiles.py`
3. Build method in `core/context_profile_builder.py`
4. `isinstance` dispatch in `ExecutiveEngine._build_context()`
5. Registration in `ExecutiveEngine._register_executives()`
6. `tests/test_executive_engine.py` — add registration test and rule tests

When adding a new model:
1. `models/new_model.py`
2. Re-export in `memory/memory_models.py` if it is a memory object type
3. Tests in the relevant test file

---

## Sprint Workflow

### Before a sprint

1. Receive the sprint specification from the Chief Systems Architect.
2. Read the specification fully.
3. Read all files that will be affected.
4. Identify any conflicts with existing architecture.
5. If conflicts exist: stop and report before writing any code.

### During a sprint

1. Implement only what is specified.
2. Do not add features, optimizations, or refactors not in the spec.
3. Do not modify files outside the sprint scope.
4. Keep `ROADMAP.md` current (mark sprint as completed, update "Current Sprint").

### After a sprint

1. Summarize: files created, files modified, key decisions.
2. Do not propose the next sprint — wait for instruction.
3. Stop and wait.

---

## Architecture Rules

These rules apply to all implementations:

1. **Models are dumb.** No business logic in `models/`. Only dataclass fields, `__post_init__` validation, and computed properties.

2. **Services coordinate.** `services/` contains classes that use `core/` components to accomplish a goal. Services do not contain knowledge about vault structure.

3. **Core is stateless where possible.** `ContextEngine` and `ContextProfileBuilder` hold state only as a cache of loaded documents — they do not mutate data.

4. **Executives are isolated.** Each executive receives a typed context profile and returns a list of recommendations. They do not call other executives, services, or the knowledge base directly.

5. **`DailyExecutiveCycle` owns order.** Stage sequencing lives only in `DailyExecutiveCycle.run()`. Services do not call each other.

6. **Dependency injection over globals.** `DailyExecutiveCycle` accepts an optional `MemoryStore` parameter. `CaptureRouter` accepts `extra_handlers`. This pattern enables testing without mocking.

7. **No premature integration.** Do not add PostgreSQL, async, AI, or Telegram code until those sprints begin. Placeholder `.gitkeep` files exist to signal the future without blocking the present.

---

## Definition of Done

A sprint is complete when:

- [ ] All specified files are created or modified
- [ ] All new public APIs have docstrings
- [ ] All new modules have a corresponding test file
- [ ] All tests pass when run with `python tests/test_<module>.py`
- [ ] `ROADMAP.md` reflects the completed sprint
- [ ] `apps/marcos-core/README.md` reflects any new components
- [ ] No unspecified files were created or modified
- [ ] No existing tests were broken

---

## How to Propose Architectural Improvements

The Chief Builder does not propose architecture. The Chief Systems Architect (ChatGPT) designs.

If the Chief Builder identifies a structural issue during implementation:

1. Stop.
2. Report the issue clearly: what was found, what the impact is, what the options are.
3. Do not implement a solution.
4. Wait for a decision from the Chief Systems Architect or Repository Owner.

The only exception: if a bug is introduced during the current sprint (e.g., a double vault load
identified immediately), the Chief Builder may fix it and document the fix.
