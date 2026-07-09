---
description: Bring up local Marcos OS services needed for development, per .context/current.md.
---

Use the `repo-startup` skill.

1. Read `.context/current.md` (Current Services section) instead of `HANDOFF.md` and `PROJECT_STATE.md` in full.
   - If `.context/current.md` is missing, stale relative to a known `PROJECT_STATE.md` change, or doesn't answer the question at hand, fall back to reading `HANDOFF.md` (Startup Commands section) and `PROJECT_STATE.md` (Current Infrastructure section) directly, via the `context-builder` skill's regeneration step.
2. Start only the services actually needed for the task at hand — do not start the full stack for an unrelated change.
3. Confirm each started service responds at its documented port/URL.
4. Never stop an already-running Vite, Docker, or other development server.

Report which services were started (or already running) and their reachable URLs.
