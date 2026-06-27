# Marcos OS

Personal Operating System for Marcos Vargas.

**Status:** In Development — Sprint 009 Complete

---

## Purpose

Marcos OS reduces Marcos's mental load by combining knowledge, memory, AI reasoning, and automation across his life, marriage, business, and finances.

It is not a computer operating system. It is a personal intelligence layer that learns, remembers, and advises.

---

## Documentation

| Document | Purpose |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | System architecture, layer diagram, runtime pipeline, integration seams |
| [`HANDOFF.md`](HANDOFF.md) | Continuity document for future Claude Code sessions — read this first |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Coding standards, testing expectations, sprint workflow, definition of done |
| [`DEVELOPMENT_GUIDE.md`](DEVELOPMENT_GUIDE.md) | Development workflow, roles, sprint lifecycle, long-term roadmap |
| [`ROADMAP.md`](ROADMAP.md) | Sprint history, upcoming sprints, technical debt |
| [`MISSION.md`](MISSION.md) | The purpose and values behind Marcos OS |
| [`CHANGELOG.md`](CHANGELOG.md) | Version history |

---

## Quick Start

```bash
cd apps/marcos-core
python main.py
```

Runs the Daily Executive Cycle: loads the knowledge vault, runs all executives, generates a Morning Brief, and prints it to the console.

---

## Architecture Overview

```
Knowledge Layer (obsidian/)
    → Context Layer (ContextEngine + ContextProfileBuilder)
        → Capture Layer (CapturePipeline + CaptureRouter)
            → Memory Layer (MemoryStore + DraftMemory)
                → Executive Layer (8 domain executives)
                    → Recommendation Layer
                        → Output Layer (Morning Brief)
```

All layers are orchestrated by `DailyExecutiveCycle` in `apps/marcos-core/`.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full system design.

---

## Running Tests

```bash
cd apps/marcos-core
python tests/test_daily_cycle.py
python tests/test_executive_engine.py
python tests/test_event_bus.py
python tests/test_morning_brief.py
python tests/test_capture_pipeline.py
python tests/test_memory_commit_service.py
python tests/test_memory_store.py
python tests/test_context_profiles.py
```

No test runner required. Each file is self-contained.

---

## Current Capabilities

- Loads and indexes the full Obsidian knowledge vault
- Runs 8 domain executives (1 active, 7 structural stubs)
- Marriage Executive produces 3 rule-based recommendations
- Generates a formatted Morning Brief to the console
- Captures raw text and classifies it into typed memory buckets
- Commits captures as Draft memory objects pending review
- Publishes and subscribes to system events via a synchronous Event Bus
- Executes the full pipeline in a single `DailyExecutiveCycle.run()` call

## What Is Not Yet Built

- PostgreSQL persistence (Sprint 011)
- AI-generated recommendations via OpenRouter (Sprint 012)
- Telegram delivery (Sprint 013)
- Home Assistant integration
- Voice capture
- Web dashboard
