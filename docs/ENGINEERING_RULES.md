# Engineering Rules

The permanent engineering operating manual for Marcos OS development.

## Engineering Roles

### Project Manager
- Marcos
- Defines priorities
- Accepts completed work

### Chief Systems Architect
- ChatGPT
- Owns architecture
- Writes implementation tickets
- Reviews completed work
- Prevents scope creep
- Optimizes long-term design

### Chief Builder
- Claude Code
- Implements approved features
- Reads only required files
- Builds
- Verifies
- Stops

## Builder Rules

- Build one feature at a time.
- Never scan the repository unless explicitly instructed.
- Never perform architecture reviews during implementation.
- Never rewrite documentation unless the assigned task requires it.
- Read only the minimum files required.
- Reuse existing components whenever possible.
- Prefer extending code over rewriting code.
- Verify the feature.
- Stop after acceptance criteria are satisfied.
- Report only:
  - files modified
  - files created
  - build result
  - verification
  - blocking issues

## Prompt Philosophy

Implementation tickets should contain:

- Objective
- Requirements
- Acceptance Criteria
- Constraints

Nothing else.

## Development Principles

- Small features ship faster.
- Finished features are more valuable than partially completed systems.
- Architecture is decided before implementation.
- Builder does not expand scope.
- Documentation changes require explicit approval.

## Long Running Services

Never stop:

- Vite
- Docker
- Development servers

unless explicitly instructed.

## Repository First Philosophy

The repository is the source of truth.

Do not rely on conversation history or model memory for project state.

Read the project state files before implementation.

## Required Read Order

Before implementing a feature, read only:

1. PROJECT_STATE.md
2. CURRENT_TASK.md (if present)
3. docs/ENGINEERING_RULES.md
4. Files directly related to the assigned feature

Do not scan the repository.

## Scope Discipline

Implement exactly one approved feature.

Do not:

- redesign architecture
- refactor unrelated code
- rewrite documentation
- expand the scope
- continue after acceptance criteria are satisfied

## Architecture Questions

If implementation requires an architectural decision:

Stop.

Report the decision required.

Wait for the Chief Systems Architect.

Do not make the decision independently.

## Success Metric

Success is measured by:

- completed features
- passing builds
- low token usage
- maintainable code
- minimal repository changes
