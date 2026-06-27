# Marcos OS — Handoff Document

This document is written for a future Claude Code conversation. Read this first.

---

## What You Are Building

Marcos OS is a Personal Operating System for Marcos Vargas. Not a computer OS.
Its purpose is to reduce his mental load across life, marriage, business, and finances
by combining knowledge, memory, AI reasoning, and automation.

You are the **Chief Builder** — an implementation agent. Your role is to build from
specifications provided by the Chief Systems Architect (ChatGPT). Do not redesign.
Do not invent architecture. Ask before making assumptions.

Your operating instructions live in [`CLAUDE.md`](CLAUDE.md). Read it before every session.

---

## Recommended Reading Order

For a new session, read these files in order:

1. [`CLAUDE.md`](CLAUDE.md) — your role and operating rules
2. This file — current state, what's done, what's next
3. [`ARCHITECTURE.md`](ARCHITECTURE.md) — how the system is structured
4. [`ROADMAP.md`](ROADMAP.md) — sprint history and upcoming work
5. [`apps/marcos-core/README.md`](apps/marcos-core/README.md) — full component reference

Then read the relevant source files for the sprint you are implementing.

---

## Repository Status (as of Sprint 009)

| Item | Status |
|---|---|
| Python version | 3.11+ required |
| External dependencies | None (stdlib only) |
| Database | In-memory (PostgreSQL planned Sprint 011) |
| AI integration | None (OpenRouter planned Sprint 012) |
| Telegram | Not connected (planned Sprint 013) |
| Home Assistant | Not connected (planned future) |
| Tests | 8 test files, all stdlib unittest-style, no pytest required |
| main.py | Runs end-to-end; loads vault once; renders Morning Brief |

---

## Completed Sprints

| Sprint | Name | What Was Built |
|---|---|---|
| 000 | Repository Init | CLAUDE.md, README, CHANGELOG, .gitignore, MISSION.md, ROADMAP.md |
| KB | Knowledge Layer | Obsidian vault with 18 domain folders and populated personal documents |
| 001 | Executive Engine | `BaseExecutive`, `ExecutiveEngine`, 8 domain executives (placeholders), `Recommendation` model |
| 002 | Memory Layer | 6 memory models, `MemoryStore` (in-memory CRUD), PostgreSQL migration path documented |
| 003 | Morning Brief | `MorningBriefService`, `MorningBrief` model, console output |
| 004 | Marriage Executive v1 | Rule-based `MarriageExecutive` producing 3 real recommendations |
| 005 | Context Profiles | 8 typed context profile dataclasses, `ContextProfileBuilder`, executives decoupled from raw knowledge |
| 006 | Capture Pipeline | `CapturePipeline`, `CaptureRouter`, `Capture`, `CaptureResult`, handler chain architecture |
| 007 | Memory Commit Service | `DraftMemory` model, `MemoryCommitService`, Draft lifecycle established |
| 008 | Event Bus | `Event` model, `EventBus` (synchronous pub/sub), 5 event type constants |
| 009 | Daily Executive Cycle | `DailyExecutiveCycle` (6-stage orchestrator), `DailyCycleResult`, simplified `main.py`, `render_brief()` extracted |

---

## Current Architecture Summary

```
Knowledge Layer (obsidian/)
    → ContextEngine (index and search)
        → ContextProfileBuilder (typed profiles per executive)
            → ExecutiveEngine (orchestrates 8 executives)
                → Recommendation objects (typed, prioritized)
                    → MorningBrief (formatted output)
                        → render_brief() (console renderer)

All stages orchestrated by DailyExecutiveCycle.run()
DailyCycleResult carries all output counts and the generated brief.
```

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the complete layer diagram, runtime pipeline, and integration seams.

---

## Coding Conventions

### Python

