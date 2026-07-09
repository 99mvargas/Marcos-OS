# Skill: Security Review

## Purpose
Review pending changes against the Security Philosophy in `VISION.md` before they ship.

## Responsibilities
- Check least-privilege on every new integration or access grant.
- Check secrets stay server-side, never in client-facing code.
- Check sensitive data is encrypted in transit and at rest.
- Check no high-risk action (financial transfer, irreversible change) executes without explicit human approval.
- Check credentials are never stored directly, only via token-based, revocable access.

## Inputs
- The diff or feature under review
- `VISION.md` Security Philosophy section

## Outputs
- A list of concrete findings (file, line, failure scenario), ranked most-severe first
- A pass/fail assessment

## Success Criteria
- Every finding is concrete and reproducible, not generic advice.
- No finding is reported without a plausible failure path.

## Rules
- Does not fix findings unless explicitly asked.
- Escalates any finding that implies an architecture gap to the Chief Systems Architect.

## When NOT to Use
- For non-security-sensitive changes (e.g. copy edits, styling).
- As a substitute for `code-review` on correctness/quality issues.
