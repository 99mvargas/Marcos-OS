# Workflow: Feature

## Trigger
The `/feature` command, or any approved ticket in `NEXT_TASK.md` that carries no unresolved architectural ambiguity.

## Agents
1. `product-manager` — confirms the ticket has Objective, Requirements, Acceptance Criteria, and Constraints before work starts.
2. `chief-architect` — only invoked if an architectural question arises; otherwise skipped.
3. `backend-engineer` and/or `frontend-engineer` and/or `infrastructure-engineer` and/or `finance-engineer` — implementation, delegating to `api-workflow` and/or `ui-workflow` as scope requires.
4. `qa-engineer` — verification.
5. `documentation-engineer` — updates `PROJECT_STATE.md` / `HANDOFF.md` / `NEXT_TASK.md`.
6. `git-engineer` — only if the user explicitly requests a commit.

## Inputs
- `NEXT_TASK.md`
- `PROJECT_STATE.md`
- `docs/ENGINEERING_RULES.md`
- Files directly related to the assigned feature

## Outputs
- Modified or new files implementing exactly the one approved feature
- Updated `PROJECT_STATE.md`, `HANDOFF.md`, `NEXT_TASK.md` (documentation step only)

## Stop Conditions
- Acceptance criteria are satisfied → stop, report, do not continue to unrelated work.
- The feature requires an architectural decision → stop immediately, report the decision required, wait for the Chief Systems Architect. Do not implement a workaround.
- The ticket is ambiguous or missing acceptance criteria → stop and route back to `product-manager` rather than guessing scope.

## Verification
`qa-engineer` runs the relevant build (`npm run build` and/or a real server run) and exercises the golden path for the feature directly — not a static read of the diff.
