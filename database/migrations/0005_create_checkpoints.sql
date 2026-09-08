-- TASK-0003: One row per checkpoint actually written to GitHub.
-- docs/RUNTIME_ARCHITECTURE.md §6, §17. UNIQUE(commit_sha) is the
-- idempotent-recording guarantee described in §14: a retried checkpoint
-- step either produces a new commit (new row) or no-ops (no duplicate row
-- for the same commit).

CREATE TABLE checkpoints (
    id            BIGSERIAL PRIMARY KEY,
    task_id       TEXT NOT NULL REFERENCES tasks (task_id) ON DELETE CASCADE,
    branch        TEXT NOT NULL,
    commit_sha    TEXT NOT NULL,
    pushed        BOOLEAN NOT NULL DEFAULT false,
    written_at    TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT checkpoints_commit_sha_unique UNIQUE (commit_sha)
);

CREATE INDEX idx_checkpoints_task_id ON checkpoints (task_id);
