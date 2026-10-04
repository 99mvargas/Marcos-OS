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
  milestone, TASK-0001). The runtime is **designed**
  (`docs/RUNTIME_ARCHITECTURE.md`, TASK-0002), its operational state store
  is **implemented but not deployed** (`database/`, `apps/marcos-api/app/db/`,
  TASK-0003), and the headless worker invocation contract for both Claude
  Code and Codex is **implemented and empirically validated**
  (`apps/marcos-api/app/runtime/`, TASK-0004) — but the `marcos-tasks-db`
  Postgres container has still not been started (infrastructure change
  requiring human approval; see `HUMAN_REQUIRED_QUEUE.md` #1). The
  Orchestrator role is no longer designed as n8n itself — see `DEC-010`,
  which supersedes `DEC-007` with deterministic Python/code polling
  Postgres directly; TASK-0005 implements it next. Implementation is
  sequenced as TASK-0003 through TASK-0007 (see
  `docs/RUNTIME_ARCHITECTURE.md` §22), now directed by the Repository
  Owner directly rather than gated on a separate Chairman approval per
  task (see `DEC-010`'s ownership note).
- **Active tasks:** see `tasks/*.yaml`. **Open human-required items:** see
  `HUMAN_REQUIRED_QUEUE.md`.

## Current Task

- **ID:** `TASK-0005-orchestrator-verifier-watchdog`
- **Status:** `COMPLETED`
- **Assigned agent:** Builder (Claude Code)
- **Objective:** Implement the Orchestrator role as deterministic Python
  code (per `DEC-010`) that claims tasks from Postgres and dispatches
  TASK-0004's headless workers, plus an independent Verifier (secrets/
  scope/real-test checks) and a Watchdog (leases, retry exhaustion, dead
  workers, cost-audit signal). Deliberately stops short of auto-dispatching
  the `CHECKPOINT` step itself against a real repository.
- **Human action required:** No, for this checkpoint's own completion. The
  two items in `HUMAN_REQUIRED_QUEUE.md` from TASK-0004 remain open and
  unaffected by this task.
- **Next agent:** Chairman (review the implementation and decide on the
  two open `HUMAN_REQUIRED_QUEUE.md` items, which gate live use, not this
  checkpoint).

## Previous Tasks

- **ID:** `TASK-0004-headless-worker-contract` — `COMPLETED`, see
  `checkpoint/TASK-0004-headless-worker-contract-v1`.
- **ID:** `TASK-0003-runtime-state-store` — `COMPLETED`, see
  `checkpoint/TASK-0003-runtime-state-store-v1`.
- **ID:** `TASK-0002-autonomous-agent-runtime` — `COMPLETED`, see
  `checkpoint/TASK-0002-autonomous-agent-runtime-v1`.
- **ID:** `TASK-0001-autonomous-agent-protocol-bootstrap` — `COMPLETED`,
  see `checkpoint/TASK-0001-autonomous-agent-protocol-v1`.

## What Changed This Checkpoint

- Added `apps/marcos-api/app/runtime/orchestrator.py` — claims the next
  dispatchable task (`tasks_repo.claim_next_dispatchable_task`, a new
  generalization of TASK-0003's READY-only claim to every state with a
  worker-dispatchable `next_agent`), builds a targeted role prompt from the
  task row's own fields (no repo dump), dispatches the matching
  Claude/Codex worker, records `agent_invocations`/`task_events`, and
  applies the deterministic state-machine transition the result implies.
  `CHECKPOINT` is intentionally excluded from the dispatchable set — a
  human-directed Builder session still performs every real checkpoint.
- Added `apps/marcos-api/app/runtime/verifier.py` — independent,
  non-LLM checks (secret-pattern scan, unintended-changes-vs-declared-scope
  diff, real test-command execution) run before a Builder/Tester result is
  accepted, per `AUTONOMOUS_AGENT_PROTOCOL.md` §11's "don't let the builder
  declare its own work correct."
- Added `apps/marcos-api/app/runtime/watchdog.py` — lease-expiry sweep,
  retry-exhaustion escalation to `HUMAN_REQUIRED` (reason
  `INVOCATION_FAILURE`), dead-invocation detection (a `running` row with no
  completion past a timeout window), and a cost-audit log signal (not an
  auto-pause, per the already-decided `docs/TOKEN_EFFICIENCY.md` scope).
- Validated end-to-end against a real, ephemeral `postgres:16-alpine`
  container (migrated via `database/migrate.py`, torn down immediately
  after): a missing-worktree case correctly raised `HUMAN_REQUIRED`
  (`WORKTREE_MISSING`) rather than crashing; a real Researcher-role `claude
  -p` dispatch correctly transitioned a task `READY → RESEARCHING →
  ARCHITECTED`; the Verifier correctly passed/failed on a trivial
  true/false test command; the Watchdog correctly escalated a
  retry-exhausted task and marked a simulated dead invocation `failed`.
  This run surfaced and fixed a real bug: `WorkerResult.status`
  (success/failure/timeout) was being written directly into
  `agent_invocations.status`, whose CHECK constraint uses a different
  vocabulary (succeeded/failed/timed_out) — fixed with an explicit mapping
  in `orchestrator.py`, re-verified after the fix.
- Updated `CHANGELOG.md`.
- No live Postgres, Docker, network, or production changes (the throwaway
  container and its test worktree/branch were both torn down after
  validation). No secrets committed. Small real API spend during
  validation (one Researcher-role Haiku call) — see this task's `tests`.

## What Changed in the TASK-0004 Checkpoint

- Added `apps/marcos-api/app/runtime/{permissions,worker_result,
  claude_worker,codex_worker}.py` — the headless worker invocation
  contract. `permissions.py` encodes docs/RUNTIME_ARCHITECTURE.md §9's
  per-role tool table for both providers; `worker_result.py` is the typed
  result the Orchestrator/Verifier read instead of prose;
  `claude_worker.py`/`codex_worker.py` shell out to `claude -p`/`codex exec`
  respectively and parse their real (empirically verified, not assumed)
  JSON/JSONL output schemas.
- Verified against the real, installed CLIs (not mocked): a Researcher-role
  Claude invocation correctly read a file and reported back; the same for
  Codex in `read-only` sandbox mode; a Researcher-role Claude invocation
  asked to create a file could not (`Write`/`Edit` were absent from its
  tool allowlist — structurally blocked, not merely declined); a
  Builder-profile (`acceptEdits`, not a full bypass) write succeeded
  cleanly in an isolated scratchpad directory outside this repository; a
  role-clarity fix (`--append-system-prompt`) confirmed a sub-invocation
  correctly identifies its assigned role rather than this repo's default
  `CLAUDE.md` persona.
- Recorded `docs/DECISIONS.md#DEC-010` — the Orchestrator (TASK-0005) is
  deterministic Python polling Postgres, not n8n itself; supersedes
  `DEC-007`. Decided directly by the Repository Owner in the absence of a
  live Chairman session, not left `proposed`.
- Recorded `docs/DECISIONS.md#DEC-011` — headless invocations never emit a
  full permission-bypass flag for either provider; the tool allowlist is
  the enforcement boundary, verified empirically after this repository's
  own auto-mode safety classifier flagged a bypass attempt during testing.
- Added `HUMAN_REQUIRED_QUEUE.md` — the pre-Postgres durable equivalent of
  the `human_required_queue` table, with two open entries (still open).
- Real but small (~$0.35 USD, cheapest/Haiku tier) API spend during
  empirical validation — see `tasks/TASK-0004-headless-worker-contract.yaml`'s `tests`.

## What Changed in the TASK-0003 Checkpoint

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
  captures/finance/statements; **`app/db/` (TASK-0003)** is a separate
  `psycopg`-based access layer for the Autonomous Agent Protocol's runtime
  state store — distinct tables, distinct purpose, not wired into the
  FastAPI routes yet. **`app/runtime/` (TASK-0004 + TASK-0005)** is the
  headless Claude Code/Codex worker invocation contract plus the
  Orchestrator/Verifier/Watchdog that dispatch it — also not wired into
  the FastAPI routes; it is run by calling `orchestrator.run_cycle()`
  directly today (manually, or from a cron/systemd timer a human sets up),
  not by a persistent service.
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
- `DEC-006`, `DEC-008` (TASK-0002's PostgreSQL/multi-provider decisions) —
  still `proposed`, awaiting explicit Chairman approval. `DEC-007`
  (n8n-as-Orchestrator) is superseded by `DEC-010`, not pending approval.

## Next Action

TASK-0003 through TASK-0005 are complete and validated, each against an
ephemeral Postgres container — the runtime has never touched the
persistent `marcos-tasks-db` service. The next continuation is TASK-0006
(Architect/Chairman-assist API service + Telegram notify/resume, per
`docs/RUNTIME_ARCHITECTURE.md` §22 item 4) and/or actually running the
Orchestrator against this repository's own backlog once a human resolves
`HUMAN_REQUIRED_QUEUE.md` #1 (start `marcos-tasks-db`). Two independent
items await a human decision there (#1: start the persistent container;
#2: approve a scoped low-risk task for the first real Builder-role
headless dry run) — neither blocked TASK-0004 or TASK-0005.

---

_Last updated: 2026-10-04 by Claude Code (Builder), checkpoint
`checkpoint/TASK-0005-orchestrator-verifier-watchdog-v1`._
