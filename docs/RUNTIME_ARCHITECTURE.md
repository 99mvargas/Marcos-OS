# Autonomous Agent Runtime Architecture (TASK-0002)

**Status:** Proposed — awaiting Chairman/Repository Owner review. Nothing in
this document is implemented. No orchestration, database, or n8n workflow
described here exists yet.
**Depends on:** [`AUTONOMOUS_AGENT_PROTOCOL.md`](AUTONOMOUS_AGENT_PROTOCOL.md)
v1.0 (TASK-0001), which this document assumes and extends. It does not
redefine roles, the task schema, the checkpoint procedure, or the safety
boundary matrix — those stand as designed.
**Date:** 2026-09-08

---

## 1. Current-State Assessment

Researched directly (repository + one read-only live-system check) before
writing this proposal:

- **TASK-0001 is unmerged.** `docs/AUTONOMOUS_AGENT_PROTOCOL.md`,
  `docs/AGENT_ROLES.md`, `docs/CHECKPOINTS.md`, `docs/DECISIONS.md`,
  `tasks/`, and `BUILD_STATE.md` exist only on
  `checkpoint/TASK-0001-autonomous-agent-protocol-v1`. `main` has none of
  them. This document's branch is built on top of that checkpoint branch
  (not `main`) because TASK-0002 is a direct continuation of that work —
  branching from `main` would mean writing against documentation that
  doesn't exist yet at that ref.
- **No orchestrator is wired up.** `n8n/` in this repository contains only
  `.gitkeep`. Nothing about task orchestration is versioned here.
