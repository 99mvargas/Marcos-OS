-- TASK-0003: Runtime state store.
-- Mirrors tasks/TEMPLATE.yaml (the Autonomous Agent Protocol's task schema,
-- docs/AUTONOMOUS_AGENT_PROTOCOL.md §5) as live, contended operational
-- state. tasks/<id>.yaml on GitHub remains the durable, checkpoint-time
-- snapshot; this table is authoritative only while a task is in flight.
-- See docs/RUNTIME_ARCHITECTURE.md §5, §6.

CREATE TABLE tasks (
    task_id                TEXT PRIMARY KEY,
    objective              TEXT NOT NULL,
    status                 TEXT NOT NULL,
    assigned_agent         TEXT NOT NULL,
    next_agent             TEXT,
    priority                TEXT NOT NULL,
    requirements            JSONB NOT NULL DEFAULT '[]'::jsonb,
    architecture_reference   JSONB NOT NULL DEFAULT '[]'::jsonb,
    files_changed            JSONB NOT NULL DEFAULT '[]'::jsonb,
    tests                    JSONB NOT NULL DEFAULT '[]'::jsonb,
    blockers                 JSONB NOT NULL DEFAULT '[]'::jsonb,
    decisions                 JSONB NOT NULL DEFAULT '[]'::jsonb,
    human_required             BOOLEAN NOT NULL DEFAULT false,
    human_action                JSONB,

    -- Atomic claim/lease fields (docs/RUNTIME_ARCHITECTURE.md §6) -- what
    -- git/GitHub cannot do: a row-level lock with an expiry.
    locked_by                 TEXT,
    locked_at                  TIMESTAMPTZ,
    lease_expires_at           TIMESTAMPTZ,
    retry_count                 INT NOT NULL DEFAULT 0,

    created_at                   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                    TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT tasks_priority_check CHECK (priority IN ('P0', 'P1', 'P2', 'P3')),
    CONSTRAINT tasks_status_check CHECK (status IN (
        'PROPOSED', 'READY', 'RESEARCHING', 'ARCHITECTED', 'BUILDING',
        'TESTING', 'TEST_FAILED', 'TROUBLESHOOTING', 'REVIEWING',
        'REVIEW_FAILED', 'CHECKPOINT', 'BLOCKED', 'HUMAN_REQUIRED',
        'COMPLETED', 'CANCELLED'
    )),
    CONSTRAINT tasks_assigned_agent_check CHECK (assigned_agent IN (
        'Chairman', 'Architect', 'Researcher', 'Builder', 'Reviewer',
        'Tester', 'Orchestrator', 'Human'
    )),
    CONSTRAINT tasks_next_agent_check CHECK (next_agent IS NULL OR next_agent IN (
        'Chairman', 'Architect', 'Researcher', 'Builder', 'Reviewer',
        'Tester', 'Orchestrator', 'Human'
    )),
    CONSTRAINT tasks_retry_count_nonneg CHECK (retry_count >= 0),
    CONSTRAINT tasks_human_action_requires_flag CHECK (
        human_action IS NULL OR human_required
    )
);

-- The atomic-claim query (docs/RUNTIME_ARCHITECTURE.md §6) filters on
-- exactly this shape: unclaimed, READY, ordered by priority then age.
CREATE INDEX idx_tasks_claimable ON tasks (priority, created_at)
    WHERE status = 'READY' AND locked_by IS NULL;

CREATE INDEX idx_tasks_status ON tasks (status);

-- The lease-expiry sweep (docs/RUNTIME_ARCHITECTURE.md §8, §15) only ever
-- scans currently-locked rows.
CREATE INDEX idx_tasks_lease_expiry ON tasks (lease_expires_at)
    WHERE locked_by IS NOT NULL;

CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tasks_set_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();
