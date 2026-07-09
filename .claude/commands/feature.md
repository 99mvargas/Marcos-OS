---
description: Implement the one approved feature currently defined in NEXT_TASK.md.
argument-hint: [optional ticket reference or feature note]
---

Use the `feature-implementation` skill and follow `.claude/workflows/feature-workflow.md`.

1. Read `PROJECT_STATE.md`, `NEXT_TASK.md`, and `docs/ENGINEERING_RULES.md`.
2. Confirm the ticket has a clear Objective, Requirements, Acceptance Criteria, and Constraints. If it does not, stop and report what's missing rather than guessing.
3. If the feature requires an architectural decision, stop and report the decision required — do not proceed independently (per `docs/ENGINEERING_RULES.md` § Architecture Questions).
4. Route implementation through `.claude/workflows/api-workflow.md` and/or `.claude/workflows/ui-workflow.md` depending on which app(s) the ticket touches.
5. Verify the feature actually runs (build + real execution), not just type-checks.
6. Stop once acceptance criteria are satisfied. Do not expand scope.

Report only: files modified, files created, build result, verification, blocking issues.

$ARGUMENTS
