# database/

The runtime operational state store for the Autonomous Agent Protocol
(`docs/AUTONOMOUS_AGENT_PROTOCOL.md`), implemented per
`docs/RUNTIME_ARCHITECTURE.md` §5, §6 (TASK-0002) and built out in
TASK-0003. This is **not** a general-purpose Marcos OS database --
finance, capture, and statement data stay in `apps/marcos-api`'s existing
JSON-file storage; Home Assistant and Obsidian data are untouched. This
store holds exactly the five tables in `migrations/`: `tasks`,
`task_events`, `agent_invocations`, `human_required_queue`, `checkpoints`.

`tasks/*.yaml` on GitHub is unaffected and remains the durable,
checkpoint-time record (`docs/RUNTIME_ARCHITECTURE.md` §5, §7). This
database is authoritative only while a task is in flight between
checkpoints.

## Migrations

Plain, versioned, forward-only SQL files in `migrations/`, applied in
filename order by `migrate.py` -- no ORM, no migration framework. Each
file is a single, idempotent-to-track unit: `migrate.py` records which
filenames have been applied (with a checksum) in a `schema_migrations`
table it creates on first run, and refuses to re-apply or silently accept
an edited already-applied file.

To add a schema change, add a new `NNNN_description.sql` file -- never
edit a migration that has already been applied anywhere.

```bash
pip install -r database/requirements.txt   # or reuse apps/marcos-api's venv
export DATABASE_URL=postgresql://user:pass@host:5432/marcos_tasks
python3 database/migrate.py            # apply pending migrations
python3 database/migrate.py --check    # report pending migrations, apply nothing
```

## Access layer

`apps/marcos-api/app/db/` is the thin, typed Python access layer over
these tables (used by future tasks -- the headless Claude Code invocation
contract, TASK-0004, and the n8n Orchestrator, TASK-0005). It is plain
`psycopg` (v3) with hand-written SQL, not an ORM -- consistent with
`docs/RUNTIME_ARCHITECTURE.md`'s "small, no ORM framework required" scope
for this store.

## Deployment

The `marcos-tasks-db` service definition lives in
`docker/docker-compose.marcos-os.yml` (a new, isolated Postgres container
and named volume -- it does not touch `marcos-api`, `marcos-dashboard`, or
any other existing service). Per
`docs/AUTONOMOUS_AGENT_PROTOCOL.md` §10, standing up or restarting that
service is an **infrastructure change requiring human approval** -- it is
not started automatically as part of a checkpoint. See
`tasks/TASK-0003-runtime-state-store.yaml` for whether it has been
started yet.
