# Skill: Feature Implementation

## Purpose
Implement exactly one approved feature end-to-end, following the Builder Rules in `docs/ENGINEERING_RULES.md`.

## Responsibilities
- Read only the minimum required files (`PROJECT_STATE.md`, `CURRENT_TASK.md` if present, `docs/ENGINEERING_RULES.md`, and files directly related to the feature).
- Implement exactly what the ticket specifies — no more.
- Reuse existing components; prefer extending code over rewriting it.
- Verify the feature works (run it, don't just read it).

## Inputs
- An approved ticket (Objective, Requirements, Acceptance Criteria, Constraints)
- `PROJECT_STATE.md`

## Outputs
- Modified or new files implementing the feature
- A verification result

## Success Criteria
- All acceptance criteria in the ticket are met.
- No unrelated files are modified.
- Build passes and the feature is verified running, not just type-checked.

## Rules
- Never scan the repository unless explicitly instructed.
- Never perform architecture reviews mid-implementation — stop and report if one is needed.
- Never continue working after acceptance criteria are satisfied.
- Report only: files modified, files created, build result, verification, blocking issues.

## When NOT to Use
- When no approved ticket exists.
- When the request requires an architecture decision — escalate instead.
