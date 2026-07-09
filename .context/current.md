<!-- GENERATED VIEW. Source of truth is .engineering/context.json (and the
     files it references). Do not hand-edit -- regenerate via
     `python .engineering/scripts/generate.py` instead, so this file cannot
     drift out of sync with the JSON. -->

# Current Context

## Current Sprint
020.5 -- Repository Intelligence Pipeline

## Current Task
Build .engineering/scripts/{generate.py,generate_facts.py,generate_context.py,generate_current_md.py}; split engineering state into generated facts.json and this hand-maintained decisions.json; regenerate context.json and current.md via script. Status: complete.

## Current Architecture
_Resolved from `.engineering/facts.json` (generated) and `.engineering/repository.json` (hand-maintained)._
- `apps/marcos-api/` -- backend, fastapi>=0.115, uvicorn[standard]>=0.32 (+1 more); 4 API endpoint(s) (not running (stopped after last verification))
- `apps/marcos-core/` -- legacy, no manifest found (untouched, unrelated to marcos-api)
- `apps/marcos-dashboard/` -- frontend, react, vite, tailwindcss, react-router-dom (+19 more); 8 route(s) (not confirmed running this session)
- `.claude/` -- engineering platform: 10 agents, 9 skills, 6 commands.
- Infrastructure -- Docker Compose (jellyfin, portainer).

## Current Services
_Resolved from `.engineering/repository.json`._
- Marcos Dashboard -- dev server, not confirmed running this session
- Marcos API -- :8420, not running (stopped after last verification)
- Portainer -- :9000
- Jellyfin -- :8096
- Home Assistant -- :8123 (external)

## Outstanding Decisions
_From `.engineering/context.json` -> `decisions_awaiting_approval`._
- Statement Parser real extraction approach (PDF parsing method) -- awaiting Chief Systems Architect. Full detail in `NEXT_TASK.md`.

## Next Action
Add live service-status probing (stdlib socket/HTTP, short timeout) to generate_facts.py so service up/down state becomes a generated fact instead of the hand-typed, easily-stale status strings currently in repository.json.

---
Last generated: 2026-07-08 by `generate_current_md.py`, from
`.engineering/context.json` (facts resolved via `facts.json`, architecture/
services detail via `repository.json`). Markdown docs (`PROJECT_STATE.md`,
`HANDOFF.md`, `NEXT_TASK.md`) remain authoritative for full
implementation-level detail -- this file and the JSON it's built from are
for orientation only.
