# Token & Cost Efficiency — Autonomous Agent Runtime

Part of the [Autonomous Agent Protocol](AUTONOMOUS_AGENT_PROTOCOL.md) runtime
(TASK-0002 `docs/RUNTIME_ARCHITECTURE.md`, TASK-0003 `database/`). This is
the operating rulebook for keeping every future AI invocation cheap,
observable, and auditable — token/cost efficiency is a first-class
requirement of this runtime, not an afterthought.

---

## What consumes tokens

Only an actual LLM API call (headless Claude Code invocation, or a direct
Anthropic/OpenAI API call) consumes tokens. Concretely, per
`docs/RUNTIME_ARCHITECTURE.md` §9–§10:

- Researcher / Builder / Reviewer / Tester role invocations (Claude Code).
- Architect plan-drafting and Chairman-assist recommendation calls (OpenAI
  API).
- Any future subagent or delegated call spawned inside one of the above.

## What must never consume an LLM call

Deterministic operations are handled by n8n, Postgres, or plain code —
never by asking a model to do work a program can do exactly and cheaply:

- Task claiming, locking, lease/timeout sweeps (`tasks_repo.py` — plain
  SQL, `FOR UPDATE SKIP LOCKED`).
- Status transitions, event logging, checkpoint bookkeeping
  (`task_events`, `checkpoints` tables).
- Cost/token aggregation and pricing math (`app/db/cost.py` — a static
  lookup table, not a model call).
- Retry/backoff scheduling, idempotency-key checks.
- Notification formatting and delivery (Telegram message construction is
  string templating, not generation).
- Git operations (branch creation, commit, push) — mechanical, not
  something an LLM should be asked to "decide" to do correctly.

If a task can be expressed as a SQL query, a template, or an `if`
statement, it does not get an invocation row in `agent_invocations`.

## Context-minimization rules

**Never send full repository context to an agent invocation by default.**
Every invocation must be scoped to what that role, for that task,
actually needs:

1. **Role-scoped tool permissions** (`docs/RUNTIME_ARCHITECTURE.md` §9)
   already bound *what* an invocation can touch; context minimization is
   the same principle applied to *what it's shown*. A Reviewer re-checking
   one file's diff does not need the whole repo tree.
2. **Targeted context selection**: the invocation prompt is built from the
   task row's `requirements`, `architecture_reference`, and
   `files_changed` fields — a curated pointer list, not a directory dump.
   The invoking process (future TASK-0004 wrapper) resolves those pointers
   to file contents at dispatch time, not "read everything and let the
   model figure out what matters."
3. **No repo-wide search inside a single invocation when a targeted lookup
   suffices.** Prefer `grep`/`glob` for a known symbol over an open-ended
   "explore the codebase" instruction.
