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
  milestone). Orchestration (n8n as Orchestrator) is designed but **not
  implemented**.
- **Active tasks:** see `tasks/*.yaml`.

## Current Task

- **ID:** `TASK-0001-autonomous-agent-protocol-bootstrap`
- **Status:** `CHECKPOINT`
- **Assigned agent:** Builder (Claude Code)
- **Objective:** Design and document the Autonomous Agent Protocol v1.0.
- **Human action required:** No.
- **Next agent:** Chairman (review and accept the milestone).

## What Changed This Checkpoint

- Added `docs/AUTONOMOUS_AGENT_PROTOCOL.md`, `docs/AGENT_ROLES.md`,
  `docs/CHECKPOINTS.md`, `docs/DECISIONS.md`.
- Added `tasks/` (task schema, template, and this milestone's own task
  record).
- Added this file, `BUILD_STATE.md`, as the new authoritative snapshot.
- Updated `CLAUDE.md`, `CONTRIBUTING.md`, `DEVELOPMENT_GUIDE.md`, and
  `.claude/agents/git-engineer.md` to point to / reconcile with the new
  protocol (see `docs/DECISIONS.md` for what changed and why).
- Updated `README.md` documentation table and `CHANGELOG.md`.
- No application code, infrastructure, Docker, n8n, Home Assistant,
  Proxmox, networking, or credentials were touched.

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

Await Chairman review/acceptance of the Autonomous Agent Protocol v1.0
milestone (`TASK-0001`). No further implementation begins until a new task
is approved (`status: READY`) — per this task's scope, the Google Calendar
assistant work is explicitly deferred to a future task.

---

_Last updated: 2026-09-08 by Claude Code (Builder), checkpoint
`checkpoint/TASK-0001-autonomous-agent-protocol-v1`._
