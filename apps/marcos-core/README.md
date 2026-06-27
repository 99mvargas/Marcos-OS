# marcos-core

## Purpose

Marcos Core is the orchestration engine of Marcos OS.

## Responsibilities

* Load knowledge.
* Load memory.
* Coordinate AI executives.
* Generate recommendations.
* Prioritize actions.
* Prepare future integrations.

## Architecture

### Knowledge Loader

Recursively discovers and loads every Markdown file from the Obsidian vault.
Returns a list of `KnowledgeDocument` objects.

### Context Engine

Indexes loaded documents by category and path.
Provides retrieval and search methods for downstream components.

### Executive Engine

Registers all domain executives and orchestrates a recommendation cycle.
Each executive is responsible for a specific life domain.
The engine collects, merges, and sorts all recommendations by priority.

### Executives

| Executive | Domain | Status |
|---|---|---|
| Personal Executive | Productivity, habits, time | Placeholder |
| Marriage Executive | Sara, relationships, family | **v1 — Rule-based** |
| Business Executive | Vargas Mechanical Services, growth, sales, operations | Placeholder |
| Finance Executive | Debt, investments, cash flow | Placeholder |
| Health Executive | Fitness, recovery, nutrition | Placeholder |
| Home Executive | Cleaning, household, Chai | Placeholder |
| Learning Executive | Electrical, AI, reading, skills | Placeholder |
| Smart Home Executive | Home Assistant, automations, energy, lighting | Placeholder |

#### Marriage Executive v1

Current capabilities (rule-based, no AI):

* Rule 1 — Sara document present: recommend intentional relationship investment.
* Rule 2 — Acts of Service detected in Sara.md: recommend reducing Sara's mental load.
* Rule 3 — Household Operations document present: recommend proactive household task.
* Rule 4 — No relationship knowledge: return no recommendations.

Known limitations:

* Rules fire every run cycle regardless of recency. No memory of when last recommended.
* Cannot detect whether Marcos has already acted on a recommendation.
* No date or calendar awareness.

Future AI roadmap:

* Replace rules with LLM reasoning over Sara.md and memory objects.
* Detect date planning gaps from the Memory Layer.
* Surface overdue commitments to Sara.
* Personalise recommendation cadence based on observed follow-through patterns.

### Recommendation Model

Every recommendation produced by an executive contains:

* `title` — short headline
* `description` — full explanation
* `category` — life domain
* `priority` — integer (1 = highest)
* `reasoning` — what triggered the recommendation
* `executive` — which executive produced it
* `confidence` — float 0.0–1.0

### Memory Layer

Tracks active responsibilities and adapts based on Marcos's behaviour over time.

#### Memory Objects

| Model | Purpose |
|---|---|
| `Commitment` | A promise or obligation active until completed, cancelled, or replaced |
| `Task` | A discrete action, may be linked to a parent Commitment |
| `Project` | A time-bounded goal composed of tasks and commitments |
| `Habit` | A recurring behaviour Marcos is building or maintaining |
| `RecurringResponsibility` | An obligation that resets on a fixed schedule (e.g. vet visits, bills) |
| `Observation` | A captured insight or pattern that feeds the learning model |

#### MemoryStore

Generic CRUD abstraction over all memory objects.

Methods: `create`, `get`, `update`, `delete`, `list`, `list_by`, `count`.

Current implementation: in-memory Python dicts.

#### Future PostgreSQL Integration

When PostgreSQL is connected:

* Each model type maps to a dedicated table.
* `id` fields become UUID primary keys.
* Timestamp fields use `TIMESTAMPTZ`.
* `list_by` becomes a parameterised SQL `WHERE` clause.
* An async backend (asyncpg) replaces the in-memory store.
* The `MemoryStore` interface remains unchanged — callers require no updates.

#### Adaptive Scheduling (Architecture Only)

When overdue objects are detected, the Memory Layer will:

1. Detect overdue items.
2. Determine importance using the priority model.
3. Check future availability via calendar integration.
4. Recommend a better time.
5. Avoid repeating failed scheduling patterns.
6. Learn from completed tasks to improve future recommendations.

Implementation pending executive AI reasoning integration.

### Draft Memory Layer

Marcos OS never stores uncertain information directly as active memory.
Every capture first becomes a Draft.

**Memory lifecycle:**

```
Draft → Active → Completed → Archived
```

