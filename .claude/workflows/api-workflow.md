# Workflow: API

## Trigger
`feature-workflow` (or `/bug`) determines the change is scoped to `apps/marcos-api/`.

## Agents
1. `backend-engineer` — implements the endpoint(s)/logic per the approved spec.
2. `qa-engineer` — verifies with a real server run and real HTTP requests.

## Inputs
- The approved ticket or spec
- Existing files under `apps/marcos-api/`

## Outputs
- Modified or new files under `apps/marcos-api/` only

## Stop Conditions
- The spec requires a new database, auth mechanism, or dependency not already approved → stop, report, escalate to `chief-architect`.
- The change would touch `apps/marcos-core/` without explicit assignment → stop; that boundary is not to be crossed silently.
- The endpoint behaves as specified and is verified → proceed to documentation step in the parent workflow.

## Verification
Start the server (`uvicorn app.main:app`), issue real HTTP requests against every changed or new endpoint, and confirm responses match the spec. Stop the server afterward unless told to leave it running.
