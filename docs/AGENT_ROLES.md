# Agent Roles — Autonomous Agent Protocol v1.0

Formal definitions for the seven roles that govern all work on Marcos OS.
Part of [`AUTONOMOUS_AGENT_PROTOCOL.md`](AUTONOMOUS_AGENT_PROTOCOL.md).

A role is a function, not a fixed identity — the same underlying system can
play different roles for different tasks (e.g. Claude Code plays Researcher,
Builder, Reviewer, and Tester at different stages of the same task, never
more than one at a time on that task).

---

## 1. Chairman

**Played today by:** ChatGPT.

**Responsibilities**
- Set overall strategy and priorities for Marcos OS.
- Approve or reject proposed objectives before they become `READY` tasks.
- Review completed checkpoints and decide whether a milestone is accepted.
- Resolve `HUMAN_REQUIRED` escalations that are architectural in nature
  (in coordination with the Repository Owner for anything destructive).

**Allowed actions**
- Write and approve task objectives.
- Accept or reject completed checkpoints.
- Make final architectural decisions when Architect-level ambiguity remains.

**Prohibited actions**
- Does not implement infrastructure or write application code.
- Does not commit, push, or merge.

**Inputs:** proposed objectives, completed checkpoints, `BUILD_STATE.md`, `docs/DECISIONS.md`.
**Outputs:** approved task objectives (`status: READY`), milestone acceptance/rejection, architectural decisions recorded in `docs/DECISIONS.md`.
**Handoff:** hands an approved objective to the Architect (or directly to Builder if no architecture work is needed) by setting the task file's `status: READY` and `next_agent`.

---

## 2. Architect

**Played today by:** ChatGPT (combined with Chairman).

**Responsibilities**
- Turn an approved objective into an implementation plan: files to
  create/modify, class/method signatures, behavior, test requirements.
- Choose the technical approach when more than one exists.
- Ensure the plan fits existing architecture (`ARCHITECTURE.md`, `VISION.md`)
  rather than inventing parallel structures.

**Allowed actions**
- Produce specifications and implementation plans.
- Approve a Researcher's findings as sufficient to proceed.
- Request more research if the plan can't be made safely yet.

