-- TASK-0003: Queue of open HUMAN_REQUIRED pauses.
-- Schema mirrors the Human Interruption Protocol
-- (docs/AUTONOMOUS_AGENT_PROTOCOL.md §8) exactly: reason, risk,
-- action_required, safe_to_pause, resume_condition.

CREATE TABLE human_required_queue (
    id                 BIGSERIAL PRIMARY KEY,
    task_id            TEXT NOT NULL REFERENCES tasks (task_id) ON DELETE CASCADE,
    reason             TEXT NOT NULL,
    risk               TEXT NOT NULL,
    action_required    TEXT NOT NULL,
    safe_to_pause      BOOLEAN NOT NULL DEFAULT true,
    resume_condition   TEXT NOT NULL,

    raised_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    notified_at        TIMESTAMPTZ,
    resolved_at        TIMESTAMPTZ,

    CONSTRAINT human_required_queue_risk_check CHECK (risk IN ('LOW', 'MEDIUM', 'HIGH'))
);

-- The resume/notify path (docs/RUNTIME_ARCHITECTURE.md §16) only ever
-- scans open (unresolved) pauses.
CREATE INDEX idx_human_required_queue_open ON human_required_queue (raised_at)
    WHERE resolved_at IS NULL;
