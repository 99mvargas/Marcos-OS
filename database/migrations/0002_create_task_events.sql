-- TASK-0003: Append-only audit trail for every task state transition.
-- docs/RUNTIME_ARCHITECTURE.md §6, §18. Enforced append-only at the
-- database level (not just convention) since this is the fine-grained
-- audit record §18 relies on.

CREATE TABLE task_events (
    id           BIGSERIAL PRIMARY KEY,
    task_id      TEXT NOT NULL REFERENCES tasks (task_id) ON DELETE CASCADE,
    at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor        TEXT NOT NULL,
    event_type   TEXT NOT NULL,
    detail       JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX idx_task_events_task_id_at ON task_events (task_id, at);

-- event_type is intentionally not CHECK-constrained to a fixed enum: new
-- event types are expected as the Orchestrator (TASK-0005) and invocation
-- contract (TASK-0004) are built out, and this table is append-only history
-- rather than a state machine that needs to reject unknown values.

CREATE OR REPLACE FUNCTION forbid_mutation() RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION '% is append-only: % is not allowed', TG_TABLE_NAME, TG_OP;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER task_events_no_update
    BEFORE UPDATE ON task_events
    FOR EACH ROW
    EXECUTE FUNCTION forbid_mutation();

CREATE TRIGGER task_events_no_delete
    BEFORE DELETE ON task_events
    FOR EACH ROW
    EXECUTE FUNCTION forbid_mutation();
