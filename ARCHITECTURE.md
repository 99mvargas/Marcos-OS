# Marcos OS Architecture

This document describes the complete technical architecture of Marcos OS.
A new engineer or AI agent should be able to understand the system in under 30 minutes by reading this document.

---

## What Marcos OS Is

Marcos OS is a Personal Operating System. Its purpose is to reduce Marcos's mental load while increasing his effectiveness as a husband, business owner, electrician, investor, and leader.

It is not a traditional software product. It is a living knowledge and intelligence system designed to evolve for decades.

It is organized around three layers:

| Layer | Purpose |
|---|---|
| Memory | The system remembers what Marcos should not have to remember |
| Intelligence | AI reasons over memory and provides recommendations |
| Execution | Automations and AI agents execute approved work |

---

## Design Principles

These principles govern every implementation decision.

1. **Drafts before permanence.** Nothing enters Active memory automatically. Every capture becomes a Draft first.
2. **Knowledge before intelligence.** AI reasons over documented knowledge. No AI guesses without a knowledge foundation.
3. **Executives own domains.** Each life domain has a dedicated executive. Executives do not cross domain boundaries.
4. **Profiles before raw access.** Executives receive typed context profiles. They never search the repository directly.
5. **Extend, don't replace.** New capabilities are added as new handlers, stages, or executives — not by rewriting existing ones.
6. **One orchestrator.** `DailyExecutiveCycle` is the single class that owns execution order. Business logic lives in services.
7. **No vendor lock-in.** PostgreSQL, OpenRouter, Telegram, and Home Assistant are integrations — they are replaceable at the interface level.
8. **Testability at every layer.** Every model, service, and executive is independently testable without a real vault, database, or API.

---

## High-Level Layer Diagram

```
┌─────────────────────────────────────────────────────┐
│                  KNOWLEDGE LAYER                    │
│   Obsidian vault — Markdown files by life domain    │
│   obsidian/Identity, Business, Relationships, ...   │
└─────────────────┬───────────────────────────────────┘
                  │ load_knowledge()
┌─────────────────▼───────────────────────────────────┐
│                  CONTEXT LAYER                      │
│   ContextEngine — index, search, retrieve           │
│   ContextProfileBuilder — typed profiles per exec   │
└─────────────────┬───────────────────────────────────┘
                  │ typed context profiles
┌─────────────────▼───────────────────────────────────┐
│                  CAPTURE LAYER                      │
│   CapturePipeline — split raw text into statements  │
│   CaptureRouter — classify each statement           │
│   CaptureResult — typed buckets                     │
└─────────────────┬───────────────────────────────────┘
                  │ CaptureResult
┌─────────────────▼───────────────────────────────────┐
│                  MEMORY LAYER                       │
│   MemoryCommitService — CaptureResult → DraftMemory │
│   MemoryStore — CRUD for all memory objects         │
│   DraftMemory → Active → Completed → Archived       │
└─────────────────┬───────────────────────────────────┘
                  │ context + memory state
┌─────────────────▼───────────────────────────────────┐
│                  EXECUTIVE LAYER                    │
│   ExecutiveEngine — orchestrate all executives      │
│   8 × BaseExecutive — domain-specific reasoning     │
└─────────────────┬───────────────────────────────────┘
                  │ list[Recommendation]
┌─────────────────▼───────────────────────────────────┐
│               RECOMMENDATION LAYER                  │
│   Recommendation — typed, prioritized, sourced      │
│   Priority model: Faith(1) → Family(2) → ... (10)  │
└─────────────────┬───────────────────────────────────┘
                  │ MorningBrief
┌─────────────────▼───────────────────────────────────┐
│                  OUTPUT LAYER                       │
│   MorningBrief — formatted daily summary            │
│   render_brief() — console renderer                 │
│   (future: Telegram, Dashboard, Voice)              │
└─────────────────────────────────────────────────────┘
```

---

## Runtime Pipeline

The `DailyExecutiveCycle` runs these six stages sequentially on every execution:

