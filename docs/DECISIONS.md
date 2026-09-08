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
