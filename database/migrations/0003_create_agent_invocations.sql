-- TASK-0003: One row per agent invocation attempt -- the token/cost
-- observability table required by TASK-0003's objective and the
-- idempotency/retry-accounting table from docs/RUNTIME_ARCHITECTURE.md
-- §6, §14.
--
-- invocation_id doubles as the idempotency key described in
-- docs/RUNTIME_ARCHITECTURE.md §14 ("created with a UUID idempotency_key
-- ... before the invocation starts"): the caller generates it before
-- dispatch, so a retried dispatch reuses the same id instead of creating a
-- second row.

CREATE TABLE agent_invocations (
    invocation_id       UUID PRIMARY KEY,
    task_id              TEXT NOT NULL REFERENCES tasks (task_id) ON DELETE CASCADE,
    role                 TEXT NOT NULL,
    provider             TEXT NOT NULL,
    model                TEXT,

    status               TEXT NOT NULL DEFAULT 'queued',
    retry_count          INT NOT NULL DEFAULT 0,

    -- Token/cost observability -- the minimum fields TASK-0003 requires
    -- every future AI invocation to record.
    input_tokens         INT,
    output_tokens        INT,
    total_tokens         INT,
    estimated_cost_usd   NUMERIC(12, 6),
    duration_ms          INT,

    started_at           TIMESTAMPTZ,
    completed_at         TIMESTAMPTZ,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),

    result                JSONB,
    error                 TEXT,

    CONSTRAINT agent_invocations_status_check CHECK (status IN (
        'queued', 'running', 'succeeded', 'failed', 'timed_out'
    )),
    CONSTRAINT agent_invocations_role_check CHECK (role IN (
        'Chairman', 'Architect', 'Researcher', 'Builder', 'Reviewer',
        'Tester', 'Orchestrator'
    )),
    CONSTRAINT agent_invocations_provider_check CHECK (provider IN (
        'claude-code', 'anthropic-api', 'openai'
    )),
    CONSTRAINT agent_invocations_tokens_nonneg CHECK (
        (input_tokens IS NULL OR input_tokens >= 0)
        AND (output_tokens IS NULL OR output_tokens >= 0)
        AND (total_tokens IS NULL OR total_tokens >= 0)
    ),
    CONSTRAINT agent_invocations_cost_nonneg CHECK (
        estimated_cost_usd IS NULL OR estimated_cost_usd >= 0
    ),
    CONSTRAINT agent_invocations_duration_nonneg CHECK (
        duration_ms IS NULL OR duration_ms >= 0
    ),
    CONSTRAINT agent_invocations_retry_nonneg CHECK (retry_count >= 0)
);

CREATE INDEX idx_agent_invocations_task_id ON agent_invocations (task_id);

-- Cost/token auditing by time range (docs/TOKEN_EFFICIENCY.md) and by
-- provider/model (which model is actually driving spend).
CREATE INDEX idx_agent_invocations_started_at ON agent_invocations (started_at);
CREATE INDEX idx_agent_invocations_provider_model ON agent_invocations (provider, model);

-- The lease/timeout sweep only ever needs in-flight rows.
CREATE INDEX idx_agent_invocations_in_flight ON agent_invocations (status)
    WHERE status IN ('queued', 'running');