| State | Description |
|---|---|
| Draft | Created automatically from a capture. Awaiting review. |
| Active | Approved by Marcos or a future AI reviewer. Tracked by the system. |
| Completed | The commitment or task has been fulfilled. |
| Archived | Historical record. Retained for AI learning. Never deleted. |

**Why drafts first:**

The Capture Pipeline classifies language using rules, not intent verification.
A statement classified as a commitment may be hypothetical, not an actual promise.
An observation may be inaccurate. A relationship item may be misinterpreted.

Drafts create a buffer where nothing affects Marcos's system until it has been
confirmed. This preserves the integrity of the memory layer and prevents noise
from polluting active commitments and patterns.

**MemoryCommitService:**

Converts a `CaptureResult` into `DraftMemory` objects and stores them in `MemoryStore`.
One draft per statement. No statement is dropped. Questions are stored as Unknown drafts.

**Confidence tiers (rule-based, v1):**

| Object Type | Confidence |
|---|---|
| Relationship | 0.90 |
| Commitment | 0.85 |
| Observation | 0.80 |
| Unknown / Question | 0.00 |

Confidence values will be replaced by variable AI-generated scores when the
classification layer is upgraded.

### Capture Pipeline

The Capture Pipeline is the universal intake system for Marcos OS. Every
thought, note, or event entering the system passes through this pipeline.

**Flow:**

```
raw text (Capture)
    └── CapturePipeline._split_statements()   — splits into logical statements
            └── CaptureRouter.route()          — classifies each statement
                    └── CaptureResult          — typed buckets
```

**Buckets:**

| Bucket | Description |
|---|---|
| `commitments` | Things Marcos must act on |
| `observations` | Noticed facts or patterns |
| `relationship_items` | Statements about Sara or relationships |
| `questions` | Statements phrased as questions |
| `unknown_items` | Unclassified — queued for review or AI classification |

**Extending the router:**

Add a handler function `def handle_X(statement: str) -> str | None` and
pass it to `CaptureRouter(extra_handlers=[handle_X])`. No other changes required.

**Future evolution:**

| Integration | What it enables |
|---|---|
| AI classification | Reduces unknown_items; handles ambiguous language |
| Voice capture | Speech-to-text transcripts piped into pipeline |
| Telegram | Messages from Marcos's phone routed as captures |
| Email | Summaries and action items extracted from email |
| Home Assistant | Smart home events formatted and injected as captures |
| n8n | Automation events trigger captures from any connected service |

### Context Profiles

Typed context profiles decouple executives from the knowledge base.

Previously, executives received a raw `dict` containing the ContextEngine's
`search` callable and a list of documents. This meant every executive was
responsible for knowing how to find its own data — creating tight coupling
between executives and the repository structure.

Context profiles change this. The `ContextProfileBuilder` centralises all
knowledge retrieval logic. It fetches, filters, and pre-processes documents
from the `ContextEngine`, then delivers each executive a typed dataclass
containing only what it needs.

**Benefits:**

* Repository access logic lives in one place (`ContextProfileBuilder`).
* Executives are testable without a real knowledge base — pass a profile directly.
* Adding a new knowledge source requires changes only to the builder, not to executives.
* Typed profiles make executive contracts explicit and statically checkable.

**Profiles:**

| Profile | Executive | Key fields |
|---|---|---|
| `MarriageContext` | Marriage Executive | `sara_doc`, `household_doc`, `love_language` |
| `PersonalContext` | Personal Executive | `identity_doc`, `goals_documents` |
| `BusinessContext` | Business Executive | `business_documents` |
| `FinanceContext` | Finance Executive | `finance_documents` |
| `HealthContext` | Health Executive | `health_documents` |
| `HomeContext` | Home Executive | `household_doc`, `chai_doc`, `home_documents` |
| `LearningContext` | Learning Executive | `learning_documents` |
| `SmartHomeContext` | Smart Home Executive | `tech_documents` |

### Morning Brief

The primary human-facing output of a single Marcos OS run cycle.

`MorningBriefService` executes the ExecutiveEngine, collects all recommendations,
builds a `MorningBrief` object, and renders a formatted console summary.

#### Future Evolution

| Integration | What it enables |
|---|---|
| OpenRouter (LLM) | Executives produce real AI-generated recommendations |
| PostgreSQL | Briefs are persisted and queryable historically |
| Telegram | Brief is delivered to Marcos's phone each morning |
| Home Assistant | Smart home state is included in morning context |
| Dashboard | Brief is rendered in a web UI |

