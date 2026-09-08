# Marcos OS Autonomous Agent Protocol v1.0

**Status:** Adopted (documentation/architecture milestone) — orchestration not yet implemented.
**Version:** 1.0
**Date:** 2026-09-08

This document is the authoritative operating protocol for how AI agents and
deterministic systems collaborate to build Marcos OS. It supersedes the
"two-agent, everything-on-main" model described in `DEVELOPMENT_GUIDE.md`
(see [Relationship to Existing Documentation](#relationship-to-existing-documentation)
below). It does not change coding standards — `CONTRIBUTING.md` and
`docs/ENGINEERING_RULES.md` remain in force.

---

## 1. The Problem This Protocol Solves

Marcos should not have to manually copy and paste messages between ChatGPT,
Claude Code, n8n, GitHub, and other agents to keep them synchronized.

Agents communicate through **shared, structured, machine-readable state** —
files in this repository — not through Marcos relaying conversation
transcripts between tools.

Marcos is interrupted only when:

1. A genuine human decision is required.
2. Interactive authentication is required (e.g. OAuth in a browser).
3. A potentially destructive or irreversible action requires approval.
4. The system encounters an ambiguity that cannot safely be resolved
   automatically.

Everything else — routine implementation, testing, documentation updates,
checkpoint commits to non-`main` branches — happens without interrupting him.

---

## 2. Core Systems

| System | Role | Responsibilities |
|---|---|---|
| **ChatGPT** | Chairman / Chief Systems Architect | Defines strategy, makes architectural decisions, reviews completed work, determines major milestones. Does not directly implement infrastructure. |
| **Claude Code** | Chief Builder | Inspects the repository and Builder VM, implements approved technical work, runs tests, troubleshoots, documents changes, commits work, pushes checkpoint branches to GitHub. |
| **n8n** | Operations / Agent Orchestrator | Coordinates workflows and agents, moves structured tasks between agents, executes deterministic workflows, handles triggers/scheduling/integrations/notifications/retries. Must not become the primary source of truth for engineering state. |
| **GitHub** | Engineering source of truth | Code, architecture, specifications, agent instructions, build state, decisions, changelogs, checkpoints, issues/tasks. |
| **PostgreSQL** | Future operational source of truth | Tasks, commitments, routines, state, history, personal-assistant memory. |
| **Home Assistant** | Physical-world state | Home automation and device state. |
| **Obsidian** | Human-readable knowledge | Personal knowledge system, read by Marcos OS, written by Marcos. |

GitHub is the single place ChatGPT can inspect at any time to understand
exactly where Claude Code stopped, without a copied Claude response. See
[`AGENT_ROLES.md`](AGENT_ROLES.md) for formal per-role definitions and
[`BUILD_STATE.md`](../BUILD_STATE.md) for the current snapshot.

---

## 3. First Principles

1. AI agents communicate through shared state, not through Marcos.
2. GitHub is the engineering memory.
3. Structured state is more reliable than conversational transcripts.
4. Agents have narrow responsibilities.
5. AI reasoning proposes; deterministic systems validate and execute.
6. Human attention is reserved for decisions that genuinely require it.
7. No agent should have unnecessary permissions.
8. Every meaningful change must be auditable.
9. The system must be able to resume after interruption.
10. The system must always know its current state.
11. Never build complexity merely because it is technically possible.
12. Optimize for reliability, maintainability, and ROI.

---

## 4. Roles

Seven formal roles govern all work: **Chairman, Architect, Researcher,
Builder, Reviewer, Tester, Orchestrator**. Full responsibilities, allowed
actions, prohibited actions, inputs, outputs, and handoff conditions for each
are defined in [`AGENT_ROLES.md`](AGENT_ROLES.md).

Today, ChatGPT plays Chairman and Architect; Claude Code plays Researcher,
Builder, Reviewer, and Tester (in sequence, per task); n8n is designed to
play Orchestrator once wired up (see [§9](#9-autonomous-operation-future)).
Marcos is the Repository Owner — outside the agent loop, the party who
resolves `HUMAN_REQUIRED` states.

---

## 5. Shared State: The Task File

Agents communicate through task files under [`tasks/`](../tasks/), one YAML
file per task, following the schema in [`tasks/TEMPLATE.yaml`](../tasks/TEMPLATE.yaml).
Every task carries:

```
task_id, objective, status, assigned_agent, priority, requirements,
architecture_reference, files_changed, tests, blockers, decisions,
checkpoint, human_required, human_action, next_agent, timestamps
```

A task file is the durable handoff artifact between roles — an agent picking
up a task reads the file, not a conversation. See `tasks/README.md` for the
full field reference.

### Lifecycle

```
PROPOSED → READY → RESEARCHING → ARCHITECTED → BUILDING → TESTING
    → REVIEWING → CHECKPOINT → COMPLETED
```

Failure / exception paths:

```
TESTING       → TEST_FAILED     → TROUBLESHOOTING → TESTING
REVIEWING     → REVIEW_FAILED   → BUILDING
(any state)   → BLOCKED         → HUMAN_REQUIRED
HUMAN_REQUIRED → (resume_condition met) → the state it paused from
(any pre-BUILDING state) → CANCELLED
```

Full state definitions, entry/exit conditions, and the owning agent per
state are in `tasks/README.md` § Lifecycle.

---

## 6. Checkpoint System

A checkpoint is the unit of durable, auditable progress. Full definition,
the 9-step checkpoint procedure, and branch/commit conventions are in
[`CHECKPOINTS.md`](CHECKPOINTS.md).

In summary, every checkpoint:

1. Validates the work.
2. Runs appropriate tests.
3. Updates `BUILD_STATE.md`.
4. Updates `CHANGELOG.md`.
5. Records important architectural decisions in `docs/DECISIONS.md`.
6. Commits changes.
7. Pushes the checkpoint branch to GitHub.
8. Clearly identifies whether human action is required.
9. Identifies the exact next state.

The goal: ChatGPT can inspect GitHub at any time and know exactly where
Claude Code stopped.

---

## 7. Git Workflow

**Default principle:** Claude Code may autonomously create branches, edit
files, test, commit, and push feature/checkpoint branches. Claude Code does
**not** merge into `main` unless explicitly authorized per merge, by the
Chairman or the Repository Owner.

- Work branches: `agent/<role>/<task_id>-<slug>`
  (e.g. `agent/builder/TASK-0007-statement-parser`)
- Checkpoint branches: `checkpoint/<task_id>-<slug>`
  (e.g. `checkpoint/TASK-0007-statement-parser-v1`)
- Never force-push, never `reset --hard` shared branches, never delete
  branches, never skip hooks — without explicit instruction, per the
  existing Git Safety Protocol.
- `main` only advances via an explicitly authorized merge (PR review by the
  Chairman/Repository Owner). Claude Code may open the PR; it does not merge
  it.

This updates `.claude/agents/git-engineer.md`'s stricter default (see that
file for the exact scoping) and supersedes `DEVELOPMENT_GUIDE.md`'s
"no branches" convention.

---

## 8. Human Interruption Protocol

A task enters `HUMAN_REQUIRED` using this schema (mirrored in the task file's
`human_action` field):

```yaml
status: HUMAN_REQUIRED
reason: GOOGLE_OAUTH
risk: LOW              # LOW | MEDIUM | HIGH
action_required: >
  Authorize Google Calendar in browser.
system_state:
  safe_to_pause: true
resume_condition: >
  OAuth authorization completed.
```

Rules:

- The reason is a short, stable code (e.g. `GOOGLE_OAUTH`,
  `DESTRUCTIVE_ACTION`, `ARCHITECTURE_DECISION`, `AMBIGUOUS_SPEC`), not a
  paragraph — routine detail stays in the task file, not in what's surfaced
  to Marcos.
- `risk` communicates blast radius, not urgency.
- `safe_to_pause: true` means the system is in a stable state and needs no
  time-sensitive action; `false` means something is left mid-operation
  (e.g. a container stopped, a partial migration) and should be flagged as
  such.
- Marcos receives only the reason, risk, and action required — not routine
  implementation details.
- Once `resume_condition` is met, the task resumes in the state it paused
  from (recorded in the task file), not from the beginning.

---

## 9. Autonomous Operation (Future)

This section describes the target end state. **It is not implemented by
this milestone** — no orchestration exists yet; n8n workflows are not
created or modified as part of this document.

```
ChatGPT approves objective
    → GitHub task/specification (tasks/*.yaml, status: READY)
    → n8n orchestrates: picks up READY tasks, assigns next_agent
    → Researcher (Claude Code) investigates → status: ARCHITECTED
    → Architect (ChatGPT) approves implementation plan
    → Builder (Claude Code) implements → status: BUILDING → TESTING
    → Tester (Claude Code) validates
    → Reviewer (Claude Code, adversarial pass) attempts to find failures
    → Builder fixes failures found by Reviewer
    → CHECKPOINT: validate, update BUILD_STATE.md/CHANGELOG.md/DECISIONS.md,
      commit, push checkpoint branch
    → GitHub updated → status: COMPLETED
    → next READY task automatically begins
```

Agents work asynchronously: an agent does not block waiting for another —
it reads the task file's `status` and `assigned_agent`, does its part, writes
its part, and updates `next_agent`. This is what allows n8n to poll GitHub
state and dispatch work without a human relaying messages.

---

## 10. Safety Boundaries

| Category | Examples | Default |
|---|---|---|
| Read-only inspection | Reading files, `git log`, `git status`, listing containers | **AUTONOMOUS** |
| Reversible local changes | Editing files, running tests, local branches, local builds | **AUTONOMOUS** |
| Repository changes (non-`main`) | Commit, push feature/checkpoint branches, open a PR | **AUTONOMOUS** |
| Meaningful milestones | Completing a task's acceptance criteria, a sprint boundary | **CHECKPOINT** |
| Repository changes to `main` | Merging a PR into `main` | **HUMAN APPROVAL** |
| Infrastructure changes | Docker, n8n workflow definitions, Home Assistant config, Proxmox, networking | **HUMAN APPROVAL** |
| Production/runtime changes | Restarting/reconfiguring live containers or services Marcos depends on | **HUMAN APPROVAL** |
| Destructive or irreversible actions | `rm -rf`, `git reset --hard`, force-push, dropping a DB table, deleting a branch | **HUMAN APPROVAL** |
| Sensitive/credentialed actions | OAuth flows, credentials, API keys, secrets | **HUMAN APPROVAL** (interactive auth is always a `HUMAN_REQUIRED` state) |
| External side effects | Sending messages, posting to third-party services, notifications to Marcos | **CHECKPOINT** if part of an approved task's normal output (e.g. a Telegram brief); **HUMAN APPROVAL** if novel or unscoped |

Preference order when a category is ambiguous: **AUTONOMOUS** for
routine/reversible work → **CHECKPOINT** for a meaningful milestone →
**HUMAN APPROVAL** for anything destructive, irreversible, sensitive, or
externally consequential.

---

## 11. Quality Control

The Reviewer role does not rubber-stamp the Builder's work. A review
actively attempts to find:

- Incorrect assumptions in the requirements or the implementation.
- Incomplete requirements — cases the spec didn't cover but the code needed to.
- Security problems (secrets handling, injection, unsafe defaults).
- Regressions in previously working behavior.
- Architectural violations (e.g. an Executive reaching into another's data,
  a Shared Engine being duplicated instead of reused — see `VISION.md`).
- Unnecessary complexity relative to what the task required.
- Documentation gaps — does `BUILD_STATE.md`/`CHANGELOG.md` reflect reality?
- Failure cases — what happens with empty input, missing files, network
  failure, partial state?

The Tester role verifies actual behavior where applicable (real command
runs, real HTTP requests, real test execution) rather than a static read of
the diff — consistent with the existing `qa-engineer` agent's verification
standard.

A task only reaches `CHECKPOINT` after Reviewer and Tester both sign off, or
after a `REVIEW_FAILED`/`TEST_FAILED` loop resolves their findings.

---

## 12. Relationship to Existing Documentation

This protocol is additive and consolidating, not a rewrite:

- `CONTRIBUTING.md` — Python/testing/documentation conventions remain
  unchanged. Its Roles table is extended (not replaced) by
  `AGENT_ROLES.md`'s seven formal roles.
- `docs/ENGINEERING_RULES.md` — the Builder-scope-discipline rules
  (one feature at a time, stop after acceptance criteria, architecture
  questions go to the Chairman) remain in force and are the operating
  detail behind the Builder role defined here.
- `DEVELOPMENT_GUIDE.md` — its "Branch Strategy" section is superseded by
  [§7](#7-git-workflow) above; that section now points here instead of
  describing an all-on-`main` workflow.
- `PROJECT_STATE.md` / `HANDOFF.md` / `NEXT_TASK.md` — remain valid for the
  existing narrative, human-readable session-handoff style used by the
  current dashboard/API sprint track. `BUILD_STATE.md` is the new,
  protocol-defined authoritative snapshot going forward; see
  `docs/DECISIONS.md` for the consolidation decision.
- `.engineering/*.json` and `.context/current.md` — an existing, separate,
  script-generated engineering-state cache scoped to token-efficient
  session startup. It is not replaced by `tasks/`; `tasks/` is the
  cross-agent handoff format, `.engineering/` remains Claude Code's local
  orientation cache.
- `.claude/agents/*.md` — existing Claude Code subagent definitions
  (backend-engineer, frontend-engineer, qa-engineer, git-engineer,
  chief-architect, documentation-engineer, etc.) are the concrete
  implementations Claude Code uses while playing the Builder, Tester, and
  Reviewer roles defined here. They are not redefined by this protocol.

No existing documentation file was deleted or replaced to introduce this
protocol.
