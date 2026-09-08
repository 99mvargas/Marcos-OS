# Architecture Decisions Log

A durable, append-only record of architectural decisions made under the
[Autonomous Agent Protocol](AUTONOMOUS_AGENT_PROTOCOL.md). Each entry is
written once and never edited after acceptance — corrections are new
entries that supersede an earlier one.

This is distinct from `.engineering/decisions.json`, which is Claude Code's
own hand-maintained, script-consumed engineering-state file scoped to the
current sprint/task on the dashboard track. This file is the durable,
human-and-agent-readable decision record for protocol-level and
cross-cutting architecture decisions.

Format per entry: date, decision, status (`decided` / `deferred` /
`superseded`), owner, rationale.

---

## DEC-001 — Adopt the Autonomous Agent Protocol v1.0

- **Date:** 2026-09-08
- **Status:** decided
- **Owner:** Chairman (ChatGPT), implemented by Chief Builder (Claude Code)
- **Decision:** Marcos OS adopts a formal, seven-role, task-file-based
  protocol (`docs/AUTONOMOUS_AGENT_PROTOCOL.md`) for how ChatGPT, Claude
  Code, n8n, GitHub, PostgreSQL, Home Assistant, and Obsidian collaborate.
- **Rationale:** Marcos was manually relaying messages between agents.
  Structured, shared state in GitHub removes that bottleneck and gives
  every agent a single source of truth for what's done, what's next, and
  what needs a human.

## DEC-002 — Introduce `BUILD_STATE.md` as the new authoritative state snapshot

- **Date:** 2026-09-08
- **Status:** decided
- **Owner:** Chairman, implemented by Chief Builder
- **Decision:** `BUILD_STATE.md` (repository root) is the new authoritative,
  protocol-defined snapshot of implementation state, updated at every
  checkpoint. `PROJECT_STATE.md`, `HANDOFF.md`, and `NEXT_TASK.md` are not
  deleted or rewritten — they remain valid for the existing dashboard/API
  sprint track's narrative handoff style until that track is migrated onto
  this protocol.
- **Rationale:** The existing state docs are narrative and
  session-oriented, aimed at a human/Claude reader picking up the very next
  session. The protocol needs a snapshot that is also legible to an
  orchestrator and to ChatGPT reading only GitHub, with a consistent
  section structure per checkpoint. Rewriting the existing docs in place
  risked corrupting an in-flight decision (the Statement Parser extraction
  approach, tracked in `NEXT_TASK.md`) that this milestone does not
  resolve.

## DEC-003 — Introduce `tasks/` as the shared task-state directory

- **Date:** 2026-09-08
- **Status:** decided
- **Owner:** Chairman, implemented by Chief Builder
- **Decision:** A new top-level `tasks/` directory holds one YAML file per
  task (schema in `tasks/TEMPLATE.yaml`), the shared structured state
  agents read and write. This is a new top-level directory, which
  `CONTRIBUTING.md` requires an explicit architectural decision for — this
  entry is that decision.
- **Rationale:** `.engineering/*.json` already exists but is scoped to a
  single current sprint/task for Claude Code's own session-startup
  efficiency, not a multi-task, multi-agent handoff format. `specs/` holds
  architecture specs, not task/status tracking. Neither fits the
  lifecycle-and-handoff shape this protocol needs.

## DEC-004 — Introduce a Git branching and checkpoint-branch workflow

- **Date:** 2026-09-08
- **Status:** decided (supersedes the branch strategy in `DEVELOPMENT_GUIDE.md`)
- **Owner:** Chairman, implemented by Chief Builder
- **Decision:** Claude Code may autonomously create branches, commit, and
  push feature/checkpoint branches (`agent/<role>/...`,
  `checkpoint/<task_id>-...`), but never merges into `main` without explicit
  authorization. This is a change from the prior "no branches, everything on
  main" convention documented in `DEVELOPMENT_GUIDE.md`.
