# HANDOFF

For tomorrow morning's development session. Read after PROJECT_STATE.md and
ENGINEERING_RULES.md.

# Current Sprint

018 — Claude Automation (see ROADMAP.md)

# Last Completed Feature

Claude Automation v1 — 6 reusable slash commands under `.claude/commands/`
(`/startup`, `/feature`, `/bug`, `/review`, `/document`, `/handoff`), each
invoking the corresponding Sprint 017 skill and pointing at the relevant
workflow. 4 workflow definitions under `.claude/workflows/`
(`feature-workflow.md`, `api-workflow.md`, `ui-workflow.md`,
`bug-workflow.md`), each specifying Trigger, Agents, Inputs, Outputs, Stop
Conditions, and Verification. No existing application code was modified.
`.claude/hooks/` and `.claude/templates/` remain empty, awaiting future
sprints.

Prior to this: Claude Engineering Platform Foundation v1 — a new `.claude/`
directory (`agents/`, `skills/`, `commands/`, `hooks/`, `templates/`,
`workflows/`) with 10 agent placeholder definitions and 8 skill placeholder
definitions, each documenting Purpose, Responsibilities, Inputs, Outputs,
Success Criteria, Rules, and When NOT to Use.

Prior to that: Marcos API Foundation v1 — a new, greenfield FastAPI backend
at `apps/marcos-api/` with four endpoints: `GET /health`,
`GET /finance/summary` (placeholder), `POST /statements` (stores uploaded
file, no parsing), `GET /statements` (lists stored filenames). No database,
auth, AI, or OCR. Verified with a real server run and real HTTP requests,
then stopped. `apps/marcos-core/` (legacy Python engine) was left completely
untouched — this is not a migration of it.

# Current Architecture

`apps/marcos-dashboard/` is a React 19 + Vite single-page app, styled with
Tailwind and base-ui components, entirely mock-data driven (no backend, no
auth, no database yet). `apps/marcos-api/` is a new, separate FastAPI backend,
JSON-file-storage only, not yet wired to the dashboard (no CORS, no client
calls). `apps/marcos-core/` is an earlier-phase Python engine, untouched and
unrelated to marcos-api. Self-hosted infrastructure runs via Docker
(Portainer, Jellyfin); Home Assistant is external and reachable but not
containerized here.

# Current Folder Structure (high level)

```
apps/marcos-dashboard/   React SPA — Home, Finance, Statement Vault
apps/marcos-api/         FastAPI backend — health, finance summary, statements
docker/                  Portainer + Jellyfin compose files
docs/                    ENGINEERING_RULES.md
specs/                   architecture & spec documents
.claude/                 Engineering platform — agents/, skills/, commands/
                         (6 slash commands), workflows/ (4 workflows),
                         hooks/ and templates/ still empty
```

# Current Running Services

- Marcos Dashboard
- Portainer
- Jellyfin
- Home Assistant

# Active Executives

- Home
- Finance Executive
- Infrastructure Executive
- Statement Vault

# Current Development Workflow

- Read PROJECT_STATE.md first
- Read ENGINEERING_RULES.md second
- Read HANDOFF.md third
- Implement ONE feature only
- Build
- Verify
- Update PROJECT_STATE.md
- Stop

# Next Feature

Statement Parser — real extraction (PDF parsing). Unchanged by Sprints 017
and 018; still awaiting the Chief Systems Architect's extraction-approach
decision.

# Acceptance Criteria

- Chief Systems Architect spec for real PDF extraction is approved before implementation.
- `PlaceholderStatementParser` is replaced or extended by a real `StatementParser`
  implementation, per approved spec — still no OCR or AI unless the spec adds them.
- Existing Statement Vault UI and mock data remain unaffected unless the spec requires a change.
- No backend, database, or new dependencies unless the spec explicitly approves them.
- `npm run build` succeeds.
- PROJECT_STATE.md updated with completed work, current task, and next action.

# Startup Commands

```
cd apps/marcos-dashboard
npm run dev

# marcos-api (FastAPI backend, not auto-started)
cd apps/marcos-api
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8420

# infrastructure (only if containers are stopped)
cd docker
docker compose -f docker-compose.portainer.yml -f docker-compose.jellyfin.yml --env-file .env up -d
```
