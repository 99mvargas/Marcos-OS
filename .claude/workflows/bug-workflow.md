# Workflow: Bug

## Trigger
The `/bug` command, or a defect reported in a currently running service.

## Agents
1. `qa-engineer` — reproduces the reported failure before any code changes.
2. `backend-engineer` or `frontend-engineer` — implements the minimal root-cause fix, scoped to the affected app only, delegating to `api-workflow` or `ui-workflow` as applicable.
3. `qa-engineer` — confirms the fix by rerunning the original failing scenario.
4. `documentation-engineer` — updates `PROJECT_STATE.md` (Known Issues) only if the bug was tracked there.

## Inputs
- The bug description or reproduction steps
- The affected app's existing code
- `PROJECT_STATE.md` (Known Issues section, if relevant)

## Outputs
- A minimal fix scoped to the reported defect — no unrelated refactor or scope expansion

## Stop Conditions
- The failure cannot be reproduced → stop and report; do not guess at a fix for an unreproduced bug.
- The root cause implies an architecture change → stop, report the decision required, escalate to `chief-architect`.
- The original failing scenario no longer fails → stop, report, do not continue to unrelated cleanup.

## Verification
Rerun the exact scenario that originally reproduced the bug and confirm it now passes, plus a quick check that the fix did not break adjacent behavior in the same file/component.