- **Rationale:** As the system moves toward asynchronous, multi-agent,
  potentially unattended operation, committing directly to `main` removes
  the reviewable checkpoint boundary this protocol depends on. Checkpoint
  branches give ChatGPT and Marcos a stable, inspectable unit of work
  without blocking Claude Code on human availability for routine,
  reversible progress.

## DEC-005 — Claude Code's routine checkpoint commits/pushes are pre-authorized

- **Date:** 2026-09-08
- **Status:** decided
- **Owner:** Chairman, implemented by Chief Builder
- **Decision:** `.claude/agents/git-engineer.md`'s "never commit unless
  explicitly asked" default is scoped down: committing and pushing to
  feature/checkpoint branches (never `main`) as part of completing a
  checkpoint under this protocol does not require a fresh per-commit ask.
  All of that file's other rules (never merge to `main`, never force-push,
  never delete branches, never skip hooks, without explicit instruction)
  remain unchanged.
- **Rationale:** Per-commit confirmation is exactly the manual
  human-in-the-loop step this protocol exists to remove for routine,
  reversible work. The blast radius is bounded because `main` is untouched
  and every checkpoint is independently inspectable and revertable.

## DEC-006 — Introduce PostgreSQL as the live/operational state store, separate from GitHub's durable-record role

- **Date:** 2026-09-08
- **Status:** proposed — awaiting Chairman review
- **Owner:** Builder (Claude Code), proposed for Chairman/Repository Owner
  approval
- **Decision:** Add a small, purpose-built PostgreSQL store (five tables —
  `tasks`, `task_events`, `agent_invocations`, `human_required_queue`,
  `checkpoints`; schema in `docs/RUNTIME_ARCHITECTURE.md` §6) on the
  Builder VM to hold live, frequently-mutated task state for the
  Orchestrator. GitHub's role is unchanged: it remains the durable
  engineering source of truth and the checkpoint-time snapshot.
  `tasks/<id>.yaml` is written only by the Builder, only at a checkpoint,
  always sourced from that task's current Postgres row — it never
  diverges or becomes a second live store.
- **Rationale:** Git/GitHub has no atomic "claim if unclaimed" primitive
  and no row-level lock, which makes it unsafe as a live dispatch queue
  under concurrent/retried triggers; polling GitHub on a tight interval is
  also high-latency and rate-limited. Conflating "durable record" and
  "live, contended operational state" into one store was the central
  structural problem TASK-0002 identified. See
  `docs/RUNTIME_ARCHITECTURE.md` §2, §5, §6.

## DEC-007 — n8n is the deterministic Orchestrator; Architect and Chairman-assist run as unattended OpenAI API calls, not a synchronous ChatGPT app session

- **Date:** 2026-09-08
- **Status:** proposed — awaiting Chairman review
- **Owner:** Builder (Claude Code), proposed for Chairman/Repository Owner
  approval
- **Decision:** n8n polls Postgres, claims tasks atomically, and dispatches
  headless Claude Code invocations (Researcher/Builder/Reviewer/Tester) or
  OpenAI API calls (Architect/Chairman-assist) — it never makes
  architectural or approval decisions itself. The Architect function
  (drafting an implementation plan) runs fully unattended via the OpenAI
  API. The Chairman function (objective approval, milestone acceptance)
  stays human-gated: the API drafts a recommendation, but the actual
  approval is a Telegram one-tap action by Marcos, not an autonomous
  transition.
- **Rationale:** The runtime must operate while Marcos is at work, and the
  consumer ChatGPT app has no unattended API surface n8n can call — a
  synchronous app-in-the-loop design was evaluated and rejected on that
  basis. Objective/milestone approval is exactly the category `VISION.md`
  already reserves for human control, so Chairman-*assist* (API drafts,
  human taps) was chosen over a fully autonomous Chairman. See
  `docs/RUNTIME_ARCHITECTURE.md` §10, §23.

