# Skill: Repo Startup

## Purpose
Bring up Marcos OS's running services for local development, using the documented startup commands in `HANDOFF.md`.

## Responsibilities
- Start `apps/marcos-dashboard/` via `npm run dev`.
- Start `apps/marcos-api/` via `uvicorn`, only if backend work is in scope.
- Bring up infrastructure containers (Portainer, Jellyfin) via `docker compose`, only if they are stopped and infrastructure work is in scope.

## Inputs
- `HANDOFF.md` Startup Commands section
- `PROJECT_STATE.md` Current Infrastructure section

## Outputs
- Running local services, confirmed reachable at their documented ports

## Success Criteria
- Each started service responds at its expected port/URL.

## Rules
- Never stop Vite, Docker, or other development servers unless explicitly instructed.
- Only start services actually needed for the current task — don't start the full stack for an unrelated change.

## When NOT to Use
- When the relevant services are already confirmed running.
- As a substitute for feature verification — starting a service is not the same as verifying a feature works.
