# Changelog

## Unreleased

* Implemented the Autonomous Agent Runtime's operational state store
  (TASK-0003) — five PostgreSQL tables (`tasks`, `task_events`,
  `agent_invocations`, `human_required_queue`, `checkpoints`) as
  forward-only SQL migrations plus a thin `psycopg` access layer, with
  AI invocation token/cost observability (`docs/TOKEN_EFFICIENCY.md`) as
  a first-class requirement. Validated end-to-end against an ephemeral
  throwaway Postgres container. The `marcos-tasks-db` Docker service is
  defined but intentionally **not started** — that's an infrastructure
  change requiring human approval, not part of this checkpoint. No n8n
  Orchestrator or Claude/OpenAI invocation implemented yet. See
  `database/`, `apps/marcos-api/app/db/`, `docs/TOKEN_EFFICIENCY.md`,
  `tasks/TASK-0003-runtime-state-store.yaml`.
* Proposed the Autonomous Agent Runtime architecture (TASK-0002,
  research/architecture milestone) — the concrete PostgreSQL + n8n + Claude
  Code + OpenAI API design that would make the Autonomous Agent Protocol
  v1.0 operable, including the data model, invocation/security model, and
  implementation sequence. Nothing described is implemented; no n8n,
  Docker, database, or infrastructure changes were made. Awaiting Chairman
  review. See `docs/RUNTIME_ARCHITECTURE.md`,
  `tasks/TASK-0002-autonomous-agent-runtime.yaml`.
* Adopted the Autonomous Agent Protocol v1.0 (documentation/architecture
  milestone) — formal agent roles, shared YAML task-state schema, checkpoint
  system, git branching workflow, and human-interruption protocol. No
  application code, infrastructure, or orchestration changed. See
  `docs/AUTONOMOUS_AGENT_PROTOCOL.md`, `docs/AGENT_ROLES.md`,
  `docs/CHECKPOINTS.md`, `docs/DECISIONS.md`, `BUILD_STATE.md`, `tasks/`.

## v0.1.0

* Repository initialized
