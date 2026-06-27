# Marcos OS Roadmap

# Current Version

v0.1.0

# Current Sprint

Sprint 010 — Finance Executive

# Completed Sprints

## Sprint 001 — Executive Engine

Established the AI executive team architecture.
Implemented `ExecutiveEngine`, `BaseExecutive`, and eight domain executives as typed placeholders.
Defined the `Recommendation` model.

## Sprint 002 — Memory Layer

Implemented the persistent memory abstraction.
Created six memory object models: `Commitment`, `Task`, `Project`, `Habit`, `RecurringResponsibility`, `Observation`.
Implemented `MemoryStore` with generic CRUD and documented the PostgreSQL migration path.
Defined the adaptive scheduling algorithm architecture.

## Sprint 003 — Morning Brief

Delivered the first human-facing output of Marcos OS.
Implemented `MorningBriefService` and `MorningBrief` model.
Wired the full startup cycle: Knowledge → Context → Executive Engine → Morning Brief.

## Sprint 004 — Marriage Executive v1

Implemented the first working executive producing real recommendations.
Rule-based engine reads `Sara.md` and `Household Operations.md` directly.
Produces three recommendations: intentional time, Acts of Service, household task ownership.

## Sprint 005 — Context Profiles

Decoupled executives from direct repository access.
Introduced typed context profile dataclasses for all eight executives.
Implemented `ContextProfileBuilder` as the single point of contact between the knowledge base and the executive team.

## Sprint 006 — Capture Pipeline

Implemented the universal intake system for Marcos OS.
Created `CapturePipeline`, `CaptureRouter`, `Capture`, and `CaptureResult`.
Router classifies input into: commitments, observations, relationship items, questions, and unknown items.
Extensible handler chain architecture — AI classification slots in without replacing existing handlers.

## Sprint 007 — Memory Commit Service

Implemented the Draft Memory Layer.
Created `DraftMemory` model and `MemoryCommitService`.
All captures enter the system as Drafts. Nothing becomes Active automatically.
Established the memory lifecycle: Draft → Active → Completed → Archived.

## Sprint 008 — Event Bus

Implemented the synchronous publish-subscribe Event Bus.
Created `Event` model and `EventBus` class with subscribe, unsubscribe, publish, and dispatch.
Defined five event type constants covering the full pipeline lifecycle.

## Sprint 009 — Daily Executive Cycle

Wired the complete daily runtime pipeline into a single orchestrator.
Implemented `DailyExecutiveCycle` with six ordered stages: Knowledge → Context → Memory → Executive Engine → Morning Brief → Result.
Implemented `DailyCycleResult` with timestamps, counts, and execution time.
Extracted `render_brief()` as a standalone function to eliminate double vault loading.
Simplified `main.py` to: banner → cycle → summary → brief.

# Next Planned Sprints

## Sprint 010 — Finance Executive

Implement the first working Finance Executive with rule-based recommendations.
Rules derived from Finances knowledge objects.
Cover: unnecessary spending detection, debt tracking, investment reminders.

## Sprint 011 — PostgreSQL Integration

Replace `MemoryStore` in-memory backend with a real PostgreSQL connection.
Implement schema migrations.
All memory objects and draft objects persisted across restarts.

## Sprint 012 — OpenRouter AI Orchestrator

Connect executives to LLM reasoning via OpenRouter.
Executives produce AI-generated recommendations rather than rule-based output.
Implement prompt templates per executive domain.

## Sprint 013 — Telegram Connector

Deliver the Morning Brief to Marcos's phone via Telegram.
Accept captures via Telegram messages.
Wire Telegram events into the Capture Pipeline.

# Technical Debt

Technical debt is intentionally tracked here rather than immediately resolved.
Identifying and documenting debt is preferable to hiding it or resolving it prematurely at the expense of delivery.

| ID | Description | Status |
|---|---|---|
| TD-001 | Executive domain mapping — MarriageExecutive domain was `"Marriage"` but knowledge lives in `"Relationships"`. Resolved via `ContextProfileBuilder` cross-category search in Sprint 005. | Resolved |
| TD-002 | Capture questions are currently stored as Unknown Drafts. Questions have no dedicated `DraftMemory` object type. Requires a `Question` type and a review workflow. | Planned |

# Architecture

The Marcos OS runtime flows through seven layers, each building on the last.

```
Knowledge Layer
    Obsidian vault — Markdown files organized by life domain
    ↓
Context Layer
    ContextEngine — indexes and retrieves knowledge documents
    ContextProfileBuilder — assembles typed profiles per executive
    ↓
Capture Layer
    CapturePipeline — splits and classifies raw input
    CaptureRouter — routes statements to typed buckets
    ↓
Memory Layer
    MemoryCommitService — converts captures into Draft memory objects
    MemoryStore — persists all memory objects (PostgreSQL in future)
    ↓
Executive Layer
    ExecutiveEngine — orchestrates all domain executives
    8 × BaseExecutive — generate domain-specific recommendations
    ↓
Recommendation Layer
    Recommendation objects — typed, prioritized, sourced
    ↓
Output Layer
    MorningBrief — formatted daily summary
    (future: Telegram, Dashboard, Voice)
```

# Long-Term Vision

Marcos OS is designed to evolve for decades. The long-term system includes:

* **PostgreSQL** — all memory objects, drafts, recommendations, and briefs persisted and queryable.
* **Home Assistant** — smart home state feeds into executive context; automations execute approved recommendations.
* **Voice Capture** — speech-to-text transcripts enter the Capture Pipeline directly from any room.
* **Telegram** — Morning Briefs delivered to Marcos's phone; captures accepted via message.
* **Dashboard** — web interface displaying active commitments, drafts, recommendations, and system health.
* **Mobile App** — native iOS/Android interface for capture, review, and approval of drafts.
* **AI Executive Team** — all executives powered by LLM reasoning over the full knowledge and memory graph, producing personalized and context-aware recommendations.