4. **Sub-invocations get their own scoped context**, not the parent's full
   transcript. A Builder invocation that spawns a narrower check (e.g. "does
   this file already define X") is itself a candidate for a cheaper model
   (see Model-selection rules) with only the relevant file(s) in context.
5. **Prompt caching** (per the `claude-api` skill's caching guidance)
   applies once headless invocations exist (TASK-0004): stable system
   prompts and role instructions go first and are cached; volatile,
   per-task content goes last.

## Model-selection rules

Model choice is a per-invocation decision, not a global constant:

- **Default to the lowest-cost model capable of the task.** Deterministic
  extraction, classification, or short well-specified edits do not need
  the most expensive model available; open-ended design/architecture work
  does.
- **Roles map to a starting tier, not a fixed model**: Researcher/Tester
  (read + report) and narrow Builder edits can usually run on a
  cheaper/faster model; Architect and adversarial Reviewer passes — where
  a missed defect is expensive to catch later — justify a stronger model.
- **The mapping lives in code, not in this document**, so it can change
  without a doc edit — but every invocation must record which model it
  used (`agent_invocations.model`) so the mapping's actual cost impact is
  auditable after the fact (see Auditing below).
- **Escalate on failure, don't default to the top tier.** A `TEST_FAILED`
  → `TROUBLESHOOTING` retry is a reasonable trigger to step up model
  tier; routine first-pass work is not.

## Retry limits

Per `docs/RUNTIME_ARCHITECTURE.md` §14: capped at **3 attempts per
invocation**, exponential backoff (1m, 5m, 15m). The 4th failure sets
`human_required` (`reason: INVOCATION_FAILURE`) rather than retrying
indefinitely. This bounds both wasted tokens and wasted wall-clock time on
a bad task. `agent_invocations.retry_count` is the audit trail for how
often this actually fires — a task that burns all 3 retries repeatedly is
a signal the task itself is mis-scoped, not that the retry budget should
be raised.

## Token/cost budgets

No hard per-task dollar cap is enforced by this runtime yet (that would
require killing an in-flight invocation mid-run, which is out of scope
for TASK-0003). Instead:

- Every invocation's `estimated_cost_usd` is recorded before the task can
  reach `CHECKPOINT` (see Required telemetry).
- `docs/RUNTIME_ARCHITECTURE.md` §25 estimates single-operator load at
  "low tens of dollars/month" — a task whose `cost_by_task` total is
  wildly outside that order of magnitude is the practical budget signal
  today, surfaced by the audit query below, not by an automatic cutoff.
- A hard per-task or per-day budget ceiling (auto-pause on breach) is a
  reasonable future task once real usage data exists to calibrate it —
  not invented speculatively here.

## Required telemetry

Every AI invocation must write an `agent_invocations` row
(`database/migrations/0003_create_agent_invocations.sql`) recording, at
minimum:

`invocation_id, task_id, role, provider, model, input_tokens,
output_tokens, total_tokens, estimated_cost_usd, duration_ms, status,
retry_count, started_at/completed_at`

This is enforced by the access layer, not left to caller discipline:
`invocations_repo.start_invocation()` opens the row before dispatch (so a
crashed invocation still has a `running` row, not a silent gap), and
`complete_invocation()` is the only place `estimated_cost_usd` gets
computed — callers pass token counts, not a cost figure, so the pricing
math (`app/db/cost.py`) can't drift between call sites.

## How future agents retrieve only relevant context

1. Read the task row's `requirements` / `architecture_reference` /
   `files_changed` fields — these are the pointer list, curated at
   `ARCHITECTED` time by the Architect, not assembled ad hoc per
   invocation.
2. Resolve pointers to content immediately before dispatch (future
   TASK-0004 invocation wrapper), not speculatively earlier.
3. Use `grep`/`glob`-equivalent targeted lookups for anything not already
   pointed to, rather than a broad directory read.
4. MCP tool access is granted per-role and per-invocation
   (`docs/RUNTIME_ARCHITECTURE.md` §11) — a Researcher gets read-only
   scoped access, never a standing grant to unrelated systems (e.g. the
   live n8n instance's unrelated "COO" workflows) "just in case."

## How we calculate and audit cost per task

- `app/db/cost.py::estimate_cost_usd(provider, model, input_tokens,
  output_tokens)` — a static per-model pricing table (verified against
  Anthropic's published rate card as of `PRICING_VERIFIED_AT` in that
  file; OpenAI rows are explicit unverified placeholders until an OpenAI
  invocation actually ships in TASK-0006). Returns `None` rather than a
  fabricated `0` when a model isn't in the table, so a missing rate shows
  up as a gap, not a silent undercount.
- `invocations_repo.cost_by_task(conn, task_id)` — aggregates invocation
  count, total input/output tokens, and total estimated cost for one
  task. This is the per-task audit query referenced by "Token/cost
  budgets" above.
- **Re-verify the pricing table whenever a model's published price
  changes** — it is a hardcoded snapshot, not a live lookup, by design
  (see the module docstring for why). Treat a pricing-table update the
  same as any other data correction: a new commit, not a silent edit to
  history.

## How to detect token waste

Signals to look for once real invocation data exists (none of this is
automated by TASK-0003 — it's the audit checklist for whoever reviews
`agent_invocations` periodically):

- **High `retry_count` on a task** — the task was likely mis-scoped or
  under-specified, not that the model needed more attempts.
- **`input_tokens` far larger than `files_changed` would suggest** — a
  sign context wasn't scoped (§ Context-minimization rules violated),
  e.g. a Reviewer invocation that re-read the whole repo instead of the
  diff.
- **A role consistently running on a higher-cost model than its peers**
  for equivalent tasks — a candidate for the Model-selection mapping to
  reconsider.
- **`agent_invocations` rows for work that had no business calling an LLM**
  — anything matching the "must never consume an LLM call" list above
  showing up here is a bug in the invocation wrapper, not a cost tradeoff.
- **Low cache-read ratio** once prompt caching is wired up (TASK-0004) —
  per the `claude-api` skill's caching guidance, a stable system/role
  prompt that never hits cache usually means something volatile
  (timestamps, unsorted JSON, a varying tool list) is sitting ahead of the
  cache breakpoint.