```
Stage 1 — Load Knowledge
    load_knowledge(vault_path) → list[KnowledgeDocument]
    Recursively finds all .md files in obsidian/

Stage 2 — Build Context
    ContextEngine(documents) → indexed knowledge base
    (ContextProfileBuilder is constructed inside ExecutiveEngine)

Stage 3 — Load Memory State
    MemoryStore.count(DraftMemory) → draft_memory_count
    Reports current draft backlog (no processing at this stage)

Stage 4 — Run Executive Engine
    ExecutiveEngine(context).run() → list[Recommendation]
    Builds typed profile per executive → calls generate_recommendations()
    Merges and sorts all recommendations by priority

Stage 5 — Generate Morning Brief
    MorningBriefService(context, engine).generate() → MorningBrief
    Wraps recommendations into a displayable brief object

Stage 6 — Return DailyCycleResult
    Records timestamps, counts, execution time
    Returns a fully populated DailyCycleResult
```

---

## Core Modules

### `core/`

| Module | Responsibility |
|---|---|
| `knowledge_loader.py` | Discovers and reads `.md` files from the Obsidian vault |
| `context_engine.py` | Indexes documents; provides `get_documents_by_category()`, `search()`, `summary()` |
| `context_profile_builder.py` | Builds typed context profiles for each executive from the ContextEngine |
| `executive_engine.py` | Registers executives; dispatches typed profiles; aggregates recommendations |
| `event_bus.py` | Synchronous publish-subscribe event bus; no external dependencies |
| `executives/base_executive.py` | Abstract base class all executives must implement |
| `executives/*.py` | Eight domain executives (see Executive Architecture below) |

### `models/`

| Model | Purpose |
|---|---|
| `knowledge_document.py` | A single `.md` file loaded from the vault |
| `context_profiles.py` | 8 typed context profile dataclasses (one per executive) |
| `recommendation.py` | A single prioritized recommendation from an executive |
| `morning_brief.py` | Container for a full executive cycle output |
| `daily_cycle_result.py` | Full result of one `DailyExecutiveCycle` run |
| `event.py` | Event model and type constants for the Event Bus |
| `capture.py` | Raw input entering the Capture Pipeline |
| `capture_result.py` | Classified output from the Capture Pipeline |
| `draft_memory.py` | A provisional memory object awaiting review |
| `commitment.py` | Active promise or obligation |
| `task.py` | Discrete action item |
| `project.py` | Time-bounded goal with tasks |
| `habit.py` | Recurring behaviour being tracked |
| `recurring_responsibility.py` | Schedule-driven obligation |
| `observation.py` | Captured insight or pattern |

### `memory/`

| Module | Responsibility |
|---|---|
| `memory_store.py` | Generic in-memory CRUD store; PostgreSQL migration path documented |
| `memory_models.py` | Central re-export of all memory model types |

### `services/`

| Service | Responsibility |
|---|---|
| `daily_executive_cycle.py` | Orchestrates all six pipeline stages; returns `DailyCycleResult` |
| `morning_brief.py` | Generates and renders the Morning Brief; exports `render_brief()` |
| `capture_pipeline.py` | Splits raw text into statements; delegates to `CaptureRouter` |
| `capture_router.py` | Routes each statement to a typed bucket using ordered handlers |
| `memory_commit_service.py` | Converts `CaptureResult` into `DraftMemory` objects in `MemoryStore` |

---

## Project Structure

