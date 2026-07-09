# Project State

Last Updated: 2026-07-03 by Claude Code

## Current Sprint
019 — Context Builder (see ROADMAP.md)

## Session Objective
- Objective: Reduce Claude token usage by replacing repeated startup document reads with one generated context file.
- Definition of Done: `.context/current.md` created with the 6 required sections; `context-builder` skill defined; `/startup` refactored to read `.context/current.md` instead of `HANDOFF.md` + `PROJECT_STATE.md`; expected token savings measured; no application code modified.

## Repository Status
- Current Branch: main
- Working Tree: dirty — untracked: apps/marcos-dashboard/, docker/, docs/ENGINEERING_RULES.md, specs/, .claude/agents/, .claude/skills/, .claude/commands/, .claude/workflows/, .context/

## Current Infrastructure
- Builder VM — host running Docker
- Docker — installed, running
- Portainer — deployed, reachable on :9000
- Jellyfin — deployed, reachable on :8096
- Home Assistant — reachable on :8123 (external, not containerized here)
- Marcos Dashboard — running, includes Infrastructure section
- Marcos API — new FastAPI backend (`apps/marcos-api/`), greenfield, not wired
  to the dashboard yet; not currently running (stopped after verification)

## Completed This Sprint
- `.context/current.md` — generated 6-section project summary (Current
  Sprint, Current Task, Current Architecture, Current Services, Outstanding
  Decisions, Next Action)
- `context-builder` skill (`.claude/skills/context-builder.md`) — defines
  how `.context/current.md` is regenerated from `PROJECT_STATE.md`,
  `HANDOFF.md`, `NEXT_TASK.md`
- `/startup` refactored to read `.context/current.md` instead of
  `HANDOFF.md` + `PROJECT_STATE.md` in full, with an explicit fallback to
  the source documents if the context file is missing or stale
- Measured expected token savings: ~74% fewer characters read per
  `/startup` invocation (7,385 → 1,921 chars; ~1,846 → ~480 tokens at a
  ~4-chars/token estimate — roughly 1,300+ tokens saved per invocation)

## Completed Previously (Sprint 018)
- 6 slash commands (`.claude/commands/`): `/startup`, `/feature`, `/bug`,
  `/review`, `/document`, `/handoff`
- 4 workflow definitions (`.claude/workflows/`): `feature-workflow.md`,
  `api-workflow.md`, `ui-workflow.md`, `bug-workflow.md`

## Completed Previously (Sprint 017)
- `.claude/` engineering platform scaffold (`agents/`, `skills/`, `commands/`,
  `hooks/`, `templates/`, `workflows/`)
- 10 agent placeholder definitions (`.claude/agents/`)
- 8 skill placeholder definitions (`.claude/skills/`)

## Completed Previously (Sprint 011)
- Infrastructure Dashboard
- ENGINEERING_RULES.md
- Portainer deployment
- Jellyfin deployment
- Service Registry v1
- Finance Executive Foundation
- Executive Navigation v1
- Statement Vault v1
- Statement Parser v1 (architecture only)
- Action Center v1
- Marcos API Foundation v1 (FastAPI: `/health`, `/finance/summary`, `POST /statements`, `GET /statements`)

## Current Task
Context Builder is complete: `.context/current.md` exists and `/startup`
reads it instead of full source docs. `.claude/hooks/` and
`.claude/templates/` remain empty, awaiting future sprints. Statement Parser
real extraction spec remains the outstanding architecture decision
(unchanged by this sprint), awaiting Chief Systems Architect.

## Decisions Awaiting Approval
- Statement Parser real extraction approach (PDF parsing method) — see NEXT_TASK.md.

## Known Issues
- Home Assistant URL currently hardcoded.
- Infrastructure Executive nav item routes to "/" (no dedicated Infrastructure page exists yet).
- StatementParser is a placeholder (`PlaceholderStatementParser`) — no real extraction logic yet.
- /finance/receipts and /development are placeholder pages with static content only.
- `apps/marcos-api/` is a greenfield backend, not yet wired to `apps/marcos-dashboard/`
  (no CORS config, no client calls). `apps/marcos-core/` remains untouched and unrelated.

## Next Action
Report the Statement Parser extraction decision required and await approval.
