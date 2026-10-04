# AGENTS.md — Codex Operating Rules

Marcos OS manages production home infrastructure. Treat working systems,
data, connectivity, and recovery paths as valuable. Preserve existing
behavior unless a change is explicitly justified within the user's task.

## Context to consult

- `README.md`: repository purpose and intended architecture; bootstrap
  status may be outdated.
- `CLAUDE.md`: shared operating rules, safety requirements, and recovery
  expectations. Apply relevant rules to Codex as well.
- `docs/ACTIVE-WORK.md`: operational history, open issues, and previous
  verification. Later entries may supersede earlier ones.
- `agents/`: consult the relevant infrastructure, network/security,
  orchestrator, or verifier guidance. Specialist definitions are reference
  material, not authorization to execute changes or spawn agents.
- `infrastructure/`: discovery tooling and evidence. Check timestamps and
  provenance; snapshots describe observed state, not desired configuration.

Follow explicit user constraints. If applicable instructions conflict in a
way that affects safety or authorization, resolve the conflict before acting.

## Discover before changing

Prefer read-only inspection. Never assume repository documentation reflects
current live state when fresh verification is possible. If access is missing,
identify the gap rather than inventing facts or borrowing credentials.

Distinguish observations, assumptions, and verified facts. State the source,
time, and limits of evidence when they affect a decision.

“Read-only against infrastructure” does not mean a script leaves this
repository unchanged: discovery scripts write local snapshots. Inspect their
behavior before running them, especially during a read-only task.

## Infrastructure change lifecycle

For meaningful changes, follow:

DISCOVER -> BACKUP/SNAPSHOT -> PLAN -> CHANGE -> VERIFY -> HEALTH CHECK -> DOCUMENT

1. **DISCOVER:** establish current state, dependencies, scope, and risks.
2. **BACKUP/SNAPSHOT:** establish and verify an appropriate recovery point.
   Assess its impact first; creating a backup is itself an operation.
3. **PLAN:** define the bounded change, success criteria, rollback steps,
   and approval requirements.
4. **CHANGE:** execute only the authorized plan; keep changes small.
5. **VERIFY:** test the intended result against the success criteria.
6. **HEALTH CHECK:** confirm critical services, dependencies, connectivity,
   and management access still work.
7. **DOCUMENT:** record implemented behavior, verification, remaining gaps,
   and recovery instructions.

If verification or health checks fail, stop further changes, preserve
diagnostics, and recommend rollback. Execute rollback only when already
authorized or after obtaining the required approval.

## Safety and authorization

Never make destructive, network-wide, storage, firewall, DNS, VPN, Proxmox,
ZFS, Home Assistant, Docker, or credential changes without understanding
current state, dependencies, and rollback.

Require explicit user approval before high-risk execution, including data
loss, irreversible actions, broad outages, management-path changes, security
boundary changes, public exposure, and credential rotation. Approval must
cover the concrete scope and expected impact; broad intent is insufficient.

Never remove the only known management or recovery path. Verify an
alternative before changing the active path. Pause if recovery cannot be
established.

## Secrets and reproducibility

Never expose or print secrets, put them in reports or logs, or commit or
store them in Git. Use approved environment variables or secret stores;
reference credentials by purpose only. Avoid commands that dump credentials
incidentally. Redaction filters are safeguards, not guarantees.

Prefer reproducible, declarative configuration over manual changes. Where
manual work is necessary, document sanitized steps and rollback so it can
later become managed configuration.

## Repository discipline

Inspect Git state before editing. Preserve user changes; never reset,
discard, or overwrite them to obtain a clean tree.

Modify only task-related files. Keep diffs small and reviewable, avoid
unrelated formatting, and leave no task-generated clutter. Review changes
for secrets before committing.

Update documentation when implemented behavior changes. Keep historical
evidence distinct from current status; do not rewrite old snapshots to
make them appear freshly verified.

## Relationship to the Autonomous Agent Protocol

This file governs Codex specifically, the way `CLAUDE.md` governs Claude
Code. Both are superseded by `docs/AUTONOMOUS_AGENT_PROTOCOL.md` §10 (Safety
Boundaries) where the two conflict: the canonical protocol's
Infrastructure/HUMAN APPROVAL gates apply to Codex invocations exactly as
they apply to Claude Code invocations. Codex's role-scoped sandbox profile
(`apps/marcos-api/app/runtime/permissions.py`, TASK-0004) is the enforcement
mechanism for the Researcher/Builder/Tester/Reviewer tool/sandbox limits this
file describes in prose.
