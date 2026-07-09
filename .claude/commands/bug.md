---
description: Diagnose and fix a single reported bug.
argument-hint: [bug description or reproduction steps]
---

Follow `.claude/workflows/bug-workflow.md`.

1. Read `PROJECT_STATE.md` (Known Issues) and reproduce the reported failure before changing anything.
2. Scope the fix to the affected app only (`apps/marcos-dashboard/` or `apps/marcos-api/`) — no unrelated refactor.
3. If the root cause implies an architecture change, stop and escalate rather than deciding independently.
4. Confirm the fix by rerunning the original failing scenario, not by inspection alone.
5. Stop once the reported bug is verified resolved.

Report only: files modified, root cause, verification, blocking issues.

$ARGUMENTS
