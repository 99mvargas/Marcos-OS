# Workflow: UI

## Trigger
`feature-workflow` (or `/bug`) determines the change is scoped to `apps/marcos-dashboard/`.

## Agents
1. `frontend-engineer` — implements the view(s)/component(s) per the approved spec.
2. `qa-engineer` — verifies via a running dev server and in-browser check.

## Inputs
- The approved ticket or spec
- Existing components under `apps/marcos-dashboard/`

## Outputs
- Modified or new files under `apps/marcos-dashboard/` only

## Stop Conditions
- The spec requires wiring to `apps/marcos-api/` (new CORS config, new client calls) without explicit approval → stop, report, escalate to `chief-architect`.
- The spec requires a new UI/state library outside the existing Tailwind + base-ui stack → stop and escalate.
- The feature builds and is visually confirmed working → proceed to documentation step in the parent workflow.

## Verification
Run `npm run build` to confirm it succeeds, then run the dev server and exercise the golden path and relevant edge cases in-browser. A passing build alone does not count as verification.
