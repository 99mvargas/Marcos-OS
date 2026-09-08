# BUILD_STATE

The authoritative, protocol-defined snapshot of Marcos OS implementation
state. Updated at every checkpoint per
[`docs/CHECKPOINTS.md`](docs/CHECKPOINTS.md). This is what ChatGPT (Chairman)
reads to know exactly where Claude Code (Builder) stopped, without a copied
conversation.

For the pre-protocol dashboard/API sprint track's narrative state, see
`PROJECT_STATE.md` and `HANDOFF.md` — see `docs/DECISIONS.md#DEC-002` for why
both currently exist.

---

## Protocol Status

- **Autonomous Agent Protocol:** v1.0 adopted (documentation/architecture
  milestone, TASK-0001). Orchestration (n8n as Orchestrator) is now fully
  **designed** (`docs/RUNTIME_ARCHITECTURE.md`, TASK-0002) but still **not
  implemented** — no Postgres, n8n workflow, or headless Claude Code
  invocation exists yet. Implementation is sequenced as TASK-0003 through
  TASK-0007 (see `docs/RUNTIME_ARCHITECTURE.md` §22), each requiring
  separate Chairman approval before starting.
- **Active tasks:** see `tasks/*.yaml`.

## Current Task

- **ID:** `TASK-0002-autonomous-agent-runtime`
- **Status:** `COMPLETED`
- **Assigned agent:** Builder (Claude Code)
- **Objective:** Design the practical, secure, resumable runtime
  architecture (PostgreSQL + n8n + Claude Code + OpenAI API) that makes the
  Autonomous Agent Protocol v1.0 operable. Research/architecture only — no
  runtime, database, n8n workflow, or infrastructure implemented.
- **Human action required:** No.
- **Next agent:** Chairman (review the proposal and the three open
  decisions, DEC-006 through DEC-008).

## Previous Task

- **ID:** `TASK-0001-autonomous-agent-protocol-bootstrap`
- **Status:** `COMPLETED` — see
  `checkpoint/TASK-0001-autonomous-agent-protocol-v1`.

## What Changed This Checkpoint

- Added `docs/RUNTIME_ARCHITECTURE.md` — the full TASK-0002 runtime
  architecture proposal (current-state assessment, target architecture,
  PostgreSQL data model, GitHub/n8n/Claude Code/OpenAI responsibility
  split, MCP architecture, auth model, lifecycle, retry/failure recovery,
  HUMAN_REQUIRED mechanism, security model, deployment, implementation
  sequence, rejected alternatives, cost, and risks).
- Added `tasks/TASK-0002-autonomous-agent-runtime.yaml`.
- Recorded `docs/DECISIONS.md#DEC-006` (PostgreSQL as the live-state
  store), `#DEC-007` (n8n as deterministic Orchestrator; Architect/
  Chairman-assist as unattended OpenAI API calls, not a synchronous
  ChatGPT app session), and `#DEC-008` (defer multi-provider abstraction,
  no second n8n instance for v1) — all `proposed`, awaiting Chairman
  approval.
- Updated `CHANGELOG.md`.
- No application code, infrastructure, Docker, n8n, Home Assistant,
  Proxmox, networking, or credentials were touched. (The working tree
  separately has local, uncommitted changes under `docker/jellyfin-*/`
  from the running Jellyfin container's own runtime state files —
  unrelated to this checkpoint and intentionally left uncommitted.)

## Repository Architecture Snapshot

_Unchanged by this milestone — carried forward from `PROJECT_STATE.md` /
`.context/current.md` for continuity. Regenerate this section at the next
checkpoint that touches application code._

- `apps/marcos-dashboard/` — React 19 + Vite SPA, mock-data driven, active
  development track.
- `apps/marcos-api/` — FastAPI backend, JSON-file storage, not wired to the
  dashboard yet.
- `apps/marcos-core/` — earlier-phase Python executive/memory engine,
  untouched, unrelated to marcos-api.
- `docker/` — Portainer + Jellyfin via Docker Compose. Home Assistant is
  external, not containerized here.
- `.claude/` — Claude Code engineering platform (agents, skills, commands,
  workflows).
- `.engineering/` — script-generated engineering-state cache for
  session-startup token efficiency (separate from `tasks/`).

## Outstanding Decisions (carried forward, not resolved by this milestone)

- Statement Parser real extraction approach (PDF parsing method) — owner:
  Chief Systems Architect. Detail in `NEXT_TASK.md`. Unaffected by this
  protocol milestone.

## Next Action

Await Chairman review of the TASK-0002 runtime architecture proposal and a
decision on `DEC-006`–`DEC-008` (PostgreSQL as live-state store, n8n as
deterministic Orchestrator with API-backed Architect/Chairman-assist, and
deferring multi-provider support). No implementation task (`TASK-0003`
onward, per `docs/RUNTIME_ARCHITECTURE.md` §22) begins until approved
(`status: READY`) individually — per this task's scope, the Google
Calendar assistant work remains deferred to a future task.

---

_Last updated: 2026-09-08 by Claude Code (Builder), checkpoint
`checkpoint/TASK-0002-autonomous-agent-runtime-v1`._