- **A live n8n instance already exists and is unrelated to this protocol.**
  Claude Code's environment has an active n8n MCP connection. A read-only
  `search_workflows` call (no writes, no credential access) found 8
  existing workflows — `Morning COO`, `Evening Review`, `[Finance] Weekly
  Review` (active), `Business COO - Lead Intake`, `Comfort Engine`, `[Business]
  Lead Capture`, `Marcos COO Test`, `My workflow` — none registered in this
  repo, none related to `tasks/*.yaml`. This is a pre-existing, separate
  "COO" automation track running on the same n8n instance. A
  `list_credentials` call was attempted for the auth-model section of this
  proposal and was **denied by the permission classifier** ("do not touch
  n8n or credentials during this research/architecture-only phase") — that
  denial was correct and is respected; no credential data was read. This
  confirms n8n is already a live, credentialed system with production
  automations, which raises the blast radius of anything this design wires
  into it (§19).
- **No PostgreSQL exists anywhere in this repository or its Docker
  Compose files.** `database/` is an empty placeholder (`.gitkeep` only).
  `docker/docker-compose.marcos-os.yml` runs only `marcos-api` (FastAPI,
  JSON-file storage per `apps/marcos-api/data/`) and `marcos-dashboard`
  (static SPA). `docker-compose.portainer.yml` and
  `docker-compose.jellyfin.yml` are unrelated media/infra services.
- **No MCP configuration is versioned in the repository** (no `.mcp.json`
  anywhere). The n8n and Figma MCP connections available in this Claude
  Code session are configured at the operator/session level, outside the
  repo. There is no precedent in-repo for how an agent's MCP tool access
  should be scoped per role.
- **No CI/CD exists.** `.github/` is an empty placeholder.
- **`config/` is an empty placeholder** — no existing config-management
  convention to reuse or conflict with.
- **The Builder VM** (per `PROJECT_STATE.md`) is a single host running
  Docker, currently hosting Portainer, Jellyfin, and (per Compose file)
  `marcos-api`/`marcos-dashboard`. Home Assistant is reachable from it but
  runs externally. This is also, per the n8n finding above, presumably
  where the live n8n instance runs, though this was not verified further
  (out of scope for a read-only, non-infrastructure-touching research
  pass).
- **`apps/marcos-api` already has a working pattern worth reusing**:
  FastAPI + typed models + file-backed storage under `app/storage/`, with
  routes for captures/settings/financial-records. It is the natural home
  for a small HTTP surface this design needs (§16), rather than a new
  service.
- **Two parallel "state" idioms already coexist by design** (per
  `docs/DECISIONS.md#DEC-002/DEC-003` from TASK-0001):
  `.engineering/*.json` (Claude Code's own script-generated session-startup
  cache) and `tasks/*.yaml` (cross-agent handoff state). Both are
  intentionally distinct and this proposal does not merge them.

**Conclusion:** Marcos OS today has a fully specified protocol and zero
runtime. The runtime must be built essentially from nothing — this is a
greenfield infrastructure project, not a wiring exercise between mature
subsystems. That materially affects sequencing (§22) and complexity (§24).

---

## 2. Problems With the Current Protocol That Must Be Solved for Runtime Execution

The protocol (TASK-0001) is a correct and sufficient **contract**. It is not
by itself an operable system. Specific gaps:

1. **GitHub YAML has no atomic claim primitive.** Two triggers (a retried
   webhook, a scheduled poll overlapping a slow run) both reading
   `status: READY` from `tasks/TASK-0007.yaml` and both proceeding to
   dispatch a Builder is a real race with only a flat file + git as the
   substrate. Git has no row-level lock or `UPDATE ... WHERE`.
2. **GitHub polling is high-latency and rate-limited for a live
   orchestrator.** Polling `tasks/*.yaml` on a tight interval to get
   near-real-time dispatch burns API quota and adds seconds-to-minutes of
   lag per hop across a lifecycle that has ~10 hops. Fine for a document
   humans read; not fine as the thing a scheduler polls every 30 seconds.
3. **No invocation protocol for Claude Code exists.** The protocol assumes
   "Claude Code investigates / implements," but says nothing about how an
   unattended orchestrator actually starts a Claude Code process, gets a
   structured result back, and knows it finished vs. hung vs. crashed.
   Claude Code today is operated interactively (this very session). Running
   it headlessly is a distinct integration problem TASK-0001 didn't
   address because it was explicitly out of scope for that milestone.
4. **No invocation protocol for ChatGPT/Chairman exists that doesn't
   require the app open.** The protocol names ChatGPT as Chairman/Architect
   but the consumer ChatGPT app has no API by which n8n can hand it a task
   and get a plan back unattended. This is the prompt's central open
   question — addressed in §10 and §26 (open decisions).
5. **No retry/idempotency semantics.** What happens if the same dispatch
   fires twice, or an agent invocation times out mid-run? Undefined today.
6. **No lease/heartbeat/stale-claim recovery.** If a Builder invocation
   dies mid-task, nothing un-claims it. The task would sit `BUILDING`
   forever with no automatic path to `HUMAN_REQUIRED` or retry.
7. **No resume mechanism for `HUMAN_REQUIRED`.** The schema defines
   `resume_condition` as prose. Nothing defines how "the condition was met"
   becomes a machine-actionable resume trigger the Orchestrator observes.
8. **No notification channel is wired.** `human_required`/`human_action`
   are fields in a file; nothing pushes them to Marcos. Today he'd have to
   go read the repo to find out he's needed — which defeats the protocol's
   stated purpose ("Marcos is interrupted only when... genuinely required,"
   §1 of the protocol) unless the interruption can actually reach him.
9. **No least-privilege enforcement mechanism, only a stated matrix.**
   `AUTONOMOUS_AGENT_PROTOCOL.md` §10 (Safety Boundaries) and
   `AGENT_ROLES.md`'s per-role allowed/prohibited actions are currently
   *policy*, not *enforced permission*. Nothing stops a Researcher
   invocation from being handed write credentials by mistake in a future
   n8n workflow, other than the workflow author remembering not to.
10. **Ambiguity between "durable record" and "live state."** GitHub is
    correctly the engineering source of truth for the durable record
    (§7). But if it is *also* asked to be the live, contended,
    frequently-mutated operational store, those two jobs conflict —
    exactly the tension the prompt's first-principles section flags.

This proposal's central move is separating those two jobs (§3–§6): GitHub
keeps the durable-record job unchanged; a small PostgreSQL store is
introduced for the live-state job. n8n gets a defined, narrow, deterministic
role instead of an implied one. Claude Code and the Architect each get a
concrete, least-privilege invocation contract.

---

## 3. Target Architecture

```
                    ┌─────────────────────────────┐
                    │   Marcos (Repository Owner)   │
                    │  Telegram: notify / approve   │
                    └───────────────┬───────────────┘
                                    │ HUMAN_REQUIRED notify / resume
                                    ▼
┌───────────────────────────────────────────────────────────────────┐
│                          n8n (Orchestrator)                        │
│  - Scheduled poll of Postgres (task_queue view)                    │
│  - Atomic claim (UPDATE ... WHERE status=READY RETURNING)          │
│  - Dispatches to the correct agent per next_agent                  │
│  - Retry/backoff, lease timeout sweep, idempotency-key dedup       │
│  - Writes run results + events back to Postgres                    │
│  - Sends HUMAN_REQUIRED notifications, consumes resume webhooks    │
│  - Never touches git credentials, never edits application code     │
└──────┬───────────────────┬──────────────────────┬──────────────────┘
       │                   │                      │
       ▼                   ▼                      ▼
┌──────────────┐   ┌───────────────────┐   ┌──────────────────────┐
│ PostgreSQL   │   │ Claude Code        │   │ OpenAI API           │
│ (operational │   │ (headless, per-    │   │ (Architect/Chairman- │
│  state store)│   │  role invocation)  │   │  assist service)     │
│ tasks,       │   │ Researcher/Builder/│   │ drafts plans, drafts │
│ events,      │   │ Reviewer/Tester    │   │ objective/milestone  │
│ locks,       │   │ roles; git commit/ │   │ recommendations      │
│ human_queue  │   │ push non-main      │   └──────────┬────────────┘
└──────────────┘   └─────────┬──────────┘              │
                              │ checkpoint push          │ recommendation
                              ▼                          │ (Marcos approves
                    ┌──────────────────────┐             │  P0/P1 + milestone
                    │ GitHub (Marcos-OS)   │◄────────────┘  acceptance)
                    │ engineering source   │
                    │ of truth: code,      │
                    │ tasks/*.yaml         │
                    │ (checkpoint snapshot)│
                    │ BUILD_STATE.md,      │
                    │ CHANGELOG.md,        │
                    │ docs/DECISIONS.md    │
                    └──────────────────────┘
```

Everything left of GitHub is new. GitHub's role is unchanged from
TASK-0001 — it becomes the *checkpoint-time mirror* of Postgres task state,
not the thing polled for live orchestration.

---

## 4. Agent Communication Model

Agents do not talk to each other directly. Every handoff is
Orchestrator-mediated, and every handoff is a state transition in Postgres,
not a message:

1. An agent invocation (Claude Code headless call, or an OpenAI API call)
   is given: the task's current row from Postgres, the relevant repo
   context (working directory checkout for Claude Code; a rendered prompt
   with task fields for the Architect), and nothing else.
2. It returns a structured result (JSON: new `status`, `next_agent`,
   `files_changed`/`findings`/`blockers`/`decisions` as applicable,
   `human_required` block if triggered).
3. n8n validates the result shape, writes it to Postgres
   (`tasks` + an append-only `task_events` row), and — only at checkpoint
   boundaries (§17) — triggers Claude Code (as Builder) to write the
   corresponding snapshot into `tasks/<id>.yaml` and commit it.
4. No agent ever reads another agent's live output directly; it reads its
   row from Postgres, exactly as `AGENT_ROLES.md` already specifies
   ("reads the task file, not a conversation" — Postgres is now that
   file's live counterpart).

This preserves the protocol's core rule (§1: "agents communicate through
shared, structured, machine-readable state, not by Marcos relaying
messages") and extends it to be true for AI-to-AI handoffs, not just
AI-to-human ones.

---

## 5. Runtime State Model

Two tiers, deliberately not merged:

| Tier | Store | Mutation frequency | Audience | Consistency needs |
|---|---|---|---|---|
| **Live/operational** | PostgreSQL | Every sub-state transition, retries, heartbeats | n8n, agent invocations | Needs locks, transactions, indices |
| **Durable/engineering record** | GitHub (`tasks/*.yaml`, `BUILD_STATE.md`, `CHANGELOG.md`, `docs/DECISIONS.md`) | Once per checkpoint | Marcos, Chairman/Architect, future sessions, audit | Needs human legibility, permanence, git history |

A task's Postgres row is authoritative *while the task is in flight*. The
YAML file is authoritative *as the historical record* once a checkpoint
writes it — this is the same "durable, auditable unit of progress" concept
`CHECKPOINTS.md` already defines, just now with a live staging area in
front of it instead of git being asked to serve both purposes.

Reconciliation rule: `tasks/<id>.yaml` is only ever written by the Builder,
only at a checkpoint, only from that task's current Postgres row — never
hand-edited by n8n, never diverges between checkpoints (in-flight detail
stays in Postgres and in `task_events`, not in the YAML).

---

## 6. PostgreSQL Data Model Proposal

Deliberately small — five tables, no ORM framework required, plain SQL
migrations. This is *operational* state, not a general-purpose database for
Marcos OS (finance/home data stays in `apps/marcos-api`'s existing storage
until/unless a separate task migrates it).

```sql
-- One row per task, mirrors tasks/TEMPLATE.yaml's fields.
CREATE TABLE tasks (
    task_id           TEXT PRIMARY KEY,          -- 'TASK-0007-...'
    objective         TEXT NOT NULL,
    status            TEXT NOT NULL,              -- lifecycle enum, see AUTONOMOUS_AGENT_PROTOCOL.md §5
    assigned_agent    TEXT NOT NULL,
    next_agent        TEXT,
    priority          TEXT NOT NULL,
    requirements      JSONB NOT NULL DEFAULT '[]',
    architecture_reference JSONB NOT NULL DEFAULT '[]',
    files_changed     JSONB NOT NULL DEFAULT '[]',
    tests             JSONB NOT NULL DEFAULT '[]',
    blockers          JSONB NOT NULL DEFAULT '[]',
    decisions         JSONB NOT NULL DEFAULT '[]',
    human_required    BOOLEAN NOT NULL DEFAULT false,
    human_action      JSONB,
    locked_by         TEXT,                       -- invocation id currently holding the lease
    locked_at         TIMESTAMPTZ,
    lease_expires_at  TIMESTAMPTZ,
    retry_count       INT NOT NULL DEFAULT 0,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Append-only audit trail. Never updated, only inserted.
CREATE TABLE task_events (
    id          BIGSERIAL PRIMARY KEY,
    task_id     TEXT NOT NULL REFERENCES tasks(task_id),
    at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor       TEXT NOT NULL,       -- 'n8n' | 'claude-code:<role>' | 'openai:architect' | 'human:marcos'
    event_type  TEXT NOT NULL,       -- 'claimed' | 'status_changed' | 'invocation_started' |
                                     -- 'invocation_completed' | 'invocation_failed' | 'retried' |
                                     -- 'human_required_raised' | 'human_resumed' | 'checkpoint_written'
    detail      JSONB NOT NULL DEFAULT '{}'
);

-- One row per agent invocation attempt (idempotency + retry accounting).
CREATE TABLE agent_invocations (
    idempotency_key   UUID PRIMARY KEY,
    task_id           TEXT NOT NULL REFERENCES tasks(task_id),
    role              TEXT NOT NULL,        -- Researcher|Builder|Reviewer|Tester|Architect|Chairman
    provider          TEXT NOT NULL,        -- 'claude-code' | 'openai'
    status            TEXT NOT NULL,        -- queued|running|succeeded|failed|timed_out
    started_at        TIMESTAMPTZ,
    completed_at      TIMESTAMPTZ,
    result            JSONB,
    error             TEXT
);

-- Queue of open human-required pauses. Small, human-facing.
CREATE TABLE human_required_queue (
    id                BIGSERIAL PRIMARY KEY,
    task_id           TEXT NOT NULL REFERENCES tasks(task_id),
    reason            TEXT NOT NULL,        -- stable code, e.g. GOOGLE_OAUTH
    risk              TEXT NOT NULL,        -- LOW|MEDIUM|HIGH
    action_required   TEXT NOT NULL,
    resume_condition  TEXT NOT NULL,
    raised_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    notified_at       TIMESTAMPTZ,
    resolved_at       TIMESTAMPTZ
);

-- One row per checkpoint actually written to GitHub.
CREATE TABLE checkpoints (
    id                  BIGSERIAL PRIMARY KEY,
    task_id             TEXT NOT NULL REFERENCES tasks(task_id),
    branch              TEXT NOT NULL,
    commit_sha          TEXT NOT NULL,
    pushed              BOOLEAN NOT NULL DEFAULT false,
    written_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Atomic claim (the fix for problem #1 in §2):

```sql
UPDATE tasks
SET locked_by = $1, locked_at = now(), lease_expires_at = now() + interval '45 minutes'
WHERE task_id = (
    SELECT task_id FROM tasks
    WHERE status = 'READY' AND locked_by IS NULL
    ORDER BY priority, created_at
    LIMIT 1
    FOR UPDATE SKIP LOCKED
)
RETURNING *;
```

`FOR UPDATE SKIP LOCKED` gives exactly-once dispatch under concurrent
pollers without any application-level mutex — standard Postgres job-queue
pattern, no extra infrastructure.

---

## 7. GitHub Responsibility

Unchanged from TASK-0001, restated precisely so the boundary with Postgres
is unambiguous: GitHub holds **code, specifications, agent instructions,
and the checkpoint-time snapshot of task state** —
`tasks/<id>.yaml`, `BUILD_STATE.md`, `CHANGELOG.md`, `docs/DECISIONS.md`,
and the diff itself. GitHub is written to by the Builder role only, at
checkpoints, exactly as `CHECKPOINTS.md` already specifies. GitHub is
**not** polled by the Orchestrator for dispatch decisions — Postgres is.
`main` still only advances via explicitly authorized merge; nothing here
changes that.

## 8. n8n Responsibility

n8n is the **Orchestrator role** defined in `AGENT_ROLES.md` §7, now made
concrete:

- Polls `tasks` (Postgres) on a schedule (proposal: every 60–120s; cheap,
  local query, no external rate limit) for claimable rows.
- Performs the atomic claim (§6).
- Based on `next_agent`, dispatches: a headless Claude Code invocation
  (Researcher/Builder/Reviewer/Tester) or an OpenAI API call
  (Architect/Chairman-assist).
- Applies timeout + retry + exponential backoff per invocation; on
  exhausted retries, writes `human_required` and stops (§13, §15).
- Runs a separate scheduled workflow (proposal: every 5 min) that sweeps
  `tasks` for `lease_expires_at < now()` and requeues or escalates them
  (§13).
- Sends Telegram notifications when `human_required_queue` gains a row;
  consumes a resume webhook/command to clear it (§16).
- Writes every transition to `task_events`.
- **Does not**: hold a GitHub write credential capable of touching `main`,
  edit application code, make architectural or implementation decisions,
  or run destructive/infrastructure workflows without a `HUMAN_REQUIRED`
  gate — all per the existing Orchestrator prohibited-actions list, now
  enforced by simply never granting n8n those credentials (§12).
- The pre-existing "COO" workflows found in §1 are untouched by this
  design; they are a separate track on the same n8n instance and out of
  scope for TASK-0002.

## 9. Claude Code Responsibility

Unchanged roles (Researcher, Builder, Reviewer, Tester) per `AGENT_ROLES.md`.
What's new is the **invocation contract**: n8n starts a headless Claude Code
run (`claude -p "<rendered role prompt + task context>" --output-format
json`, or an equivalent Agent-SDK wrapper — see open decision in §26) on the
Builder VM, scoped to one repo checkout, with a **role-specific permission
profile**:

| Role | Tools/permissions |
|---|---|
| Researcher | Read-only: file read, `git log`/`grep`/read-only shell. No `Edit`/`Write`, no `git commit`/`push`. |
| Builder | Read/write within the repo, `Bash` for build/test, `git commit`/`push` to non-`main` branches only. |
| Tester | Read + `Bash` to run tests/start local servers. No edits. |
| Reviewer | Read-only + `Bash` for static checks/re-running tests. No edits. |

This is an enforcement of `AGENT_ROLES.md`'s existing allowed/prohibited
lists — today those are prose; a headless invocation makes it possible to
actually configure a distinct, minimal permission profile per role instead
of trusting the model to self-restrict.

## 10. ChatGPT/OpenAI Responsibility

This is the prompt's explicit open architectural question — answered here,
not assumed:

**The runtime must not depend on the ChatGPT mobile/desktop app being
open**, because the stated requirement is that the system operates while
Marcos is at work. A consumer chat app has no API surface n8n can call
unattended. Therefore:

- **Architect function → OpenAI API, fully unattended.** Producing an
  implementation plan from an approved objective is bounded, reviewable
  work (it doesn't touch `main`, doesn't spend money, doesn't run
  infrastructure). n8n calls the OpenAI API directly with a system prompt
  encoding the Architect role (`AGENT_ROLES.md` §2) and the task's
  objective + `ARCHITECTURE.md`/`VISION.md` context, gets back a plan,
  writes it to `architecture_reference`, sets `status: ARCHITECTED`. No
  human involvement required for this hop.
- **Chairman function → API-drafted, human-gated.** Objective approval
  (`PROPOSED → READY`) and milestone acceptance are the two Chairman
  actions in the lifecycle, and both are strategic/subjective by nature —
  exactly the category `VISION.md` already reserves for the human ("AI
  advises, and never acts autonomously on high-risk decisions... the human
  remains in control"). Proposal: the OpenAI API drafts a
  recommendation (approve/reject + reasoning) for every `PROPOSED` task and
  every completed checkpoint, but that recommendation lands in the
  Telegram/notification channel (§16) as a one-tap approve, not an
  autonomous transition. Marcos remains the actual Chairman; the API
  service is Chairman-*assist*, not Chairman. This mirrors the protocol's
  own existing split between "Chairman" (ChatGPT) and "Repository Owner"
  (Marcos) — it just makes the Repository Owner's involvement a 5-second
  Telegram tap instead of a relayed conversation, which satisfies "Marcos
  does not need to copy/paste conversations between AI systems" without
  removing him from decisions that are genuinely his to make.
- Both are OpenAI **API** calls (Chat Completions/Responses API), not a
  ChatGPT session — this is what makes them callable by n8n at 2pm while
  Marcos is at work.

## 11. MCP Architecture

MCP is the mechanism for giving each headless agent invocation exactly the
external tool access its role needs, nothing more:

- Each **role**, not each provider, gets its own MCP server allowlist,
  configured per-invocation (not a single shared `.mcp.json` for all
  roles). Concretely: Researcher/Tester/Reviewer get read-only MCP
  servers (filesystem read, GitHub read); Builder additionally gets a
  GitHub MCP server scoped to this repo with contents+PR write (never
  admin/merge).
- **n8n's own MCP tool access** (as observed live in this session) is a
  separate concern from the Orchestrator's Postgres-driven dispatch logic
  — it should not be handed to agent invocations by default. If a future
  task needs an agent to read n8n workflow state (e.g., a Researcher
  investigating why a COO workflow behaves a certain way), that's a
  read-only MCP grant scoped to that one invocation, not a standing grant.
- No MCP server in this design is ever granted destructive or
  infrastructure-write scope (Docker, n8n workflow write, Home Assistant
  control) without the action itself being a declared `HUMAN_REQUIRED`
  gate — matching `AUTONOMOUS_AGENT_PROTOCOL.md` §10 exactly.
- Postgres access from n8n uses n8n's native Postgres node/credential, not
  MCP — MCP is for giving *agents* (Claude Code, the Architect call) tool
  access; n8n talking to its own operational database is plain
  credentialed access, no reason to add a protocol layer.

## 12. Authentication/Authorization Model

Principle: **one credential per system per role, minimum viable scope,
none of them shared.**

| Credential | Held by | Scope | Notes |
|---|---|---|---|
| GitHub fine-grained PAT (Builder) | Claude Code headless invocation (Builder role only) | This repo only; Contents: write, Pull requests: write. No Administration, no other repos. | Branch protection on `main` (require PR + review) is the actual enforcement that agents can't merge — token scope alone can't restrict by branch, so this is a required GitHub-side control, not optional. |
| GitHub fine-grained PAT (read-only) | Researcher/Reviewer/Tester invocations | This repo, Contents: read only | Separate from the Builder token. |
| Anthropic API key / Claude Code auth | Headless Claude Code process on the Builder VM | N/A (existing Claude Code auth) | Never passed into a repo file or task YAML. |
| OpenAI API key | n8n credential store (used for Architect/Chairman-assist calls) | API-only, no org-admin scope | Rotated independently of any other key. |
| Postgres role for n8n | n8n | `SELECT`/`INSERT`/`UPDATE` on the 5 tables in §6 only; no `DROP`/`ALTER`/`CREATE` | n8n should never be able to change its own schema. |
| Telegram bot token | n8n | Bot-only, single chat (Marcos) | Already an anticipated integration per `ARCHITECTURE.md`/`VISION.md`. |
| n8n's own credential store | n8n itself | — | Access to the n8n editor/API is itself a privileged action; who besides Marcos can edit orchestrator workflows is a policy question for the Chairman (§26), not resolved here. |

All secrets live in n8n's credential store and the Builder VM's local
environment/keychain — never in the repository, never in `tasks/*.yaml`,
never in `BUILD_STATE.md`. This is a restatement of existing repo
convention (`.gitignore` already excludes `.env`), extended to the new
credentials this design introduces.

## 13. Task Lifecycle and State Transitions

Unchanged from `tasks/README.md` § Lifecycle — this design does not modify
the state machine, only makes it operable:

```
PROPOSED → READY → RESEARCHING → ARCHITECTED → BUILDING → TESTING
    → REVIEWING → CHECKPOINT → COMPLETED
```

with `TEST_FAILED → TROUBLESHOOTING → TESTING`,
`REVIEW_FAILED → BUILDING`, and `BLOCKED`/`HUMAN_REQUIRED` reachable from any
state, exactly as specified. What's added operationally:

- Every arrow above is now: n8n claims (§6) → dispatches the invocation for
  `next_agent` → receives a structured result → writes the new `status`
  to Postgres → logs a `task_events` row → re-evaluates for the next poll.
- `CHECKPOINT` triggers the 9-step procedure from `CHECKPOINTS.md`
  unchanged, executed by the Builder invocation (§9), with n8n only
  responsible for dispatching that invocation and recording the resulting
  `checkpoints` row (§6) once it reports success.

## 14. Retry/Idempotency Model

- Every dispatched invocation is created with a UUID `idempotency_key`
  (the `agent_invocations` primary key) **before** the invocation starts.
  If n8n's own workflow execution is retried (n8n's built-in retry-on-fail),
  the same key is reused; the invocation handler checks for an existing
  row with that key and returns its existing result instead of
  re-running, rather than double-executing a Builder pass.
- Task claim is idempotent by construction (§6's `SKIP LOCKED` query only
  ever returns one row per caller).
- Retries use exponential backoff (proposal: 1m, 5m, 15m) capped at 3
  attempts per invocation; the 4th failure sets `human_required` with
  reason `INVOCATION_FAILURE` rather than retrying indefinitely (this
  directly answers "retry behavior" and "duplicate task execution" from
  the prompt's security requirements).
- Checkpoint commits are naturally idempotent at the git level (a retried
  checkpoint step either produces a new, harmless commit or — if nothing
  changed — no-ops); `checkpoints` rows are keyed by `commit_sha` to avoid
  double-recording.

## 15. Failure Recovery Model

| Failure | Detection | Recovery |
|---|---|---|
| Agent invocation crashes/hangs | `lease_expires_at` sweep (§8) | Lease released, retry per §14, or `HUMAN_REQUIRED` after max retries |
| n8n itself is down/restarting | Missed poll cycles; no state corruption (Postgres holds truth) | Resumes from Postgres state on restart — no in-memory orchestration state exists to lose |
| Postgres unreachable | n8n node failure | n8n retries the connection per its own retry policy; task state simply doesn't advance (fails safe — no partial writes possible mid-outage since claim+write is one query) |
| GitHub unreachable at checkpoint time | Builder's push step fails | Task stays in `CHECKPOINT` status (not falsely marked `COMPLETED`); retried per §14 |
| OpenAI/Anthropic API outage | Invocation timeout | Retried per §14; sustained outage escalates to `HUMAN_REQUIRED` (`reason: PROVIDER_OUTAGE`) rather than looping forever |
| Partial failure mid-checkpoint (e.g., `BUILD_STATE.md` updated, push fails) | The 9-step procedure is only considered complete when all 9 succeed (`CHECKPOINTS.md`, unchanged) | Builder re-runs the checkpoint step; git/file writes are idempotent to re-run (same content in, same content out) |

The governing principle, unchanged from the protocol: **a task's status
must always reflect reality.** Nothing here allows a task to be marked
`COMPLETED` or `CHECKPOINT`-`pushed: true` unless that step actually
happened — this proposal adds machinery for detecting and recovering from
failure, not for masking it.

## 16. HUMAN_REQUIRED Mechanism

1. Any invocation may return a `human_required` block matching the schema
   in `AUTONOMOUS_AGENT_PROTOCOL.md` §8.
2. n8n writes it to `tasks.human_required`/`human_action` and inserts a
   `human_required_queue` row.
3. n8n sends a Telegram message: reason, risk, action required — nothing
   else (per the protocol's existing rule that Marcos sees only these
   three fields).
4. Resume path (new, since the protocol didn't specify one): a small
   authenticated endpoint on the existing `apps/marcos-api` — e.g.
   `POST /tasks/{id}/resume` — that Marcos hits via a Telegram bot command
   or a dashboard button (reusing the existing dashboard rather than
   building a new approval UI). This clears `human_required_queue` and
   Postgres `tasks.human_required`, and the task resumes in the state
   recorded at the point it paused (already a required field).
5. `safe_to_pause: false` cases (something left mid-operation) get a
   distinct, more urgent Telegram formatting — still just a notification,
   never an autonomous retry of a destructive action.

## 17. Checkpoint Mechanism

Unchanged 9-step procedure (`CHECKPOINTS.md`). The only addition: step 3–7
(update `BUILD_STATE.md`, update `CHANGELOG.md`, record decisions, commit,
push) are executed by the Builder invocation exactly as a human-directed
Claude Code session would do them today — n8n's only role is dispatching
that invocation and recording the resulting `checkpoints` row (§6) and
`tasks/<id>.yaml` snapshot once the Builder reports success. n8n never
constructs a commit itself.

## 18. Audit/Logging Model

Three layers, each already fit for purpose — no new logging system is
built:

1. **`task_events`** (§6) — the fine-grained, queryable operational audit
   trail. Every claim, dispatch, retry, and human interaction is a row.
2. **n8n's own execution history** — already built into n8n (confirmed
   available via `search_executions` in this session's tool set) — the
   orchestration-level log (what ran, when, success/failure), reused
   as-is rather than duplicated.
3. **Git history + `CHANGELOG.md` + `docs/DECISIONS.md`** — the permanent,
   human-legible record, unchanged from the protocol.

## 19. Security Model

Least privilege is enforced structurally, not just declared:

- No agent invocation ever receives more than one system's write
  credential (§12) — a Builder invocation can write to GitHub (non-`main`)
  but cannot touch Postgres schema, n8n workflows, or infrastructure.
- `main` is protected at the GitHub level (branch protection + required
  review), not just by policy — this closes the gap between "Claude Code
  doesn't merge to main" as a stated rule and it being actually impossible
  for an agent credential to do so.
- The Orchestrator (n8n) is the only component with visibility across the
  whole lifecycle, and it is explicitly denied the ability to make
  decisions or hold destructive credentials (§8) — this bounds the blast
  radius of an n8n compromise to "can move task state around," not "can
  merge code or touch infrastructure."
- The live n8n instance found in §1 already holds unrelated production
  credentials (Business/Finance workflow integrations). This design adds
  new, narrowly-scoped credentials to that same instance rather than
  standing up a second n8n — that's a real, accepted risk (a compromise of
  n8n affects both tracks) flagged explicitly in §26/Risks, not something
  this document can eliminate without proposing a second n8n instance,
  which would be overbuilding for a single-operator system.
- Every category in `AUTONOMOUS_AGENT_PROTOCOL.md` §10's Safety Boundaries
  table maps to a concrete enforcement point in this design: read-only/
  reversible work → role permission profiles (§9); repo changes to `main`
  → branch protection (this section); infrastructure/production/
  destructive/credentialed actions → simply never granted to any agent
  credential, full stop, so there is no "autonomous" path to them to
  restrict — they'd require a human to physically use their own separate
  credentials, which is the correct outcome for this category.

## 20. Deployment Architecture on the Builder VM

No new compute. Additions to the existing single-host Builder VM:

- **Postgres**: one new container (`docker-compose.marcos-os.yml` gains a
  `marcos-tasks-db` service + named volume) *or* a schema/database inside
  an existing Postgres instance if one is later found to already run on
  the VM (not confirmed in this research pass — a Researcher task should
  check before TASK-0003 provisions a redundant instance).
- **n8n**: already running; this design adds workflows and credentials to
  it, not a new instance (see risk accepted in §19).
- **Claude Code headless invocations**: run as local processes on the
  Builder VM (same host, same repo checkout n8n or a wrapper script
  triggers) — no new host needed.
- **`apps/marcos-api`**: gains one small route module (`/tasks/{id}/resume`,
  §16) — reuses the existing FastAPI service and its container rather than
  standing up a new one.

None of this is implemented by TASK-0002. It is scoped here so the
Chairman can size the next infrastructure-touching task (§22) accurately.

## 21. Network/Service Dependencies

All new outbound-only from the Builder VM, no new inbound ports required:

- n8n → Postgres (localhost/internal Docker network)
- n8n → GitHub API (HTTPS, outbound)
- n8n → Anthropic (for triggering/monitoring Claude Code, if done via API
  rather than local process — see open decision §26) / local process exec
- n8n → OpenAI API (HTTPS, outbound)
- n8n → Telegram Bot API (HTTPS, outbound)
- Claude Code (Builder) → GitHub (git push, HTTPS, outbound — already
  true today)
- `apps/marcos-api` → Postgres (for the resume endpoint, §16) — new
  internal dependency for a service that's currently JSON-file-only;
  scoped narrowly to the `tasks`/`human_required_queue` tables via a
  read/limited-write credential, not general database access.

No existing network boundary changes; nothing here requires exposing a new
port externally.

## 22. Recommended Implementation Sequence

Each of the following is a **separate future task**, not part of
TASK-0002, and each should get its own Chairman approval before starting
(per the protocol's own `PROPOSED → READY` gate):

1. **TASK-0003 — Operational data store.** Provision Postgres (verify
   first whether one already exists on the Builder VM), create the §6
   schema, write a one-time importer for the existing
   `tasks/TASK-0001-*.yaml` file so Postgres and GitHub agree from day one.
2. **TASK-0004 — Headless Claude Code invocation contract.** Build and
   test the `claude -p` (or Agent-SDK) wrapper with the four role
   permission profiles (§9), exercised manually first (no n8n yet) against
   one real, low-risk task.
3. **TASK-0005 — n8n Orchestrator v1.** The poll/claim/dispatch/retry
   workflow from §8, wired to TASK-0003's Postgres and TASK-0004's
   invocation contract, dry-run on a single P3 task end-to-end.
4. **TASK-0006 — Architect/Chairman-assist API service + Telegram
   notify/resume.** §10 and §16, wired to the same task.
5. **TASK-0007 — First fully autonomous task**, P2 or lower, run through
   the complete lifecycle unattended except for the Chairman-assist
   Telegram approval taps, as a validation milestone before trusting the
   system with anything higher-priority.
6. **(Deferred, not scheduled)** Multi-provider abstraction (§26) — only
   if TASK-0007's results justify it.

## 23. Explicitly Rejected Alternatives and Why

- **Kubernetes / container orchestration platform.** A single-operator
  personal system with one host does not need a scheduler for schedulers;
  this would add an entire ops discipline (manifests, cluster
  lifecycle, networking) with no corresponding reliability or scale
  requirement. Rejected as overbuilding.
- **A general agent framework (LangGraph, CrewAI, AutoGPT-style loops).**
  These reimplement exactly what n8n (deterministic control flow) + Claude
  Code (reasoning/tool use) already do combined, add a new dependency and
  learning curve, and — critically — replace the deterministic,
  auditable state machine the protocol deliberately specifies with a
  framework-owned agent loop that's harder to constrain to the
  role-permission model in §9. Rejected: worse fit, not just redundant.
- **GitHub Issues/Actions as the live orchestrator**, instead of a
  separate Postgres store. Actions runners can't reach the Builder VM's
  local services (Postgres, Home Assistant, a self-hosted Claude Code
  process) without exposing them to the internet, which trades a
  contained blast radius for a public one. GitHub API rate limits and
  latency also make a tight poll loop impractical (§2, problem #2).
  Rejected on both security and latency grounds.
- **GitHub `tasks/*.yaml` files as the live claim/lock mechanism** (e.g.,
  claiming via a commit race). Git has no atomic "claim if unclaimed"
  primitive; this was the exact problem in §2 that motivated Postgres.
  Rejected.
- **Giving n8n a GitHub credential capable of merging to `main`,** to
  simplify the checkpoint flow. Directly violates
  `AUTONOMOUS_AGENT_PROTOCOL.md` §7 and §10 (`main` is explicitly
  HUMAN APPROVAL). Rejected outright, not a close call.
- **Synchronous ChatGPT-app-in-the-loop for every transition** (the
  prompt's explicit question). Fails the stated requirement that the
  system operate while Marcos is at work. Rejected in favor of the
  API-backed Architect + Chairman-assist model (§10).
- **Fully autonomous Chairman** (no human approval for objectives/
  milestones at all). Contradicts `VISION.md`'s standing principle that
  the human remains in control of decisions with real consequence, and
  the protocol's own separation of Chairman (ChatGPT) from Repository
  Owner (Marcos). Rejected in favor of Chairman-*assist* (§10).
- **A second, dedicated n8n instance** to isolate this protocol's
  credentials from the existing "COO" workflows found in §1. Considered
  and not recommended for v1 — doubles operational surface (two things to
  patch/monitor/host) for a risk (§19) that narrow credential scoping
  already mitigates significantly; flagged as a candidate to revisit if
  TASK-0007's dry run surfaces a concrete conflict with the COO workflows.

## 24. Estimated Complexity

**Low-to-moderate**, concentrated almost entirely in TASK-0004 (the
headless Claude Code invocation contract) and TASK-0005 (the n8n
orchestrator workflow), because everything else reuses existing
infrastructure:

- Postgres schema: small (5 tables), no ORM, plain SQL — low complexity.
- n8n workflow: a handful of nodes (schedule trigger → Postgres query →
  switch on `next_agent` → HTTP/Execute-Command node → Postgres write) —
  moderate complexity, mostly in getting retry/backoff/lease-sweep right.
- Headless Claude Code invocation: the least precedented piece — no
  existing pattern in this repo for non-interactive Claude Code with
  per-role permission scoping; this is genuine new integration work, not
  configuration of something that already exists elsewhere in the repo.
- OpenAI API Architect/Chairman-assist calls: low complexity — a
  well-understood API call pattern.
- Telegram notify/resume + one FastAPI route: low complexity, follows
  `apps/marcos-api`'s existing route conventions.

Overall: this is a real, multi-task engineering project (roughly the 5
tasks in §22), not a single afternoon of wiring — but nothing in it
requires new technology unfamiliar to the stack already in use
(Postgres, FastAPI, n8n, Claude Code).

## 25. Expected Operating Cost

- **Infrastructure marginal cost ≈ $0/month.** Postgres and n8n both run
  self-hosted on the already-owned Builder VM; no new hosted service is
  introduced.
- **Telegram Bot API: free.**
- **LLM API usage is the actual variable cost**, driven by task volume,
  not by this architecture. At a single-operator pace (a handful of tasks
  per week, each involving a few Claude Code role invocations and a couple
  of small OpenAI Architect/Chairman-assist calls), this is plausibly
  low tens of dollars/month — the same order of magnitude as Marcos's
  existing interactive Claude Code usage, since headless invocations
  replace, rather than add to, the manual sessions this protocol exists to
  reduce.
- No component in this design bills per-request beyond LLM API metering
  (n8n, Postgres, Telegram are all free at this scale).

## 26. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Race condition double-dispatches a task | `FOR UPDATE SKIP LOCKED` atomic claim (§6) |
| Stuck/crashed invocation deadlocks a task forever | Lease expiry + sweep (§8, §15) |
| Retry loop runs up API cost or spins forever on a bad task | Capped retries + backoff → `HUMAN_REQUIRED` (§14) |
| A future workflow author accidentally grants an agent invocation excess credentials | Role-scoped credential table is documented (§12) as the checklist to enforce at build time; branch protection on `main` is a second, independent backstop that doesn't depend on remembering the checklist |
| n8n compromise affects both this protocol and the existing unrelated "COO" workflows (§1, §19, §23) | Narrow, single-purpose credentials added for this protocol; accepted risk for v1, revisit a second instance if TASK-0007 surfaces a real conflict |
| Secrets leak into a committed file | Unchanged existing convention (`.gitignore`, no secrets in `tasks/*.yaml`/`BUILD_STATE.md`) extended to new credentials; nothing in this design writes a credential to a repo path |
| Postgres becomes a second, drifting source of truth despite §5's reconciliation rule | Rule is structural, not just documented: only the Builder-at-checkpoint writes YAML, and it always writes from the current Postgres row — no other write path to `tasks/*.yaml` exists in this design |
| Headless Claude Code invocation is a genuinely new integration with no in-repo precedent (§24) | Sequenced as its own task (TASK-0004) with a manual, no-orchestrator dry run before n8n is wired to it, so failure modes are found in isolation |
| Chairman-assist (API) drifts toward de facto autonomous approval if Marcos routinely rubber-stamps its Telegram taps | Explicitly a process/usage risk, not a technical one — flagged here so the Chairman can decide whether milestone-acceptance taps need periodic real review; not solvable in software |

---

## Relationship to Existing Documentation

Additive, consistent with `AUTONOMOUS_AGENT_PROTOCOL.md` §12's own rule for
itself: this document does not redefine roles, the task schema, the
checkpoint procedure, the git workflow, or the safety-boundary matrix. It
answers exactly the question TASK-0001 explicitly deferred: `§9. Autonomous
Operation (Future)` of that document said orchestration "is not implemented
by this milestone." This document is that follow-on design. No existing
file is deleted or contradicted; where this document narrows an
ambiguity left open by TASK-0001 (the Chairman/Architect invocation model,
§10), that narrowing is presented as a proposal for Chairman approval, not
a unilateral change to the adopted protocol.
