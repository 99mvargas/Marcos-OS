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
  milestone, TASK-0001). The runtime is now fully **designed**
  (`docs/RUNTIME_ARCHITECTURE.md`, TASK-0002) and its operational state
  store is **implemented but not deployed** (`database/`,
  `apps/marcos-api/app/db/`, TASK-0003) — the `marcos-tasks-db` Postgres
  container has not been started (infrastructure change requiring human
  approval, see TASK-0003's `blockers`). No n8n workflow or headless
  Claude Code invocation exists yet. Implementation is sequenced as
  TASK-0003 through TASK-0007 (see `docs/RUNTIME_ARCHITECTURE.md` §22),
  each requiring separate Chairman approval before starting.
- **Active tasks:** see `tasks/*.yaml`.

## Repository Consolidation (First Mission)

A second, independent repository (`~/marcos-os`, unrelated git history, an
earlier infrastructure-control-plane-focused evolution of Marcos OS) was
read-only classified against this canonical repository on 2026-10-04. Two
pre-existing backups of that repository were verified intact
(`~/marcos-os-premerge-backup.bundle`,
`~/marcos-os-workforce-untracked-backup.tar.gz`); nothing in it was
modified. Findings:

- **Migrated:** `AGENTS.md` (Codex operating rules) — committed this
  checkpoint, content unchanged, cross-referenced from `CLAUDE.md` and
  `docs/AUTONOMOUS_AGENT_PROTOCOL.md` §10.
- **Not migrated (obsolete):** its `AGENTS.md`'s host repo also had stub
  `ansible/`/`docker/`/`scripts/` READMEs (no real content) and a
  `workforce/` Python task-store prototype — superseded by this repo's
  Postgres-backed TASK-0003 store; no architecture worth porting.
- **Kept as historical reference only, not adopted as current truth:** its
  `CLAUDE.md` (different product framing), `infrastructure/discovery/`
  network/Proxmox/UniFi snapshots, and `docs/ACTIVE-WORK.md` (95KB
  operational log) — real provenance, but frozen-in-time observations, not
  live state.
- **Outstanding, not yet done:** folding the Verifier/Orchestrator safety
  ideas from its `agents/orchestrator.md` and `agents/verifier.md` (never
  trust a worker's self-reported success; re-check live state; serialize
  work on shared resources) into `docs/AGENT_ROLES.md` and the future
  Verifier implementation; and deciding whether to adopt its `.mcp.json`
  Home Assistant MCP server entry (deferred — requires Marcos's input on
  whether that integration is wanted, not purely a repository-level call).
- Once those two items are resolved, `~/marcos-os` has no remaining unique
  production logic and is safe to archive (not delete).

## Current Task

- **ID:** `TASK-0003-runtime-state-store`
- **Status:** `COMPLETED`
- **Assigned agent:** Builder (Claude Code)
- **Objective:** Implement the PostgreSQL operational state store (five
  tables from `docs/RUNTIME_ARCHITECTURE.md` §6) plus AI invocation
  cost/token observability, as plain SQL migrations and a thin typed
  access layer — the smallest production-quality foundation for the
  runtime designed in TASK-0002. Does not implement the n8n Orchestrator
  or any Claude/OpenAI invocation.
- **Human action required:** No (for this checkpoint). Flagged
  separately: starting the `marcos-tasks-db` Docker container is an
  infrastructure change requiring human approval before TASK-0004/0005
  can run against a live instance — see this task's `blockers`.
- **Next agent:** Chairman (review the implementation and `DEC-009`, and
  decide whether to approve starting `marcos-tasks-db`).

## Previous Tasks

- **ID:** `TASK-0002-autonomous-agent-runtime` — `COMPLETED`, see
  `checkpoint/TASK-0002-autonomous-agent-runtime-v1`.
- **ID:** `TASK-0001-autonomous-agent-protocol-bootstrap` — `COMPLETED`,
  see `checkpoint/TASK-0001-autonomous-agent-protocol-v1`.

## What Changed This Checkpoint

- Added `database/migrations/0001`–`0005` — the five runtime tables
  (`tasks`, `task_events`, `agent_invocations`, `human_required_queue`,
  `checkpoints`) with the atomic-claim index, append-only audit trigger,
  and idempotent-checkpoint unique constraint from
  `docs/RUNTIME_ARCHITECTURE.md` §6.
- Added `database/migrate.py` — a small (~100 line), framework-free
  forward-only migration runner.
- Added `apps/marcos-api/app/db/` — a thin `psycopg`-based access layer
  (typed Pydantic row models, atomic claim, lease sweep, event logging,
  invocation token/cost recording, human-required lifecycle, checkpoint
  idempotency) plus `cost.py`, a static Anthropic pricing table for
  estimating cost per invocation.
- Added `docs/TOKEN_EFFICIENCY.md` — what consumes tokens, what must
  never consume an LLM call, context-minimization and model-selection
  rules, retry limits, required telemetry, and how to audit cost/detect
  waste.
- Added `docker-compose.marcos-os.yml`'s `marcos-tasks-db` service
  definition (new, isolated container + named volume, localhost-only
  port) and `docker/.env.example` variable names — **defined but not
  started**, per `docs/DECISIONS.md#DEC-009`.
- Added `apps/marcos-api/requirements.txt`'s `psycopg[binary]` dependency.
- Recorded `docs/DECISIONS.md#DEC-009` (plain SQL migrations + thin
  access layer, no ORM; Postgres container defined as code but not
  deployed; relationship to the separate future Sprint 011 PostgreSQL
  plan for `apps/marcos-core`).
- Validated migrations and the access layer end-to-end (atomic
  claim/no-double-dispatch, append-only trigger, token/cost math, human-
  required lifecycle, checkpoint idempotency, lease sweep, CHECK
  constraints — 15/15 checks) against a fully ephemeral, throwaway
  Postgres container — not the named `marcos-tasks-db` service, torn
  down immediately after.
- Updated `CHANGELOG.md`.
- No finance, Home Assistant, or existing `apps/marcos-api` application
  data was migrated or touched; no n8n, Proxmox, Home Assistant, or
  network configuration was touched; no credentials were committed. (The
  working tree separately has local, uncommitted changes under
  `docker/jellyfin-*/` from the running Jellyfin container's own runtime
  state files — unrelated to this checkpoint and intentionally left
  uncommitted.)

## Repository Architecture Snapshot

- `apps/marcos-dashboard/` — React 19 + Vite SPA, mock-data driven, active
  development track.
- `apps/marcos-api/` — FastAPI backend, JSON-file storage for
  captures/finance/statements; **`app/db/` (new, TASK-0003)** is a
  separate `psycopg`-based access layer for the Autonomous Agent
  Protocol's runtime state store — distinct tables, distinct purpose,
  not wired into the FastAPI routes yet.
- `apps/marcos-core/` — earlier-phase Python executive/memory engine,
  untouched, unrelated to marcos-api.
- `database/` — **(new, TASK-0003)** the runtime state store's SQL
  migrations and migration runner. Not a general Marcos OS database — see
  `database/README.md`.
- `docker/` — Portainer + Jellyfin + marcos-api/marcos-dashboard via
  Docker Compose, plus the new (not-yet-started) `marcos-tasks-db`
  service. Home Assistant is external, not containerized here.
- `.claude/` — Claude Code engineering platform (agents, skills, commands,
  workflows).
- `.engineering/` — script-generated engineering-state cache for
  session-startup token efficiency (separate from `tasks/`).

## Outstanding Decisions (carried forward, not resolved by this milestone)

- Statement Parser real extraction approach (PDF parsing method) — owner:
  Chief Systems Architect. Detail in `NEXT_TASK.md`. Unaffected by this
  protocol milestone.
- `DEC-006`–`DEC-008` (TASK-0002's PostgreSQL/n8n/multi-provider
  decisions) — still `proposed`, awaiting explicit Chairman approval.

## Next Action

Await Chairman review of the TASK-0003 implementation and `DEC-009`, and
a decision on whether to approve starting the `marcos-tasks-db` Docker
container (infrastructure change, human-approval-gated per
`docs/AUTONOMOUS_AGENT_PROTOCOL.md` §10). TASK-0004 (headless Claude Code
invocation contract) does not begin until approved (`status: READY`).

---

_Last updated: 2026-10-04 by Claude Code (Builder), checkpoint
`checkpoint/repo-consolidation-codex-guardrails-v1` — repository-consolidation
work, parallel to and independent of the TASK-0003/0004 protocol sequence
above, which this checkpoint does not otherwise change. Note for whoever
reconciles branches: TASK-0004 implementation is proceeding concurrently on
`agent/infrastructure/TASK-0004-headless-worker-contract`, branched from the
same `checkpoint/TASK-0003-runtime-state-store-v1` base; both branches touch
`BUILD_STATE.md` and will need a manual merge, not a fast-forward._
