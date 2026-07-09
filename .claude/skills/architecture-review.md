# Skill: Architecture Review

## Purpose
Check a proposed spec or implementation against Marcos OS's constitutional architecture (`VISION.md`) before it is built.

## Responsibilities
- Verify Executive independence is preserved (no Executive reads another's data).
- Verify any new capability maps to an existing Shared Engine (Timeline, Recommendation, Decision, Memory, Integration Framework, Goal) or is flagged as needing a new one.
- Verify alignment with the Core Principles (decision-first, explainable recommendations, human control, no autonomous high-risk actions).

## Inputs
- The spec or ticket under review
- `VISION.md`
- `PROJECT_STATE.md`

## Outputs
- A written assessment: aligned / not aligned / needs Chief Systems Architect decision
- A list of specific principle or Executive-boundary violations, if any

## Success Criteria
- Every flagged issue cites the specific line or principle in `VISION.md` it conflicts with.
- No new architecture is invented as part of the review.

## Rules
- Only the Chief Systems Architect approves architecture changes; this skill only surfaces conflicts.
- Does not modify code.

## When NOT to Use
- During routine implementation of an already-approved spec.
- For code-quality or bug review — use `code-review` instead.
