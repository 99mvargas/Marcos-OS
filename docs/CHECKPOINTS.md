# Checkpoints — Autonomous Agent Protocol v1.0

Part of [`AUTONOMOUS_AGENT_PROTOCOL.md`](AUTONOMOUS_AGENT_PROTOCOL.md).

## What Is a Checkpoint

A checkpoint is the unit of durable, auditable progress in Marcos OS. A task
reaches `CHECKPOINT` status only after the Reviewer and Tester have both
signed off (or their failure loops have resolved). A checkpoint is what
makes a piece of work visible and resumable from GitHub alone — without
anyone needing to relay a Claude Code conversation to ChatGPT.

## The Checkpoint Procedure

Every checkpoint performs these nine steps, in order:

1. **Validate the work** — confirm it matches the task's `requirements` and
   `architecture_reference`; no unscoped changes crept in.
2. **Run appropriate tests** — the project's real test suite/build, not a
   static read of the diff.
3. **Update `BUILD_STATE.md`** — the authoritative snapshot (see
   `BUILD_STATE.md` for the required format).
4. **Update `CHANGELOG.md`** — one entry describing what changed and why.
5. **Record important architectural decisions** in `docs/DECISIONS.md`, if
   any were made or newly confirmed during the task.
6. **Commit changes** — one commit (or a small, logically-scoped set) with a
   message describing why, not just what.
7. **Push the checkpoint branch to GitHub.**
8. **Clearly identify whether human action is required** — set the task
   file's `human_required` and, if `true`, `human_action`
   (see `AUTONOMOUS_AGENT_PROTOCOL.md` §8).
9. **Identify the exact next state** — `COMPLETED` if the task is done, or
   the specific state and `next_agent` for what comes next.

A checkpoint that skips any of these steps is incomplete — the task stays in
`CHECKPOINT` status until all nine are done.

## Branch and Commit Conventions

- **Work branches:** `agent/<role>/<task_id>-<slug>`
  e.g. `agent/builder/TASK-0007-statement-parser`
- **Checkpoint branches:** `checkpoint/<task_id>-<slug>`
  e.g. `checkpoint/TASK-0007-statement-parser-v1`
- Checkpoint branches are pushed to `origin`; they are never merged into
  `main` by an agent. Merging `main` forward is a separate, explicitly
  authorized action by the Chairman/Repository Owner.
- Commit messages follow the existing repository convention: a short
  summary line, then the why, not a restatement of the diff.
- A task may produce more than one checkpoint (e.g. a large task
  checkpoints incrementally); each checkpoint branch is named uniquely
  (append `-v2`, `-v3`, ... or a date suffix if the same task checkpoints
  again).

## How ChatGPT Reads State From GitHub

Given only a repository URL and branch name, the Chairman/Architect can
reconstruct exactly where a task stands by reading, in order:

1. `BUILD_STATE.md` — what's true right now, across all tasks.
2. `tasks/<task_id>.yaml` — this task's full status, blockers, decisions,
   `human_required`, and `next_agent`.
3. `CHANGELOG.md` — what changed, in what order.
4. `docs/DECISIONS.md` — any architectural decisions made along the way.
5. The checkpoint branch's diff — the actual change, if detail is needed.

No conversation transcript is required at any point in this chain.

## Relationship to `PROJECT_STATE.md` / `HANDOFF.md`

The existing dashboard/API sprint track continues to use `PROJECT_STATE.md`,
`HANDOFF.md`, and `NEXT_TASK.md` in their current narrative style until it
is migrated onto this protocol. New protocol-governed tasks use
`BUILD_STATE.md` and `tasks/*.yaml` as described here. See
`docs/DECISIONS.md` for this consolidation decision.
