# Next Task

This file always contains exactly one task. Read it and begin implementation
immediately — no repository scan required.

Note: Sprints 017 (Claude Engineering Platform) and 018 (Claude Automation)
are complete — see PROJECT_STATE.md and HANDOFF.md. Both were
platform-scaffolding detours and did not resolve the task below, which
remains outstanding.

## Current Task

Statement Parser — Real Extraction Spec

## Objective

Statement Parser v1 (architecture) is complete: `ParsedStatement`,
`StatementParser`, and `PlaceholderStatementParser` exist and are verified.
This task is to define — with the Chief Systems Architect — the approach for
real extraction from an uploaded statement file, before any implementation
begins.

Constraints:
- No OCR.
- No AI.
- No backend, database, or new dependencies unless the approved spec adds them.
- This is a specification/decision task, not an implementation task.

## Files Expected

- None yet. This is an architecture-question task per
  `docs/ENGINEERING_RULES.md` § Architecture Questions — stop and report the
  decision required rather than picking an extraction approach independently.

## Acceptance Criteria

- A concrete extraction approach (e.g. text-layer PDF parsing vs. structured
  format requirement) is proposed and approved before any parser code changes.
- The approved approach is captured back into this file (or a follow-up
  `NEXT_TASK.md`) as an implementation-ready ticket.

## Verification

- N/A until an approach is approved — nothing to build yet.

Stop after the decision is reported and approval is received.