## DEC-008 — Defer multi-AI-provider abstraction; no general agent framework or second n8n instance for v1

- **Date:** 2026-09-08
- **Status:** proposed — awaiting Chairman review
- **Owner:** Builder (Claude Code), proposed for Chairman/Repository Owner
  approval
- **Decision:** The runtime uses Claude Code (Anthropic) for
  Researcher/Builder/Reviewer/Tester and the OpenAI API for
  Architect/Chairman-assist, on the existing single n8n instance, with no
  provider-routing abstraction layer, no general agent framework
  (LangGraph/CrewAI/AutoGPT-style), and no second, isolated n8n instance.
  Revisit only if a future task (earliest candidate: TASK-0007, the first
  fully autonomous dry run) surfaces a concrete need.
- **Rationale:** No measurable requirement today justifies the added
  complexity; the prompt's own "cheapest architecture that reliably
  provides the capability, with a clean upgrade path" constraint applies
  directly. A second n8n instance would isolate this protocol's
  credentials from the existing unrelated "COO" workflows found on the
  live instance, but doubles operational surface for a risk that narrow
  credential scoping already mitigates. See `docs/RUNTIME_ARCHITECTURE.md`
  §19, §22, §23, §26.

## DEC-009 — Implement the runtime state store as plain SQL migrations + a thin psycopg access layer; define but do not start the Postgres container

- **Date:** 2026-09-08
- **Status:** decided
- **Owner:** Builder (Claude Code)
- **Decision:** TASK-0003 implements the five tables from
  `docs/RUNTIME_ARCHITECTURE.md` §6 (`tasks`, `task_events`,
  `agent_invocations`, `human_required_queue`, `checkpoints`) as
  hand-written, forward-only SQL files in `database/migrations/`, applied
  by a ~100-line runner (`database/migrate.py`) with no ORM and no
  migration framework (no Alembic/Flyway). The Python access layer
  (`apps/marcos-api/app/db/`) is plain `psycopg` (v3) with typed Pydantic
  row models, matching this repo's existing `apps/marcos-api` conventions
  rather than introducing a second Python data-access pattern.
  `docker/docker-compose.marcos-os.yml` gains a `marcos-tasks-db` service
  definition (new, isolated container + named volume, localhost-only port)
  as recommended in `docs/RUNTIME_ARCHITECTURE.md` §20 — but per
  `docs/AUTONOMOUS_AGENT_PROTOCOL.md` §10 ("Infrastructure changes... Docker"
  is `HUMAN APPROVAL`, not autonomous), the service is defined as code
  only and was not started as part of this checkpoint. This store is
  narrowly scoped to the Autonomous Agent Protocol's runtime state; it
  does not migrate, replace, or fulfill the separate, pre-existing
  "Sprint 011 PostgreSQL Integration" plan for `apps/marcos-core`'s memory
  system (`ROADMAP.md`, `apps/marcos-core/README.md`) — that remains a
  distinct future task with its own schema and its own decision to make.
- **Rationale:** The schema is small (five tables, no joins beyond a
  shared `task_id` foreign key) and forward-only migrations are simpler to
  reason about than a framework's migration DSL for this size of project —
  consistent with `docs/RUNTIME_ARCHITECTURE.md`'s own "small, no ORM
  framework required" scope for this store and the prompt's "don't add an
  ORM unless clearly justified" instruction. Standing up the actual
  database container is a genuine infrastructure action on the Builder
  VM (a new persistent service, new inbound port, new credential) — the
  protocol's own safety-boundary table puts that in `HUMAN APPROVAL`, not
  `AUTONOMOUS`/`CHECKPOINT`, regardless of how detailed the commissioning
  task was. Migrations and the access layer were instead validated against
  a fully ephemeral, throwaway Postgres container (not part of the
  `docker-compose.marcos-os.yml` stack, torn down immediately after
  validation) — this is "running tests / local builds," which the same
  table marks `AUTONOMOUS`.