```
Marcos-OS/
├── CLAUDE.md                    # AI operating instructions
├── MISSION.md                   # The purpose and values of Marcos OS
├── ROADMAP.md                   # Sprint history, next sprints, technical debt
├── ARCHITECTURE.md              # This document
├── HANDOFF.md                   # Continuity document for future AI sessions
├── CONTRIBUTING.md              # Standards and workflow for contributors
├── DEVELOPMENT_GUIDE.md         # Sprint lifecycle and development process
├── README.md                    # Project overview and links
├── CHANGELOG.md                 # Version history
├── .gitignore
│
├── obsidian/                    # Marcos OS knowledge vault
│   ├── Home.md                  # Vault home page
│   ├── Identity/Identity.md     # Core identity document
│   ├── Relationships/Sara.md    # Marriage knowledge
│   ├── Home/Chai.md             # Pet knowledge
│   ├── Home/Household Operations.md
│   ├── Capture Hub/Capture Hub.md
│   └── [16 other domain folders with README.md stubs]
│
├── specs/
│   └── Memory Layer.md          # Memory Layer specification
│
├── apps/
│   └── marcos-core/             # Primary Python application
│       ├── main.py              # Entry point (minimal orchestration only)
│       ├── pyproject.toml
│       ├── requirements.txt
│       ├── core/                # Engines and orchestration
│       ├── models/              # Data models and dataclasses
│       ├── memory/              # MemoryStore and memory model exports
│       ├── services/            # Business logic services
│       ├── tests/               # Unit tests (no pytest required)
│       ├── config/              # Future configuration files
│       ├── integrations/        # Future external integrations
│       ├── prompts/             # Future AI prompt templates
│       └── logs/                # Future log output
│
├── database/                    # Future PostgreSQL schemas
├── n8n/                         # Future n8n workflow exports
├── scripts/                     # Future utility scripts
├── config/                      # Future repository-level config
└── docs/                        # Future extended documentation
```

---

## Executive Architecture

All executives inherit from `BaseExecutive` and implement three things:

```python
@property
def name(self) -> str: ...       # "Marriage Executive"
@property
def domain(self) -> str: ...     # "Marriage"
def generate_recommendations(self, context: MarriageContext) -> list[Recommendation]: ...
```

The eight domain executives:

| Executive | Domain | Context Profile | Status |
|---|---|---|---|
| PersonalExecutive | Personal | `PersonalContext` | Placeholder |
| MarriageExecutive | Marriage | `MarriageContext` | v1 — Rule-based |
| BusinessExecutive | Business | `BusinessContext` | Placeholder |
| FinanceExecutive | Finance | `FinanceContext` | Placeholder |
| HealthExecutive | Health | `HealthContext` | Placeholder |
| HomeExecutive | Home | `HomeContext` | Placeholder |
| LearningExecutive | Learning | `LearningContext` | Placeholder |
| SmartHomeExecutive | Smart Home | `SmartHomeContext` | Placeholder |

**How execution works:**

```
ExecutiveEngine.run()
    for executive in self._executives:
        profile = self._build_context(executive)   # dispatch by isinstance
        recs = executive.generate_recommendations(profile)
        all_recommendations.extend(recs)
    return sorted(all_recommendations, key=lambda r: r.priority)
```

**Adding a new executive:**

1. Create `core/executives/new_executive.py` inheriting `BaseExecutive`.
2. Add a context profile dataclass to `models/context_profiles.py`.
3. Add a build method to `core/context_profile_builder.py`.
4. Add an `isinstance` dispatch case in `ExecutiveEngine._build_context()`.
5. Register the executive in `ExecutiveEngine._register_executives()`.
6. Add tests.

---

## Context Profile Architecture

Context profiles decouple executives from the knowledge base.

**Before profiles (Sprint 001–004):**
Executives received a raw dict with a `search` callable and called `search("Sara.md")` internally. Each executive was tightly coupled to vault structure.

**After profiles (Sprint 005+):**
`ContextProfileBuilder` fetches, filters, and pre-processes documents. Executives receive a typed dataclass containing only what they need. Repository access logic lives in one place.

**Example:**

```python
@dataclass
class MarriageContext:
    sara_doc: Optional[KnowledgeDocument] = None
    household_doc: Optional[KnowledgeDocument] = None
    love_language: str = ""
```

Executives are testable without a real vault:

```python
executive.generate_recommendations(MarriageContext(sara_doc=mock_doc, love_language="Acts of Service"))
```

---

## Memory Lifecycle