- Python 3.11+ features used throughout (`list[X]`, `X | None`, `match`)
- All models: `@dataclass` with type hints
- Use `field(default_factory=...)` for mutable defaults
- `__post_init__` for validation (e.g., `DraftMemory` validates `object_type` and `confidence`)
- Module-level constants in `UPPER_SNAKE_CASE` (e.g., `_PRIORITY_HIGH = 2`)
- Private attributes prefixed with `_`
- Abstract base classes use `ABC` and `@abstractmethod`
- `pathlib.Path` for all filesystem operations — never string paths
- `uuid.uuid4()` for IDs
- `time.perf_counter_ns()` for execution timing
- No external dependencies — stdlib only (no `requests`, no `psycopg2`, no AI SDK yet)

### Docstrings

- All public classes and functions have Google-style docstrings
- Private helpers: one-line docstring only
- Models: class-level docstring plus `Attributes:` section
- Avoid over-commenting — the code is the documentation

### Comments

- Default: no comments
- Acceptable: hidden invariants, non-obvious workarounds, future integration seams marked `# future:`
- Never: "what" comments, task references, change log comments

### File naming

- All Python files: `snake_case.py`
- All documentation: `UPPER_CASE.md`
- All test files: `test_<module>.py`

---

## Repository Conventions

### Structure

```
apps/marcos-core/
    core/           — engines (knowledge, context, executive, event bus)
    models/         — dataclasses only, no business logic
    memory/         — MemoryStore and memory model re-exports
    services/       — business logic that coordinates core components
    tests/          — one test file per module
    config/         — placeholder (future config files)
    integrations/   — placeholder (future external connectors)
    prompts/        — placeholder (future LLM prompt templates)
    logs/           — placeholder (future log output)
```

### Import resolution

`main.py` inserts `_APP_ROOT` (the `marcos-core/` directory) into `sys.path`.
Test files insert `Path(__file__).resolve().parents[1]` (also `marcos-core/`).
All imports are absolute from there: `from core.context_engine import ContextEngine`.

### Placeholder executives

Seven executives are currently placeholders. They return `[]` from `generate_recommendations()`.
Do not remove them. Do not fill them in without a spec. They are structural stubs awaiting AI integration.

### `.gitkeep` files

Empty directories use `.gitkeep`. Do not delete them — they reserve future integration points.

---

## Known Technical Debt

| ID | Description | Status |
|---|---|---|
| TD-001 | MarriageExecutive domain was `"Marriage"` but Sara.md lives in `Relationships/`. Resolved by `ContextProfileBuilder` doing cross-category search. | Resolved |
| TD-002 | Questions from `CapturePipeline` are stored as `OBJECT_TYPE_UNKNOWN` with `confidence=0.0`. No dedicated `Question` object type exists. | Open — planned for a future sprint |

---

## What Must Never Be Changed

These files or patterns must not be modified without explicit instruction:

| Item | Reason |
|---|---|
| `CLAUDE.md` | Permanent AI operating instructions — only changed by direct user command |
| `BaseExecutive` interface | Changing `name`, `domain`, or `generate_recommendations` signature breaks all executives |
| `MemoryStore` method signatures | PostgreSQL migration depends on this interface being stable |
| `DailyExecutiveCycle` stage order | Stages have data dependencies — reordering breaks the pipeline |
| The priority model (1–10) | Drives all recommendation sorting across the entire executive layer |
| Draft-first invariant | Nothing should bypass Draft state and write directly to Active memory |

---

## Next Planned Sprints

### Sprint 010 — Finance Executive

Implement the first working `FinanceExecutive` with rule-based recommendations.
- Read from `Finances/` category documents
- Produce rules for: debt tracking, spending awareness, investment reminders
- Pattern: follow the `MarriageExecutive` implementation exactly

### Sprint 011 — PostgreSQL Integration

Replace `MemoryStore` in-memory backend.
- All memory objects, drafts, and briefs persisted across restarts
- Schema definitions in `database/`
- `DailyExecutiveCycle` receives store via dependency injection (already wired)

