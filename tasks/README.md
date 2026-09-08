# Task Files — Shared Agent State

Part of the [Autonomous Agent Protocol](../docs/AUTONOMOUS_AGENT_PROTOCOL.md).

Each file in this directory is one task: the shared, structured state that
lets the Chairman, Architect, Researcher, Builder, Reviewer, Tester, and
(eventually) Orchestrator hand work to each other through GitHub instead of
through a relayed conversation. See `docs/AGENT_ROLES.md` for role
definitions and `docs/CHECKPOINTS.md` for what happens at a checkpoint.

Filename convention: `TASK-<0000>-<slug>.yaml`, e.g.
`TASK-0001-autonomous-agent-protocol-bootstrap.yaml`. Task IDs are a single
global sequence, independent of the dashboard/API track's sprint numbers.

## Schema

See [`TEMPLATE.yaml`](TEMPLATE.yaml) for the literal, commented schema. Field
summary:

| Field | Type | Meaning |
|---|---|---|
| `task_id` | string | Unique ID, matches the filename. |
| `objective` | string | One or two sentences: what this task accomplishes and why. |
| `status` | enum | Current lifecycle state — see below. |
| `assigned_agent` | enum | Which role currently owns the task: `Chairman`, `Architect`, `Researcher`, `Builder`, `Reviewer`, `Tester`, `Orchestrator`, or `Human`. |
| `priority` | enum | `P0`–`P3`, matching `TODO.md`'s scale. |
| `requirements` | list | Concrete, checkable requirements (not prose). |
| `architecture_reference` | string/list | Pointers to the relevant spec(s): `ARCHITECTURE.md` section, `specs/*.md`, or an inline plan from the Architect. |
| `files_changed` | list | Populated by the Builder as work happens. |
| `tests` | list | Test commands run and their result, populated by the Tester. |
| `blockers` | list | Anything currently preventing progress; empty when unblocked. |
| `decisions` | list | Pointers to `docs/DECISIONS.md` entries made or needed for this task. |
| `checkpoint` | object | `branch`, `commit`, `pushed`, `validated`, `build_state_updated`, `changelog_updated`. |
| `human_required` | boolean | Whether the task is currently paused for a human. |
| `human_action` | object/null | Present only when `human_required: true` — see the Human Interruption Protocol schema in `AUTONOMOUS_AGENT_PROTOCOL.md` §8. |
| `next_agent` | enum/null | Who should act next; `null` only when `status: COMPLETED` or `CANCELLED`. |
| `timestamps` | object | `created`, `updated`, `started`, `completed` — ISO 8601 UTC. |

## Lifecycle

```
PROPOSED → READY → RESEARCHING → ARCHITECTED → BUILDING → TESTING
    → REVIEWING → CHECKPOINT → COMPLETED
```

| State | Owning agent | Entered when | Exits to |
|---|---|---|---|
| `PROPOSED` | Chairman | An objective is drafted but not yet approved. | `READY` (approved) or `CANCELLED` (rejected). |
| `READY` | Orchestrator / Architect | Chairman approves the objective. | `RESEARCHING` if investigation is needed, else `ARCHITECTED`. |
| `RESEARCHING` | Researcher | Investigation begins. | `ARCHITECTED`. |
| `ARCHITECTED` | Architect | A concrete implementation plan exists. | `BUILDING`. |
| `BUILDING` | Builder | Implementation begins. | `TESTING`. |
| `TESTING` | Tester | Implementation is verified. | `REVIEWING` (pass) or `TEST_FAILED` (fail). |
| `TEST_FAILED` | Builder | Tester found a failure. | `TROUBLESHOOTING`. |
| `TROUBLESHOOTING` | Builder | Root-causing and fixing the failure. | `TESTING` (re-verify). |
| `REVIEWING` | Reviewer | Tests pass; adversarial review begins. | `CHECKPOINT` (pass) or `REVIEW_FAILED` (fail). |
| `REVIEW_FAILED` | Builder | Reviewer found a problem. | `BUILDING` (fix, then re-flow through Testing/Reviewing). |
| `CHECKPOINT` | Builder | Review passes; the 9-step checkpoint procedure runs. | `COMPLETED`, or the next task state if the checkpoint reveals more work remains. |
| `BLOCKED` | whoever is assigned | Progress halted by something outside that agent's authority (a dependency, missing info) that is not yet a human ask. | `HUMAN_REQUIRED` if it can't resolve itself, or back to the prior state once unblocked. |
| `HUMAN_REQUIRED` | Human | A destructive/irreversible action, interactive auth, ambiguous spec, or genuine decision is needed. | Resumes in the state it paused from once `resume_condition` is met. |
| `COMPLETED` | — | Checkpoint finished, `human_required: false`. | Terminal. |
| `CANCELLED` | — | Chairman cancels before completion. | Terminal. |

Any state may transition to `BLOCKED` or `HUMAN_REQUIRED`; both always
record which state to resume into.

## Rules

- One task file owns one unit of work with one acceptance criteria set —
  matching the existing "one feature at a time" Builder rule in
  `docs/ENGINEERING_RULES.md`.
- Only the agent named in `assigned_agent` writes to the task file at a
  given moment; handoff happens by updating `assigned_agent`/`next_agent`
  and committing.
- `human_required` and `human_action` are the *only* fields a human is
  expected to read routinely. Everything else is agent-to-agent detail.
- Task files are never deleted after completion — they are the audit trail.
