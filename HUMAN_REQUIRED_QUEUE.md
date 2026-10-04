# Human Required Queue

Pre-Postgres durable equivalent of the `human_required_queue` table
(`database/migrations/0004_create_human_required_queue.sql`,
`docs/RUNTIME_ARCHITECTURE.md` §6). The `marcos-tasks-db` container is not
yet running (see entry #1 below, which is itself the reason), so this file
is the structured record Marcos/Chairman read instead of querying Postgres.
Once the database is live, open entries here are imported as real
`human_required_queue` rows and this file's open section is cleared to a
pointer ("see Postgres") — this file does not become a second live store.

Per `docs/AUTONOMOUS_AGENT_PROTOCOL.md` §8, only `reason`, `risk`, and
`action_required` are routine reading for Marcos; everything else is
agent-to-agent detail kept for audit.

---

## Open

### #1 — Start the `marcos-tasks-db` Postgres container

- **task_id:** TASK-0004-headless-worker-contract (blocks live use by
  TASK-0005's Orchestrator; does not block TASK-0004 itself, which was
  completed and validated against an ephemeral, throwaway Postgres
  container per the same pattern TASK-0003 used)
- **reason:** `INFRASTRUCTURE_CHANGE`
- **risk:** LOW
- **action_required:** Approve starting the `marcos-tasks-db` service
  already defined in `docker/docker-compose.marcos-os.yml` (new, isolated
  container + named volume, localhost-only port; no code change required —
  the service definition has existed since TASK-0003). This is a Docker
  infrastructure change, which `docs/AUTONOMOUS_AGENT_PROTOCOL.md` §10
  classifies as `HUMAN APPROVAL`, not `AUTONOMOUS`/`CHECKPOINT`, regardless
  of how validated the schema/access layer are.
- **safe_to_pause:** true — nothing is left mid-operation; the system
  continues validating all runtime code against ephemeral containers until
  this is approved.
- **resume_condition:** Marcos (or the Chairman, with Marcos's sign-off)
  approves starting the container, e.g. `docker compose -f
  docker-compose.marcos-os.yml --env-file .env up -d marcos-tasks-db` is run
  and confirmed healthy. TASK-0005's Orchestrator can then be pointed at the
  live instance instead of an ephemeral one for its own end-to-end dry run.
- **raised_at:** 2026-10-04
- **resolved_at:** —

### #2 — Authorize one real, low-risk Builder-role headless dry run

- **task_id:** TASK-0004-headless-worker-contract
- **reason:** `ARCHITECTURE_DECISION`
- **risk:** LOW
- **action_required:** `docs/RUNTIME_ARCHITECTURE.md` §22 calls for the
  headless invocation contract to be "exercised manually first ... against
  one real, low-risk task" before TASK-0005 wires an Orchestrator to it.
  Researcher-role invocations (read-only; cannot write regardless of model
  intent, tool-allowlist verified) were exercised for real during this
  checkpoint — see TASK-0004's `tests`. A Builder-role invocation (file
  edits enabled via `acceptEdits`) was deliberately **not** exercised for
  real against this repository during this autonomous session, to avoid an
  unattended process making real edits without a human choosing the task it
  edits. Approve a specific, scoped, low-risk real task for the first
  Builder-role headless dry run (e.g. a small doc fix in a throwaway
  branch), or confirm the Builder-profile write-path smoke test already run
  against the isolated scratchpad directory (not this repository) is
  sufficient evidence to proceed.
- **safe_to_pause:** true.
- **resume_condition:** Marcos names a task (or approves proceeding on the
  scratchpad evidence alone) and the dry run is run and recorded.
- **raised_at:** 2026-10-04
- **resolved_at:** —

---

## Resolved

_(none yet)_
