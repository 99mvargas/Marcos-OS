# Marcos OS — Development Guide

This document describes how Marcos OS is developed, who does what, and how work flows from idea to implementation.

---

## The Two-Agent System

Marcos OS is developed using two AI systems with distinct, non-overlapping roles.

### Chief Systems Architect — ChatGPT

ChatGPT designs the system. Responsibilities:

- Define the long-term vision and architecture
- Write sprint specifications
- Make architectural decisions when conflicts arise
- Approve or reject proposed changes to core design
- Define the priority model, lifecycle rules, and integration contracts

ChatGPT does not write code.

### Chief Builder — Claude Code

Claude Code builds the system. Responsibilities:

- Read specifications and implement them exactly
- Create and modify files as directed
- Maintain documentation consistency
- Identify implementation conflicts and report them
- Never redesign without explicit instruction

Claude Code does not make architectural decisions.

### Repository Owner — Marcos Vargas

Marcos directs the work. He decides:

- Which sprint runs next
- Which features matter most
- When to pause, pivot, or accelerate
- What goes into the Obsidian vault

---

## How New Features Are Selected

Features come from one of three sources:

1. **The Roadmap** — ChatGPT has already specified upcoming sprints. These run in order unless Marcos changes priorities.
2. **Marcos's direct request** — Marcos may request a specific capability outside the roadmap.
3. **Architecture evolution** — ChatGPT may redesign a layer when an integration is ready (e.g., replacing `MemoryStore` with PostgreSQL).

Claude Code does not propose features. If it identifies a useful improvement while building, it flags it as technical debt or a future consideration — and waits.

---

## Sprint Lifecycle

### 1. Specification

The Chief Systems Architect writes a sprint specification. A complete spec includes:

- Sprint number and name
- Goal (one sentence)
- Files to create
- Files to modify
- Exact class and method signatures
- Behavior description for each component
- Test requirements
- Documentation update requirements

### 2. Kickoff

Marcos delivers the sprint spec to Claude Code with the instruction:
> "Read the repository before making changes. You are implementing Sprint X of Marcos OS."

Claude Code reads all affected files before writing a single line.

### 3. Implementation

Claude Code implements exactly what the spec describes:

- Creates specified files
- Modifies specified files
- Writes specified tests
- Updates `ROADMAP.md` and `README.md` if instructed

Nothing outside the spec is touched.

### 4. Completion Report

Claude Code delivers:
- Files created
- Files modified
- Key implementation decisions (if any)
- Outstanding issues or conflicts (if any)

Then stops.

### 5. Review

Marcos reviews the output. If corrections are needed, they are issued as direct instructions.
If the sprint is accepted, the next sprint begins.

---

## Technical Debt Process

Technical debt is not resolved speculatively. It is tracked and resolved deliberately.

### Identifying debt

If Claude Code encounters a problem that cannot be fixed within the current sprint's scope, it documents it:

1. Assigns a TD-XXX identifier
2. Adds it to the technical debt table in `ROADMAP.md`
3. Notes whether it is Open or Resolved
4. Continues the sprint

### Resolving debt

Technical debt is resolved when:

- A sprint explicitly targets it, OR
- Resolving it is a prerequisite for the current sprint

Do not resolve debt opportunistically while building something else.

---

## Release Philosophy

Marcos OS does not have traditional releases. It has sprint milestones.

**Current phase: Foundation (v0.1.x)**

The foundation phase focuses on:
- Getting the runtime pipeline fully operational
- Establishing patterns that future integrations will follow
- Building the knowledge base with real personal data
- Testing every layer independently

**Next phase: Intelligence (v0.2.x)**

The intelligence phase begins when OpenRouter is connected and executives produce real AI-generated recommendations.

**Production phase (v1.0.x)**

When PostgreSQL, Telegram, and the full executive team are live. Marcos uses it daily.

There is no release schedule. Sprints advance when Marcos decides to advance them.

---

## Branch Strategy

The repository does not currently use branches.

All work is committed directly to the main branch during the foundation phase.

When the repository has active external integrations (PostgreSQL, Telegram), a branch strategy will be introduced. Until then, the main branch is always the working state.

---

## Long-Term Roadmap

| Sprint | Name | Status |
|---|---|---|
| 001 | Executive Engine | Complete |
| 002 | Memory Layer | Complete |
| 003 | Morning Brief | Complete |
| 004 | Marriage Executive v1 | Complete |
| 005 | Context Profiles | Complete |
| 006 | Capture Pipeline | Complete |
| 007 | Memory Commit Service | Complete |
| 008 | Event Bus | Complete |
| 009 | Daily Executive Cycle | Complete |
| 010 | Finance Executive | Planned |
| 011 | PostgreSQL Integration | Planned |
| 012 | OpenRouter AI Orchestrator | Planned |
| 013 | Telegram Connector | Planned |
| 014 | Home Assistant Integration | Future |
| 015 | Voice Capture | Future |
| 016 | Dashboard | Future |
| 017 | Mobile App | Future |

Sprints 010–013 are specified in `ROADMAP.md`. Sprints 014+ are directional — they will be specified when the preceding integrations are stable.

---

## Repository Maintenance

### Documentation stays current

Every sprint updates:
- `ROADMAP.md` — mark sprint complete, update "Current Sprint"
- `apps/marcos-core/README.md` — add new components, update tables
- `ARCHITECTURE.md` — update if structural patterns changed
- `HANDOFF.md` — update "Completed Sprints" and pending issues

### The Obsidian vault is knowledge, not code

The `obsidian/` folder is Marcos's personal knowledge base. It is structured as Markdown with wikilinks, intended for use in Obsidian. The Python application reads it — it does not write to it.

When personal information changes (new commitments, new goals, life events), the vault is updated directly in Obsidian by Marcos. The Python application picks up the changes automatically on the next run.

### The `specs/` folder grows with the system

As ChatGPT writes specifications for new layers, they are saved in `specs/` before implementation begins. This allows architectural decisions to be reviewed before code is written.

### Secrets and credentials

No credentials, API keys, or tokens are ever committed to the repository. When integrations requiring credentials are added (OpenRouter, Telegram, PostgreSQL), they will be loaded from environment variables or a `.env` file excluded by `.gitignore`.

---

## Running Marcos Core

```bash
cd apps/marcos-core
python main.py
```

This:
1. Loads all Markdown documents from `obsidian/`
2. Runs all 8 executives
3. Generates a Morning Brief
4. Prints the brief to the console
5. Reports execution time

### Running tests

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

Each test file is self-contained and prints `PASS` per test.

No test runner (pytest, unittest discover) is required.

---

## What to Check Before Starting a Sprint

Before writing any code, verify:

1. You have read `CLAUDE.md`
2. You have read the sprint specification completely
3. You have read all files the sprint will modify
4. No conflicts exist between the spec and the current architecture
5. If conflicts exist: stop, report, wait for resolution

This step takes 5 minutes and prevents hours of rework.
