# Skill: Frontend UI

## Purpose
Implement or extend views and components in `apps/marcos-dashboard/` per an approved spec.

## Responsibilities
- Build React components consistent with the existing Tailwind + base-ui conventions.
- Maintain the current mock-data-driven pattern unless the spec explicitly approves wiring to `apps/marcos-api/`.
- Fit new UI into the existing Executive navigation structure.

## Inputs
- Approved ticket or spec
- Existing components under `apps/marcos-dashboard/`

## Outputs
- Modified or new frontend files
- A verification result from running the dev server and exercising the golden path in-browser

## Success Criteria
- `npm run build` succeeds.
- The feature is visually confirmed working, not just compiled.
- No unrelated pages/components are touched.

## Rules
- Never wire to `apps/marcos-api/` without explicit spec approval and CORS configuration.
- Never stop the Vite dev server unless explicitly instructed.
- Never introduce a new UI/styling library without approval.

## When NOT to Use
- For backend/API work — use `backend-api`.
- When the UI implies an Executive not listed in `VISION.md`.