### Daily Executive Cycle

The `DailyExecutiveCycle` is the single class responsible for running the
complete Marcos OS pipeline. It owns the execution order; all business logic
remains in the underlying services.

**Execution flow:**

```
DailyExecutiveCycle.run()
    │
    ├── Stage 1 — Load Knowledge
    │       load_knowledge(vault_path) → list[KnowledgeDocument]
    │
    ├── Stage 2 — Build Context
    │       ContextEngine(documents)
    │
    ├── Stage 3 — Load Memory
    │       MemoryStore.count(DraftMemory) → draft_memory_count
    │
    ├── Stage 4 — Run Executive Engine
    │       ExecutiveEngine(context).run() → list[Recommendation]
    │
    ├── Stage 5 — Generate Morning Brief
    │       MorningBriefService.generate() → MorningBrief
    │
    └── Stage 6 — Return DailyCycleResult
            started_at, completed_at, execution_time_ms, ...
```

**DailyCycleResult fields:**

| Field | Description |
|---|---|
| `started_at` | UTC timestamp when the cycle began |
| `completed_at` | UTC timestamp when the cycle finished |
| `knowledge_documents` | Documents loaded from the vault |
| `draft_memory_count` | DraftMemory objects in the store |
| `executives_run` | Number of executives executed |
| `recommendations` | Priority-sorted recommendation list |
| `morning_brief` | The generated MorningBrief |
| `execution_time_ms` | Wall-clock time in milliseconds |
| `success` | True when brief was generated and cycle completed |

**Future integrations:**

| Integration | Stage affected |
|---|---|
| PostgreSQL | Stage 5: persist brief before returning |
| OpenRouter | Stage 4: executives use LLM reasoning |
| Home Assistant | Stage 2: smart home state merged into context |
| Telegram | Stage 5: dispatch brief to Marcos's phone |
| Voice Assistant | New stage before Stage 1: transcribe and capture voice input |

### Runtime Events

The Event Bus enables loose coupling between Marcos OS components.
Publishers emit events; subscribers react to them. Neither holds a reference to the other.

**Current implementation:** synchronous, single-process, no external dependencies.

**Event types:**

| Constant | Value | Published when |
|---|---|---|
| `CAPTURE_CREATED` | `capture.created` | A raw capture enters the pipeline |
| `DRAFT_CREATED` | `draft.created` | A DraftMemory object is committed |
| `MEMORY_UPDATED` | `memory.updated` | A memory object changes state |
| `RECOMMENDATIONS_GENERATED` | `recommendations.generated` | Executive Engine completes a run cycle |
| `MORNING_BRIEF_CREATED` | `morning_brief.created` | A Morning Brief is generated |

**Usage:**

```python
bus = EventBus()
bus.subscribe(CAPTURE_CREATED, my_handler)
bus.publish(CAPTURE_CREATED, payload={"source": "telegram"})
bus.unsubscribe(CAPTURE_CREATED, my_handler)
```

**Future evolution:**

When integrations are connected, they will communicate through the Event Bus rather than direct calls:

| Integration | Event Bus role |
|---|---|
| Telegram | Subscribes to `morning_brief.created` to deliver the brief; publishes `capture.created` on incoming messages |
| Home Assistant | Publishes `capture.created` on automation triggers; subscribes to `recommendations.generated` to execute approved actions |
| PostgreSQL | Subscribes to all event types to write a persistent event log |
| AI reviewer | Subscribes to `draft.created` to evaluate and promote high-confidence drafts |
| n8n | Publishes events via webhook; subscribes to trigger workflow executions |

## Current Limitations

* Executives return empty recommendation lists. LLM reasoning is not yet implemented.
* MemoryStore uses in-memory storage only. PostgreSQL not yet connected.
* No external API integrations.
* Adaptive scheduling algorithm not yet implemented.

## Future Roadmap

* Connect executives to LLM reasoning via OpenRouter.
* Replace MemoryStore with PostgreSQL backend (asyncpg).
* Integrate n8n for automation execution.
* Add Home Assistant integration to Smart Home Executive.
* Add calendar and email integrations.
* Implement adaptive scheduling algorithm.
* Build Telegram delivery for daily recommendation briefings.
