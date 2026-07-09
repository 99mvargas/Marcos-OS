# Skill: Backend API

## Purpose
Implement or extend API endpoints in `apps/marcos-api/` per an approved spec.

## Responsibilities
- Add or modify FastAPI routes, request/response models, and business logic exactly as specified.
- Keep storage approach (currently JSON-file-storage) unchanged unless the spec approves a new one.
- Preserve the boundary between `apps/marcos-api/` and `apps/marcos-core/`.

## Inputs
- Approved ticket or spec
- Existing files under `apps/marcos-api/`

## Outputs
- Modified or new backend files
- A verification result from a real server run and real HTTP requests

## Success Criteria
- The endpoint(s) behave exactly as specified.
- Server starts cleanly with `uvicorn` and responds correctly to the relevant requests.

## Rules
- No new database, auth, or dependency without explicit spec approval.
- No secrets embedded in code; follow `VISION.md` Security Philosophy.
- Stop and report if the endpoint requires an architectural decision (e.g. parsing/extraction method).

## When NOT to Use
- For UI work — use `frontend-ui`.
- For `apps/marcos-core/` changes not explicitly assigned.