```
Capture (raw text)
    ↓ CapturePipeline
CaptureResult (classified statements)
    ↓ MemoryCommitService
DraftMemory (state = "Draft")
    ↓ future: AI reviewer or Marcos approval
Active Memory (Commitment / Observation / etc.)
    ↓ when fulfilled
Completed
    ↓ archived, never deleted
Archived
```

**Why drafts first:** Rule-based classification is imperfect. A statement classified as a commitment may be hypothetical. Requiring an approval step before promotion prevents noise from polluting active tracking.

**Draft confidence tiers (v1, rule-based):**

| Type | Confidence |
|---|---|
| Relationship | 0.90 |
| Commitment | 0.85 |
| Observation | 0.80 |
| Unknown / Question | 0.00 |

---

## Capture Lifecycle

```
Raw text input (any source)
    ↓ CapturePipeline._split_statements()
    Split on: . ! ? and newlines
    ↓ CaptureRouter.route() per statement
    Handler chain (first match wins):
        _handle_commitment()    → "I need to...", "Remember to...", "I will..."
        _handle_relationship()  → "Sara said...", "Sara wants..."
        _handle_observation()   → "I noticed...", "Chai...", "The kitchen..."
        _handle_question()      → ends with "?"
        fallthrough             → unknown_items
    ↓ CaptureResult
    Buckets: commitments, observations, relationship_items, questions, unknown_items
    ↓ MemoryCommitService.commit()
    One DraftMemory per statement, all state="Draft"
```

**Extending the router:** Add a handler function `def handle_X(statement: str) -> str | None` and pass it to `CaptureRouter(extra_handlers=[handle_X])`. AI classification will slot in at the end of the chain.

---

## Event-Driven Architecture

The Event Bus (`core/event_bus.py`) enables loose coupling between components. In v1 it is synchronous and in-process.

**Current event types:**

| Constant | Value |
|---|---|
| `CAPTURE_CREATED` | `capture.created` |
| `DRAFT_CREATED` | `draft.created` |
| `MEMORY_UPDATED` | `memory.updated` |
| `RECOMMENDATIONS_GENERATED` | `recommendations.generated` |
| `MORNING_BRIEF_CREATED` | `morning_brief.created` |

**Future role:** When Telegram, Home Assistant, PostgreSQL, and n8n are connected, they will communicate through the Event Bus rather than direct service calls. This is the architectural seam that allows integrations to be added without modifying existing services.

---

## Future AI Integration

When OpenRouter is connected (Sprint 012):

1. Each executive receives its context profile as before.
2. Instead of returning `[]`, `generate_recommendations()` calls an LLM with a prompt template from `apps/marcos-core/prompts/`.
3. The LLM response is parsed into `Recommendation` objects and returned.
4. The rest of the pipeline — aggregation, sorting, Morning Brief — is unchanged.

No changes are required outside the executive files and prompt templates.

---

## Future PostgreSQL Integration

`MemoryStore` is the migration seam. When PostgreSQL is connected (Sprint 011):

1. A `PostgreSQLMemoryStore` class implementing the same interface replaces the in-memory store.
2. `DailyExecutiveCycle.__init__` receives the new store via dependency injection.
3. No callers change — they all use the `MemoryStore` interface.

Schema definitions will live in `database/`.

---

## Future Home Assistant Integration

Home Assistant state will be injected at Stage 2 of the Daily Cycle:

1. A `HomeAssistantContextEnricher` fetches current device states.
2. The `ContextProfileBuilder` receives the enricher and merges HA state into `SmartHomeContext` and `HomeContext`.
3. The Smart Home Executive uses that state to produce automation recommendations.

---

## Priority Model

Recommendations are sorted by priority (1 = highest). The default order:

| Priority | Domain |
|---|---|
| 1 | Faith |
| 2 | Family |
| 3 | Health & Safety |
| 4 | Commitments to Sara |
| 5 | Business |
| 6 | Career |
| 7 | Financial responsibilities |
| 8 | Long-term goals |
| 9 | Home maintenance |
| 10 | Convenience |

This model is defined in `specs/Memory Layer.md` and used by executives when setting `Recommendation.priority`.
