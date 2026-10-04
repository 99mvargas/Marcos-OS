# Consolidated Backlog

A single, priority-ordered view across all three tracks this repository
currently carries (`docs/DECISIONS.md#DEC-002` explains why three tracks
coexist: the Autonomous Agent Protocol track, the pre-protocol dashboard/API
sprint track, and the `apps/marcos-core` executive-engine track). Ordered by
Marcos OS's standing priority: income → business profitability → high-
interest debt → scalable systems → automation → savings/investments →
smart home → convenience → luxury. Pull the top item that isn't `Blocked`.

| # | Item | Track | Priority basis | Status |
|---|---|---|---|---|
| 1 | TASK-0006 — Architect/Chairman-assist API service + Telegram notify/resume (`docs/RUNTIME_ARCHITECTURE.md` §10) | Autonomous Agent Protocol | **Automation** — this is the literal primary mission objective: the last piece needed before Marcos stops being the message bus between Claude Code/Codex/ChatGPT. TASK-0003/0004/0005 (Postgres store, headless worker contract, Orchestrator/Verifier/Watchdog) are complete this session. | Actionable now against ephemeral Postgres, same pattern as 0003–0005. Live dispatch still needs `HUMAN_REQUIRED_QUEUE.md` #1 (start `marcos-tasks-db`). |
| 2 | Statement Parser — real extraction approach | Dashboard/API sprint track | **Scalable systems** — explicitly P0 in `TODO.md`, "unlocks Budget, Timeline, Recommendation, and Goal Engines." Highest-ROI item already on record in this repo. | **Blocked — not a repository-level decision.** `NEXT_TASK.md` and `docs/ENGINEERING_RULES.md` require the Chief Systems Architect (ChatGPT/Chairman) to pick the extraction approach before any implementation; picking it independently would be exactly the "invent architecture" failure mode `CLAUDE.md` prohibits. |
| 3 | Vaultwarden deployment | New, mission-approved project | **Security** — explicitly authorized by the mission brief, spec complete this session (`docs/VAULTWARDEN_ARCHITECTURE.md`, `docs/VAULTWARDEN_BACKUP_RECOVERY.md`). | Spec/config-as-code done. Blocked on four decisions only Marcos can make (hostname, Cloudflare Access policy membership, invite-only vs. one-time signup, physical FIDO2 key purchase) before anything is deployed. |
| 4 | TASK-0007 — first fully autonomous task, P2 or lower, run end-to-end as a validation milestone (`docs/RUNTIME_ARCHITECTURE.md` §22) | Autonomous Agent Protocol | **Automation** — proves the system in #1 actually works unattended before trusting it with anything higher-priority. | Depends on #1 and on `marcos-tasks-db` being live (or an extended ephemeral-validation pattern — same approach already used through TASK-0005). |
| 5 | Infrastructure Executive | Dashboard/API sprint track | **Convenience/smart home** — resolves a known nav bug (routes to `/`), but no revenue/debt/automation leverage. | Not started; no blockers. Lower priority than 1–4 by the standing ranking, not by complexity. |
| 6 | Budget Engine, Timeline Engine, Recommendation Engine, Goal Engine | Dashboard/API sprint track | Chained behind #2. | Blocked on #2. |
| 7 | Knowledge Executive | Dashboard/API sprint track | Medium — real data source exists (`obsidian/` vault), no architecture decision needed. | Not started; could move ahead of #6's chain if Marcos wants dashboard progress while #2 stays blocked. |
| 8 | Decision Engine, Business Executive, Purchasing Executive, Habit Engine, Health Executive, Identity Executive | Dashboard/API sprint track | P2–P3 per `TODO.md`, each chained behind something above or needs its own Chief Systems Architect decision. | Blocked / not started — unchanged from `TODO.md`. |
| 9 | Multi-provider abstraction (beyond Claude Code + Codex) | Autonomous Agent Protocol | Deferred per `DEC-008` — revisit only if TASK-0007's dry run surfaces a concrete need. | Deferred, not scheduled. |

## Standing Human-Required Items (not backlog — already blocking, see `HUMAN_REQUIRED_QUEUE.md`)

1. Approve starting the `marcos-tasks-db` Postgres container.
2. Approve a specific, scoped, low-risk real task for the first Builder-role
   (file-editing) headless dry run against this actual repository.

## Repository Consolidation — Closeout

Per the read-only classification of the second, independent `~/marcos-os`
repository (see `BUILD_STATE.md` § Repository Consolidation):

- `AGENTS.md` migrated and committed (`checkpoint/repo-consolidation-codex-guardrails-v1`).
- The Verifier "never trust the worker's own self-report" idea from Repo
  B's `agents/verifier.md` is now independently satisfied by TASK-0005's
  `apps/marcos-api/app/runtime/verifier.py` (secrets scan, unintended-
  changes check, real test execution — all run regardless of what the
  Builder claims).
- One item remains genuinely Marcos's to decide, not a repository-level
  call: whether to adopt Repo B's `.mcp.json` Home Assistant MCP server
  entry. Not done automatically.
- Once that one decision is made (either way), `~/marcos-os` has no
  remaining unique production logic and is safe to archive (not delete) —
  both its backup files are already verified intact.

## Explicitly Not Added To This Backlog

Per the mission brief's "don't get distracted" instruction: no new homelab
or convenience project was added here merely because it was discovered
during this session (e.g. Repo B's `infrastructure/discovery/` tooling, its
95KB `docs/ACTIVE-WORK.md` operational history). Both are preserved as
historical reference in Repo B, not pulled forward into active work.
