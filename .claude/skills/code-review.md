# Skill: Code Review

## Purpose
Review a diff for correctness bugs and reuse/simplification/efficiency issues before it is accepted.

## Responsibilities
- Identify concrete correctness bugs (wrong output, crash, edge-case failure) with a specific failure scenario.
- Identify unnecessary duplication, complexity, or inefficiency introduced by the change.
- Rank findings by severity.

## Inputs
- The current diff or PR
- Directly related existing code for context

## Outputs
- A ranked list of findings, each with file, line, and concrete failure scenario or inefficiency

## Success Criteria
- Every finding is verified against actual code behavior, not speculation.
- No finding is reported without a concrete scenario.

## Rules
- Does not apply fixes unless explicitly asked.
- Does not expand into architecture or security review — escalate those separately.

## When NOT to Use
- For architecture-level concerns — use `architecture-review`.
- For security-specific concerns — use `security-review`.