### Sprint 012 — OpenRouter AI Orchestrator

Connect executives to LLM reasoning.
- Prompt templates in `apps/marcos-core/prompts/`
- Executives call LLM in `generate_recommendations()`; rest of pipeline unchanged
- Recommendation confidence becomes AI-generated

### Sprint 013 — Telegram Connector

Deliver Morning Brief to Marcos's phone.
- Subscribe to `MORNING_BRIEF_CREATED` on the Event Bus
- Accept raw text captures via incoming Telegram messages
- Route through existing `CapturePipeline`

---

## Architecture Decisions

### Why `ContextProfileBuilder` exists

Sprint 001–004 executives received a raw dict with a `search` callable.
Each executive was responsible for knowing vault structure.
Sprint 005 centralised that coupling into `ContextProfileBuilder`.
Now executives only know about their typed profile dataclass — they can be tested without a vault.

### Why `render_brief()` is a standalone function

`MorningBriefService.print_brief()` was added first, but it required a live `ContextEngine`
and `ExecutiveEngine` just to read two integers. Sprint 009 extracted `render_brief()` as a
module-level function that takes those integers directly. `main.py` now calls it with counts
from `DailyCycleResult` — no second vault load, no service reconstruction.

### Why drafts exist

Rule-based classification is imperfect. A statement like "I wonder if I need to call the bank"
should not create an Active commitment. Drafts are the mandatory intermediate state that prevents
noise from polluting the memory layer. Everything enters as Draft and requires promotion to Active.

### Why `DailyExecutiveCycle` owns stage order

Business logic must not know what runs before or after it. The orchestrator is the one place
where execution order is encoded. If you need to add a new stage (e.g., voice transcription),
add it to `DailyExecutiveCycle.run()` — not to an existing service.

### Why the Event Bus is synchronous

At v1, there are no external consumers. Async/threading adds complexity without benefit.
The Event Bus interface is already correct for a future async upgrade — only the dispatch
internals change, not the `subscribe`/`publish` API.

---

## Lessons Learned

- **Read the full file before editing.** Edit conflicts in `morning_brief.py` were caused by
  trying to use `Edit` on a section where the target string was not unique. When a file has
  repeated patterns, write it in full using `Write`.

- **Do not double-load the vault.** `main.py` originally loaded the vault twice — once inside
  `DailyExecutiveCycle` and once in a context shim to support `print_brief()`. The `render_brief()`
  function was created specifically to eliminate this. Never reconstruct services for rendering purposes.

- **isinstance dispatch is the right pattern for executive context.** A registry dict keyed by
  executive class was considered, but `isinstance` dispatch in `_build_context()` is simpler,
  explicit, and statically readable. Use it for all future executives.

- **Placeholder executives return `[]` — that is correct.** Do not interpret empty recommendation
  lists as a bug. Seven of eight executives are structural stubs pending AI integration. The system
  is designed to produce output from the one implemented executive (Marriage) while others await specs.

---

## Important Files

| File | Purpose |
|---|---|
| `CLAUDE.md` | AI operating instructions — read first in every session |
| `ARCHITECTURE.md` | Full system architecture — read for any structural questions |
| `ROADMAP.md` | Sprint history and upcoming work |
| `specs/Memory Layer.md` | Defines memory object types, priority model, lifecycle |
| `apps/marcos-core/main.py` | Entry point — should stay minimal |
| `apps/marcos-core/services/daily_executive_cycle.py` | Orchestration — the system's spine |
| `apps/marcos-core/core/context_profile_builder.py` | All vault access logic lives here |
| `apps/marcos-core/core/executives/marriage_executive.py` | Reference implementation for future executives |
| `apps/marcos-core/models/context_profiles.py` | All 8 executive context dataclasses |
| `obsidian/Identity/Identity.md` | Marcos's core identity document |
| `obsidian/Relationships/Sara.md` | Marriage knowledge — drives Marriage Executive |