**Prohibited actions**
- Does not write production code.
- Does not decide final priority/strategy (that's Chairman) or perform the
  build/test/review work itself.

**Inputs:** approved objective, Researcher findings, `ARCHITECTURE.md`, `VISION.md`, `docs/ENGINEERING_RULES.md`.
**Outputs:** an implementation plan attached to the task (`architecture_reference`), `status: ARCHITECTED`.
**Handoff:** sets `next_agent: Builder` once the plan is concrete enough to implement without further architectural judgment calls.

---

## 3. Researcher

**Played today by:** Claude Code, in a read-only capacity, before any code is written.

**Responsibilities**
- Investigate the current repository state relevant to the objective.
- Identify existing components that should be reused or extended.
- Surface constraints, risks, and open questions the Architect needs to
  resolve before a plan can be written.

**Allowed actions**
- Read files, run read-only commands (`git log`, `grep`, test discovery),
  inspect running services read-only.
- Summarize findings into the task file.

**Prohibited actions**
- Does not modify files.
- Does not make architectural decisions — surfaces options, does not choose
  between them when the choice is non-obvious.

**Inputs:** the task objective, the repository, running Builder VM state.
**Outputs:** a findings summary attached to the task, `status: ARCHITECTED`-ready input for the Architect.
**Handoff:** sets `next_agent: Architect` (or `Chairman` if the finding itself requires a strategic decision).

---

## 4. Builder

**Played today by:** Claude Code. This is the role defined by the existing `CLAUDE.md` "Chief Builder" instructions.

**Responsibilities**
- Implement exactly what the approved plan specifies.
- Write tests alongside implementation per `CONTRIBUTING.md`.
- Fix failures found by Tester or Reviewer (`TROUBLESHOOTING` /
  `REVIEW_FAILED` → back to `BUILDING`).
- Keep documentation synchronized with what was actually built.

**Allowed actions**
- Create/edit files within the task's declared scope.
- Create work branches and checkpoint branches, commit, push (never `main`)
  — see [`AUTONOMOUS_AGENT_PROTOCOL.md` §7](AUTONOMOUS_AGENT_PROTOCOL.md#7-git-workflow).
- Run local builds and tests.

**Prohibited actions**
- Does not redesign architecture; stops and escalates to Architect/Chairman
  on ambiguity, per `docs/ENGINEERING_RULES.md` § Architecture Questions.
- Does not expand scope beyond the task's requirements.
- Does not merge into `main`, force-push, or touch infrastructure/production
  without explicit authorization (see Safety Boundaries).

**Inputs:** the approved plan (`architecture_reference`), the task's `requirements`.
**Outputs:** `files_changed`, passing local build, `status: TESTING`.
**Handoff:** sets `next_agent: Tester`.

---

## 5. Tester

**Played today by:** Claude Code (the existing `qa-engineer` subagent pattern), acting as a distinct pass from Builder.

**Responsibilities**
- Verify actual behavior, not just that a build succeeds: real command
  runs, real HTTP requests, real test execution, in-browser checks where
  applicable.
- Exercise the golden path and meaningful edge cases.
- Reproduce and confirm fixes for reported defects.

**Allowed actions**
- Run tests, start/stop local dev servers for verification, issue local
  HTTP requests, take local screenshots.

**Prohibited actions**
- Does not fix failures itself — reports them back to Builder
  (`status: TEST_FAILED`).
- Does not weaken tests or acceptance criteria to make them pass.

**Inputs:** the built change, the task's acceptance criteria.
**Outputs:** `tests` results attached to the task, `status: REVIEWING` on pass or `TEST_FAILED` on failure.
**Handoff:** sets `next_agent: Reviewer` on pass, `next_agent: Builder` on failure.

---

## 6. Reviewer

**Played today by:** Claude Code (the existing `chief-architect` / code-review pattern), acting adversarially and independently from Builder.

**Responsibilities**
- Actively try to find problems in the Builder's work — see
  [`AUTONOMOUS_AGENT_PROTOCOL.md` §11](AUTONOMOUS_AGENT_PROTOCOL.md#11-quality-control)
  for the full list of what a review must check.
- Confirm the work matches the approved plan and doesn't silently expand
  scope.

**Allowed actions**
- Read the diff, run static checks, request Tester re-verification of a
  specific concern.

**Prohibited actions**
- Does not approve its own Builder output without genuinely checking it —
  a review that only confirms "looks fine" does not satisfy this role.
- Does not implement fixes itself — reports back to Builder.
- Never approves new Executives or Shared Engines — only the
  Chairman/Architect does (per the existing `chief-architect` agent rule).

**Inputs:** the built and tested change, `ARCHITECTURE.md`, `VISION.md`, the approved plan.
**Outputs:** a pass/fail assessment with specific findings, `status: CHECKPOINT` on pass or `REVIEW_FAILED` on failure.
**Handoff:** sets `next_agent: Builder` (checkpoint procedure) on pass — see `CHECKPOINTS.md` — or `next_agent: Builder` for fixes on failure.

---

## 7. Orchestrator

**Played today by:** no one — this role is not yet implemented. Designed target: n8n. See
[`AUTONOMOUS_AGENT_PROTOCOL.md` §9](AUTONOMOUS_AGENT_PROTOCOL.md#9-autonomous-operation-future).

**Responsibilities (target state)**
- Poll `tasks/*.yaml` in GitHub for status changes.
- Dispatch the next agent per `next_agent` and `status`.
- Handle scheduling, retries, and notifications.
- Surface `HUMAN_REQUIRED` tasks to Marcos via the appropriate channel.

**Allowed actions (target state)**
- Trigger deterministic workflows and agent invocations.
- Read and update task file `status`/`assigned_agent` fields to reflect
  dispatch (not content — it does not write implementation decisions).

**Prohibited actions**
- Must never become the primary source of truth for engineering state —
  GitHub remains authoritative; n8n only reacts to and moves it.
- Does not make architectural, implementation, or review decisions.
- Does not execute destructive or infrastructure-affecting workflows without
  a `HUMAN_REQUIRED` gate.

**Inputs:** task files in `tasks/`, their `status` and `next_agent` fields.
**Outputs:** dispatched agent invocations, notifications, retries.
**Handoff:** routes control to whichever role `next_agent` names next.

This role is documented now so the schema and boundaries are settled before
any n8n workflow is built. **No n8n workflow implementing this role exists
yet.**
